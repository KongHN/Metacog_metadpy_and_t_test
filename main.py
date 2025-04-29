import os
import pandas as pd
import numpy as np
from metadpy.utils import discreteRatings, trials2counts
from metadpy.mle import metad
from tqdm import tqdm


def calculate_metrics(file_path, rating_type, n_ratings=None):
    # 读取 CSV 文件
    data = pd.read_csv(file_path)

    # 保存原始列名
    original_columns = data.columns

    # 修改列名
    data = data.rename(columns={'Stimulus': 'Stimuli', 'Response': 'Responses'})

    # 初始化结果列表
    results = []

    # 关键词列表
    block_keywords = ['block', 'blocks', 'Block', 'Blocks', 'BlockNumber', 'Block_count',
                      'Int.Block', 'block_type', 'BlockID', 'Block_Type', 'NumBlock', 'blocki']
    # 筛选出包含关键词的列
    block_columns = [col for col in data.columns if any(keyword in col for keyword in block_keywords)]

    # 按 Subj_idx 分组
    subj_groups = data.groupby('Subj_idx')
    for subj_idx, group in tqdm(subj_groups, desc="Processing subjects", unit="subject"):
        if rating_type == 1:  # 连续数据
            if n_ratings is None:
                raise ValueError("对于连续数据，需要提供 n_ratings。")
            # 假设数据列名为 'Stimuli', 'Accuracy', 'Confidence'
            nR_S1, nR_S2 = trials2counts(
                data=group,
                stimuli='Stimuli',
                accuracy='Accuracy',
                confidence='Confidence',
                nRatings=n_ratings
            )
        elif rating_type == 2:  # 离散数据
            if n_ratings is None:
                raise ValueError("对于离散数据，需要提供 n_ratings。")
            # 假设数据列名为 'Stimuli', 'Accuracy', 'Confidence'
            nR_S1, nR_S2 = trials2counts(
                data=group,
                stimuli='Stimuli',
                accuracy='Accuracy',
                confidence='Confidence',
                nRatings=n_ratings
            )
        else:
            raise ValueError("无效的评分类型。请输入 1 表示连续数据，2 表示离散数据。")

        try:
            # 计算 D prime 使用 mle 功能
            fit = metad(
                data=group,
                nRatings=n_ratings,
                stimuli='Stimuli',
                accuracy='Accuracy',
                confidence='Confidence',
                verbose=0
            )
            d_prime = fit['dprime'][0]
            meta_d = fit['meta_d'][0]
            m_ratio = fit['m_ratio'][0]
            m_diff = fit['m_diff'][0]  # 新增：获取 m_diff 的值
        except ZeroDivisionError:
            d_prime = np.nan
            meta_d = np.nan
            m_ratio = np.nan
            m_diff = np.nan

        # 统计包含关键词列中不同值的个数
        if block_columns:
            unique_block_values = pd.unique(group[block_columns].values.ravel())
            block_count = len(unique_block_values)
        else:
            block_count = None

        # 统计每个 Subj_idx 的数据行数
        trails_count = len(group)

        # 添加结果到列表
        results.append({
            'Subj_idx': subj_idx,
            'D prime': d_prime,
            'dprime_metadpy': d_prime,
            'meta d’': meta_d,
            'm ratio': m_ratio,
            'm diff': m_diff,  # 新增：添加 m_diff 到结果字典
            'Block': block_count,
            'Trails': trails_count
        })

    # 创建结果 DataFrame
    result_df = pd.DataFrame(results)

    # 添加 Part 列
    file_name = os.path.basename(file_path)
    if 'part1' in file_name:
        result_df['Part'] = 'first'
    elif 'part2' in file_name:
        result_df['Part'] = 'second'
    else:
        result_df['Part'] = None

    # 提取 data_ 后面、_part 前面的部分
    try:
        start_index = file_name.index('data_') + len('data_')
        end_index = file_name.index('_part')
        name = file_name[start_index:end_index]
    except ValueError:
        name = None

    # 添加 Name 列
    result_df['Name'] = name

    # 还原原始列名
    data.columns = original_columns

    return result_df


# 这里直接指定 CSV 文件的目录
csv_file_directory = r'F:\科研\02Metacog-617\data test\test\data separation'  # 请根据实际情况修改为正确的目录
csv_file_name = input("请输入本地 CSV 文件的名字：")
file_path = os.path.join(csv_file_directory, csv_file_name)

rating_type = int(input("请输入评分类型（1 表示连续数据，2 表示离散数据）："))
if rating_type in [1, 2]:
    n_ratings = int(input("请输入评分的点数："))
else:
    raise ValueError("无效的评分类型。请输入 1 表示连续数据，2 表示离散数据。")

# 计算指标
result_df = calculate_metrics(file_path, rating_type, n_ratings)

# 这里直接指定 Excel 文件的地址
xlsx_file_path = r'F:\科研\02Metacog-617\data test\Database_Information.xlsx'  # 请根据实际情况修改为正确的文件路径
xlsx_df = pd.read_excel(xlsx_file_path)

# 进行匹配
merged_df = pd.merge(result_df, xlsx_df[['Name_in_database', 'Category']],
                     left_on='Name', right_on='Name_in_database', how='left')

# 删除多余的列
merged_df = merged_df.drop(columns=['Name_in_database'])

# 调整列顺序
column_order = ['Category', 'Name', 'Subj_idx', 'D prime', 'meta d’', 'm ratio', 'm diff', 'Block', 'Trails', 'Part']
merged_df = merged_df[column_order]

# 提取 data_ 后面的部分作为输出文件名，并在前面加上 meta_
file_name = os.path.basename(file_path)
try:
    start_index = file_name.index('data_') + len('data_')
    output_name = 'meta_' + file_name[start_index:]
    if not output_name.endswith('.csv'):
        output_name += '.csv'
except ValueError:
    output_name = 'meta_output.csv'

# 获取读取文件的上两级目录
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(file_path)))
# 创建 Result of meta 文件夹
result_dir = os.path.join(parent_dir, 'Result of meta')
if not os.path.exists(result_dir):
    os.makedirs(result_dir)

# 保存结果到指定路径
with tqdm(total=1, desc="Saving results", unit="step") as pbar:
    output_path = os.path.join(result_dir, output_name)
    merged_df.to_csv(output_path, index=False)
    pbar.update(1)

print("结果已保存到：", output_path)