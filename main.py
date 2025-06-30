import os
import pandas as pd
import numpy as np
from metadpy.mle import metad
from metadpy.utils import discreteRatings
from alive_progress import alive_bar

# 固定的csv文件目录
csv_dir = r"F:\科研\02Metacog\data test\test\data separation"
# 固定的xlsx文件路径
xlsx_path = r"F:\科研\02Metacog\data test\Database_Information.xlsx"

# 准确率相关列名列表
accuracy_cols = ['ErrorDirection', 'Accuracy', 'ErrorDirectionJudgment', 'accuracy']


def calculate_metrics(csv_filename, data_type, nrating):
    # 完整的csv文件路径
    csv_path = os.path.join(csv_dir, csv_filename)
    # 读取csv文件
    df = pd.read_csv(csv_path)

    # 替换列名
    original_stimuli_col = None
    original_responses_col = None
    for col in df.columns:
        if 'Stimulus' in col:
            original_stimuli_col = col
            df.rename(columns={col: 'Stimuli'}, inplace=True)
        if 'Response' in col:
            original_responses_col = col
            df.rename(columns={col: 'Responses'}, inplace=True)

    # 检查是否存在准确率相关列
    accuracy_col = next((col for col in accuracy_cols if col in df.columns), None)

    if accuracy_col:
        df['Accuracy'] = df[accuracy_col]

        # 检查准确率列的值是否为0/1或布尔型
        unique_vals = df['Accuracy'].dropna().unique()
        valid_accuracy = all(val in [0, 1, True, False] for val in unique_vals)

        if not valid_accuracy:
            print(f"警告: 列 '{accuracy_col}' 包含非布尔/0-1值，尝试转换为0-1")
            # 尝试将常见的正确/错误表示转换为0-1
            df['Accuracy'] = df['Accuracy'].map({
                'correct': 1, 'incorrect': 0,
                'right': 1, 'wrong': 0,
                'True': 1, 'False': 0,
                True: 1, False: 0
            }).fillna(df['Accuracy'])
    else:
        # 计算Accuracy
        if 'Stimuli' not in df.columns or 'Responses' not in df.columns:
            raise ValueError("数据中既没有准确率相关列，也没有Stimuli和Responses列")
        df['Accuracy'] = (df['Stimuli'] == df['Responses']).astype(int)

    # 按Subj_idx分组
    grouped = df.groupby('Subj_idx')
    total_subjects = len(grouped)
    results = []

    # 创建进度条
    with alive_bar(total_subjects, title=f'处理 {csv_filename}') as bar:
        for subj_idx, group in grouped:
            # 统计Blocks
            block_cols = ['block', 'blocks', 'Block', 'Blocks', 'BlockNumber', 'Block_count',
                          'Int.Block', 'block_type', 'BlockID', 'Block_Type', 'NumBlock', 'blocki']
            block_col = next((col for col in block_cols if col in group.columns), None)
            if block_col:
                block_count = group[block_col].nunique()
            else:
                block_count = 0

            # 统计总Trials，根据相同Subj_idx的行数计算
            trial_count = len(group)

            # 数据验证
            valid_data = True
            # 检查刺激类型是否足够
            stim_counts = group['Stimuli'].value_counts()
            if len(stim_counts) < 2:
                print(f"警告: Subj_idx {subj_idx} 的刺激类型不足，无法计算d'")
                valid_data = False

            # 检查准确率是否为0或1（会导致d'为无穷）
            accuracy = group['Accuracy'].mean()
            if np.isclose(accuracy, 0) or np.isclose(accuracy, 1):
                print(f"警告: Subj_idx {subj_idx} 的准确率为{accuracy:.2f}，无法计算d'")
                valid_data = False

            if not valid_data:
                results.append({
                    'Subj_idx': subj_idx,
                    'dprime': np.nan,
                    'meta_d': np.nan,
                    'm_ratio': np.nan,
                    'm_diff': np.nan,
                    'Block': block_count,
                    'Trials': trial_count,
                    'Error': '数据不足或分布不合理'
                })
                bar()  # 更新进度条
                continue

            try:
                if data_type == 1:  # 连续数据
                    responseConf, _ = discreteRatings(group['Confidence'], nbins=nrating)
                    group['Confidence'] = responseConf
                elif data_type == 2:  # 离散数据
                    pass

                fit = metad(
                    data=group,
                    nRatings=nrating,
                    stimuli='Stimuli',
                    accuracy='Accuracy',
                    confidence='Confidence'
                )

                dprime = fit['dprime'].values[0]
                meta_d = fit['meta_d'].values[0]
                m_ratio = fit['m_ratio'].values[0]
                m_diff = fit['m_diff'].values[0]

                # 检查d'是否为零
                if np.isclose(dprime, 0):
                    print(f"警告: Subj_idx {subj_idx} 的d'值为零，无法计算m-ratio和m-diff")
                    m_ratio = np.nan
                    m_diff = np.nan

                results.append({
                    'Subj_idx': subj_idx,
                    'dprime': dprime,
                    'meta_d': meta_d,
                    'm_ratio': m_ratio,
                    'm_diff': m_diff,
                    'Block': block_count,
                    'Trials': trial_count,
                    'Error': None
                })
            except ZeroDivisionError as e:
                print(f"错误: Subj_idx {subj_idx} 发生除以零错误: {str(e)}")
                results.append({
                    'Subj_idx': subj_idx,
                    'dprime': np.nan,
                    'meta_d': np.nan,
                    'm_ratio': np.nan,
                    'm_diff': np.nan,
                    'Block': block_count,
                    'Trials': trial_count,
                    'Error': '除以零错误'
                })
            except Exception as e:
                print(f"错误: Subj_idx {subj_idx} 发生未知错误: {str(e)}")
                results.append({
                    'Subj_idx': subj_idx,
                    'dprime': np.nan,
                    'meta_d': np.nan,
                    'm_ratio': np.nan,
                    'm_diff': np.nan,
                    'Block': block_count,
                    'Trials': trial_count,
                    'Error': str(e)
                })

            bar()  # 更新进度条

    result_df = pd.DataFrame(results)

    # 恢复列名
    if original_stimuli_col:
        df.rename(columns={'Stimuli': original_stimuli_col}, inplace=True)
    if original_responses_col:
        df.rename(columns={'Responses': original_responses_col}, inplace=True)

    return result_df


