# 加载必要的包
library(ggplot2)

# 读取 CSV 文件
file_path <- "F:\\科研\\02Metacog-617\\data test\\test\\final data\\0meta_data.csv"
data <- read.csv(file_path)

# 按 Exp_Name 分组
exp_names <- unique(data$Exp_Name)

# 存储每个 Exp_Name 的 m_ratio t 检验结果
results_ratio <- data.frame(Exp_Name = character(),
                            t_value = numeric(),
                            p_value = numeric(),
                            stringsAsFactors = FALSE)
# 存储每个 Exp_Name 的 m_diff t 检验结果
results_diff <- data.frame(Exp_Name = character(),
                           t_value = numeric(),
                           p_value = numeric(),
                           stringsAsFactors = FALSE)

# 存储总的 m_ratio 数据
total_first_data_ratio <- numeric()
total_second_data_ratio <- numeric()
# 存储总的 m_diff 数据
total_first_data_diff <- numeric()
total_second_data_diff <- numeric()

# 对每个 Exp_Name 进行配对 t 检验
for (exp_name in exp_names) {
  # 筛选出当前 Exp_Name 的数据
  subset_data <- data[data$Exp_Name == exp_name, ]
  
  # 找出 m_ratio 为空值的 Subj_idx
  na_subj_idx_ratio <- unique(subset_data$Subj_idx[is.na(subset_data$m_ratio)])
  # 找出 m_diff 为空值的 Subj_idx
  na_subj_idx_diff <- unique(subset_data$Subj_idx[is.na(subset_data$m_diff)])
  
  # 排除 m_ratio 和 m_diff 为空值对应 Subj_idx 的数据
  clean_data <- subset_data[!subset_data$Subj_idx %in% c(na_subj_idx_ratio, na_subj_idx_diff), ]
  
  # 筛选出在 first 和 second 部分都存在的 Subj_idx
  first_subj <- unique(clean_data$Subj_idx[clean_data$Part == "first"])
  second_subj <- unique(clean_data$Subj_idx[clean_data$Part == "second"])
  common_subj <- intersect(first_subj, second_subj)
  
  # 仅保留在 first 和 second 部分都存在的 Subj_idx 对应的数据
  clean_data <- clean_data[clean_data$Subj_idx %in% common_subj, ]
  
  # 提取 first 和 second 部分的 m_ratio 数据
  first_data_ratio <- clean_data[clean_data$Part == "first", "m_ratio"]
  second_data_ratio <- clean_data[clean_data$Part == "second", "m_ratio"]
  
  # 提取 first 和 second 部分的 m_diff 数据
  first_data_diff <- clean_data[clean_data$Part == "first", "m_diff"]
  second_data_diff <- clean_data[clean_data$Part == "second", "m_diff"]
  
  # 确保 first 和 second 部分的 m_ratio 数据长度相同
  if (length(first_data_ratio) == length(second_data_ratio)) {
    # 进行 m_ratio 的配对样本 t 检验
    t_test_result_ratio <- t.test(first_data_ratio, second_data_ratio, paired = TRUE)
    
    # 对 m_ratio 的 t 值和 p 值进行四舍五入，保留 3 位小数
    t_value_ratio <- round(t_test_result_ratio$statistic, 3)
    p_value_ratio <- round(t_test_result_ratio$p.value, 3)
    
    # 存储 m_ratio 的结果
    new_result_ratio <- data.frame(Exp_Name = exp_name,
                                   t_value = t_value_ratio,
                                   p_value = p_value_ratio)
    results_ratio <- rbind(results_ratio, new_result_ratio)
    
    # 累加 m_ratio 数据到总的数据中
    total_first_data_ratio <- c(total_first_data_ratio, first_data_ratio)
    total_second_data_ratio <- c(total_second_data_ratio, second_data_ratio)
  } else {
    cat(paste("对于 Exp_Name", exp_name, "，m_ratio 的 first 和 second 部分的数据长度不一致，无法进行配对 t 检验。\n"))
  }
  
  # 确保 first 和 second 部分的 m_diff 数据长度相同
  if (length(first_data_diff) == length(second_data_diff)) {
    # 进行 m_diff 的配对样本 t 检验
    t_test_result_diff <- t.test(first_data_diff, second_data_diff, paired = TRUE)
    
    # 对 m_diff 的 t 值和 p 值进行四舍五入，保留 3 位小数
    t_value_diff <- round(t_test_result_diff$statistic, 3)
    p_value_diff <- round(t_test_result_diff$p.value, 3)
    
    # 存储 m_diff 的结果
    new_result_diff <- data.frame(Exp_Name = exp_name,
                                  t_value = t_value_diff,
                                  p_value = p_value_diff)
    results_diff <- rbind(results_diff, new_result_diff)
    
    # 累加 m_diff 数据到总的数据中
    total_first_data_diff <- c(total_first_data_diff, first_data_diff)
    total_second_data_diff <- c(total_second_data_diff, second_data_diff)
  } else {
    cat(paste("对于 Exp_Name", exp_name, "，m_diff 的 first 和 second 部分的数据长度不一致，无法进行配对 t 检验。\n"))
  }
}

# 进行总的 m_ratio 配对样本 t 检验
total_t_test_result_ratio <- t.test(total_first_data_ratio, total_second_data_ratio, paired = TRUE)
# 对总的 m_ratio 的 t 值和 p 值进行四舍五入，保留 3 位小数
total_t_value_ratio <- round(total_t_test_result_ratio$statistic, 3)
total_p_value_ratio <- round(total_t_test_result_ratio$p.value, 3)

