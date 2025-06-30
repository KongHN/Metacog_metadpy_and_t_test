# 加载所需包
library(lme4)
library(dplyr)
library(ggplot2)
library(tidyr)
library(car)
library(effects)
library(MuMIn)
library(corrplot)

# 读取数据（替换为您的文件路径）
data <- read.csv("F://科研//02Metacog//data test//test//meta_data_result//0meta_data.csv")

# 数据预处理
data$Part <- as.factor(data$Part)
data$Difficulty <- as.factor(data$Difficulty)
data$Category <- as.factor(data$Category)
data$Trials_scaled <- scale(data$Trials)
data$m_ratio_scaled <- scale(data$m_ratio)
data$m_diff_scaled <- scale(data$m_diff)

# 探索性数据分析
par(mfrow = c(1, 2))
hist(data$m_ratio, main = "m_ratio分布", col = "skyblue")
hist(data$m_diff, main = "m_diff分布", col = "lightgreen")

ggplot(data, aes(x = Part, y = m_ratio, fill = Part)) +
  geom_boxplot() +
  theme_minimal() +
  labs(title = "m_ratio按Part分组的箱线图")

ggplot(data, aes(x = Difficulty, y = m_diff, fill = Difficulty)) +
  geom_boxplot() +
  theme_minimal() +
  labs(title = "m_diff按Difficulty分组的箱线图")

cor_matrix <- cor(data[, c("Trials", "m_ratio", "m_diff")], use = "complete.obs")
round(cor_matrix, 2)
corrplot(cor_matrix, method = "color", type = "upper", tl.col = "black", tl.srt = 45)

# 建立混合效应模型
model_m_ratio <- lmer(m_ratio ~ Trials + Difficulty + Category + (1|Part), data = data)
model_m_diff <- lmer(m_diff ~ Trials + Difficulty + Category + (1|Part), data = data)

# 模型诊断
summary(model_m_ratio)
summary(model_m_diff)
par(mfrow = c(2, 2))
plot(model_m_ratio, which = 1:4)
qqmath(residuals(model_m_ratio))

# 固定效应显著性检验
Anova(model_m_ratio, type = 3)
Anova(model_m_diff, type = 3)

# 模型比较
model_m_ratio_null <- lmer(m_ratio ~ 1 + (1|Part), data = data)
model_m_ratio_full <- lmer(m_ratio ~ Trials + Difficulty + Category + (1|Part), data = data)
AIC(model_m_ratio_null, model_m_ratio_full)
anova(model_m_ratio_null, model_m_ratio_full)

# 效应分析与可视化
eff_m_ratio <- effects::effect("Difficulty", model_m_ratio)
plot(eff_m_ratio, type = "条形图", col = "steelblue", main = "Difficulty对m_ratio的影响")

eff_m_diff <- effects::effect("Category", model_m_diff)
plot(eff_m_diff, type = "条形图", col = "darkgreen", main = "Category对m_diff的影响")

eff_trials <- effects::effect("Trials", model_m_ratio)
plot(eff_trials, type = "线图", col = "red", main = "Trials对m_ratio的影响")

data$pred_m_ratio <- predict(model_m_ratio)
ggplot(data, aes(x = m_ratio, y = pred_m_ratio)) +
  geom_point(col = "blue", alpha = 0.5) +
  geom_abline(slope = 1, intercept = 0, linetype = "dashed", col = "red") +
  theme_minimal() +
  labs(title = "m_ratio实际值与预测值对比")

# 模型拟合指数
r2_m_ratio <- r2glmm(model_m_ratio)
r2_m_diff <- r2glmm(model_m_diff)
r2_m_ratio
r2_m_diff

# 随机效应分析
ranef(model_m_ratio)