def save_results(result_df, csv_filename):
    # 创建新文件夹
    parent_dir = os.path.dirname(csv_dir)
    new_folder = os.path.join(parent_dir, 'meta_data_result')

    # 调试：检查目录是否存在和可写
    os.makedirs(new_folder, exist_ok=True)

    # 调试：检查目录权限
    if not os.access(new_folder, os.W_OK):
        print(f"错误: 目录 {new_folder} 不可写")
        return

    # 生成新的csv文件名
    new_csv_name = 'meta_' + csv_filename.split('data_')[1]
    new_csv_path = os.path.join(new_folder, new_csv_name)


    # 读取xlsx文件
    xlsx_df = pd.read_excel(xlsx_path)

    # 提取csv文件名中data_后面以及_part前面的部分
    exp_name = csv_filename.split('data_')[1].split('_part')[0]

    # 匹配xlsx文件中的Name_in_database
    match_row = xlsx_df[xlsx_df['Name_in_database'] == exp_name]
    if not match_row.empty:
        result_df['Category'] = match_row['Category'].values[0]
        result_df['Exp_Name'] = match_row['Name_in_database'].values[0]
        # 确保Difficulty列的数据类型为object，避免类型不匹配问题
        result_df['Difficulty'] = match_row['Difficulty'].astype(object).values[0]
    else:
        # 如果没有找到匹配项，填写Exp_Name中最后一个_后面的内容
        category = exp_name.split('_')[-1] if '_' in exp_name else exp_name
        result_df['Category'] = category
        result_df['Exp_Name'] = exp_name
        # 设置Difficulty为NaN，并指定数据类型为object
        result_df['Difficulty'] = pd.Series([np.nan], dtype=object)

    # 记录part后面的部分
    part_match = None
    if '_part' in csv_filename:
        part_str = csv_filename.split('_part')[1].split('.csv')[0]
        if part_str:
            part_match = part_str
    result_df['Part'] = part_match

    # 确保Difficulty列的数据类型为object
    result_df['Difficulty'] = result_df['Difficulty'].astype(object)

    # 当Difficulty为空时，根据Exp_Name中最后一个_前面的内容去匹配xlsx的Name_in_database
    if result_df['Difficulty'].isna().any():
        # 创建一个从Name_in_database到Difficulty的映射
        difficulty_map = dict(zip(xlsx_df['Name_in_database'], xlsx_df['Difficulty']))

        # 创建一个从Name_in_database到Category的映射，用于后续可能的更新
        category_map = dict(zip(xlsx_df['Name_in_database'], xlsx_df['Category']))

        # 遍历结果中的每一行
        for idx, row in result_df.iterrows():
            if pd.isna(row['Difficulty']):
                exp_name = row['Exp_Name']
                # 获取最后一个_前面的内容
                if '_' in exp_name:
                    base_exp_name = exp_name.rsplit('_', 1)[0]
                    if base_exp_name in difficulty_map and not pd.isna(difficulty_map[base_exp_name]):
                        # 直接赋值，因为Difficulty列已经是object类型
                        result_df.at[idx, 'Difficulty'] = difficulty_map[base_exp_name]
                        # 同时更新Category（如果需要）
                        if pd.isna(row['Category']) and base_exp_name in category_map:
                            result_df.at[idx, 'Category'] = category_map[base_exp_name]

    # 整理输出csv文件的列顺序
    result_df = result_df[
        ['Category', 'Exp_Name', 'Subj_idx', 'dprime', 'meta_d', 'm_ratio', 'm_diff', 'Block', 'Trials', 'Difficulty',
         'Part', 'Error']]

    # 保存结果到新的csv文件
    try:
        result_df.to_csv(new_csv_path, index=False)
        print(f"成功保存文件: {new_csv_path}")
    except PermissionError as e:
        print(f"错误: 无法保存文件 {new_csv_path} - 权限被拒绝")
        print(f"请确保文件没有被其他程序打开，并且目录可写")
        print(f"详细错误: {e}")
    except Exception as e:
        print(f"错误: 保存文件时发生未知错误: {e}")


if __name__ == "__main__":
    csv_filename = input("请输入csv文件名: ")
    data_type = int(input("请输入数据类型（1: 连续数据，2: 离散数据）: "))
    nrating = int(input("请输入nrating的n值: "))

    result_df = calculate_metrics(csv_filename, data_type, nrating)
    save_results(result_df, csv_filename)