# 进行总的 m_diff 配对样本 t 检验
total_t_test_result_diff <- t.test(total_first_data_diff, total_second_data_diff, paired = TRUE)
# 对总的 m_diff 的 t 值和 p 值进行四舍五入，保留 3 位小数
total_t_value_diff <- round(total_t_test_result_diff$statistic, 3)
total_p_value_diff <- round(total_t_test_result_diff$p.value, 3)

# 存储总的 t 检验结果
total_results <- data.frame(Exp_Name = c("m_ratio", "m_diff"),
                            t_value = c(total_t_value_ratio, total_t_value_diff),
                            p_value = c(total_p_value_ratio, total_p_value_diff))

# 保存总的 t 检验结果到新的 CSV 文件
total_output_file <- file.path(file_dir, "Total_T_test.csv")
write.csv(total_results, file = total_output_file, row.names = FALSE)

# 打印保存总的 t 检验结果成功的消息
cat(paste("总的 t 检验结果已保存到", total_output_file, "\n"))

# 准备 m_ratio 绘图数据
plot_data_ratio <- data.frame(
  Part = rep(c("first", "second"), each = length(total_first_data_ratio)),
  m_ratio = c(total_first_data_ratio, total_second_data_ratio)
)

# 准备 m_diff 绘图数据
plot_data_diff <- data.frame(
  Part = rep(c("first", "second"), each = length(total_first_data_diff)),
  m_diff = c(total_first_data_diff, total_second_data_diff)
)

# 定义主题
custom_theme <- theme_minimal() +
  theme(
    plot.title = element_text(hjust = 0.5, size = 16, face = "bold"),
    axis.title = element_text(size = 14),
    axis.text = element_text(size = 12),
    legend.title = element_text(size = 14),
    legend.text = element_text(size = 12)
  )

# 绘制 m_ratio 的箱线图
plot_box_ratio <- ggplot(plot_data_ratio, aes(x = Part, y = m_ratio, fill = Part)) +
  geom_boxplot() +
  labs(title = "First 和 Second 部分 m_ratio 的箱线图",
       x = "部分",
       y = "m_ratio") +
  custom_theme

# 绘制 m_ratio 的柱状图
plot_bar_ratio <- ggplot(plot_data_ratio, aes(x = Part, y = m_ratio, fill = Part)) +
  stat_summary(fun = "mean", geom = "bar") +
  stat_summary(fun.data = "mean_se", geom = "errorbar", width = 0.2) +
  labs(title = "First 和 Second 部分 m_ratio 的柱状图",
       x = "部分",
       y = "m_ratio") +
  custom_theme +
  geom_text(stat = "summary", fun = "mean", aes(label = round(..y.., 3)), vjust = -0.5)

# 绘制 m_diff 的箱线图
plot_box_diff <- ggplot(plot_data_diff, aes(x = Part, y = m_diff, fill = Part)) +
  geom_boxplot() +
  labs(title = "First 和 Second 部分 m_diff 的箱线图",
       x = "部分",
       y = "m_diff") +
  custom_theme

# 绘制 m_diff 的柱状图
plot_bar_diff <- ggplot(plot_data_diff, aes(x = Part, y = m_diff, fill = Part)) +
  stat_summary(fun = "mean", geom = "bar") +
  stat_summary(fun.data = "mean_se", geom = "errorbar", width = 0.2) +
  labs(title = "First 和 Second 部分 m_diff 的柱状图",
       x = "部分",
       y = "m_diff") +
  custom_theme +
  geom_text(stat = "summary", fun = "mean", aes(label = round(..y.., 3)), vjust = -0.5)

# 保存 m_ratio 箱线图
plot_file_box_ratio <- file.path(file_dir, "Total_T_test_m_ratio_boxplot.png")
ggsave(plot_file_box_ratio, plot_box_ratio, width = 8, height = 6)

# 保存 m_ratio 柱状图
plot_file_bar_ratio <- file.path(file_dir, "Total_T_test_m_ratio_barplot.png")
ggsave(plot_file_bar_ratio, plot_bar_ratio, width = 8, height = 6)

# 保存 m_diff 箱线图
plot_file_box_diff <- file.path(file_dir, "Total_T_test_m_diff_boxplot.png")
ggsave(plot_file_box_diff, plot_box_diff, width = 8, height = 6)

# 保存 m_diff 柱状图
plot_file_bar_diff <- file.path(file_dir, "Total_T_test_m_diff_barplot.png")
ggsave(plot_file_bar_diff, plot_bar_diff, width = 8, height = 6)

# 打印保存图表成功的消息
cat(paste("m_ratio 箱线图已保存到", plot_file_box_ratio, "\n"))
cat(paste("m_ratio 柱状图已保存到", plot_file_bar_ratio, "\n"))
cat(paste("m_diff 箱线图已保存到", plot_file_box_diff, "\n"))
cat(paste("m_diff 柱状图已保存到", plot_file_bar_diff, "\n"))

## 统计参与总的 t 检验的数据数量
num_data_ratio <- length(total_first_data_ratio) + length(total_second_data_ratio)
num_data_diff <- length(total_first_data_diff) + length(total_second_data_diff)
cat(paste("参与 m_ratio 配对样本 t 检验的数据数量为", num_data_ratio, "\n"))
cat(paste("参与 m_diff 配对样本 t 检验的数据数量为", num_data_diff, "\n"))