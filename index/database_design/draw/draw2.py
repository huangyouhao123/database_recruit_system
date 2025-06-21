import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

# 生成示例数据（非负数）
np.random.seed(0)
scores = np.random.exponential(scale=50, size=1000)  # 对数正态分布示例数据

# 计算实际数据的均值
actual_mean = np.mean(scores)
print(f"Actual mean: {actual_mean}")

# 拟合正态分布
params_norm = stats.norm.fit(scores)
mean_norm, std_norm = params_norm

# 拟合对数正态分布
params_lognorm = stats.lognorm.fit(scores, floc=0)
shape_lognorm, loc_lognorm, scale_lognorm = params_lognorm

# 打印拟合参数
print(f"Normal distribution parameters: mean={mean_norm}, std={std_norm}")
print(f"Log-normal distribution parameters: shape={shape_lognorm}, loc={loc_lognorm}, scale={scale_lognorm}")

# 绘制成绩分布
plt.figure(figsize=(12, 8))
sns.histplot(scores, kde=True, bins=30, stat='density', color='blue', label='Data')

# 生成正态分布曲线
xmin, xmax = plt.xlim()
x = np.linspace(xmin, xmax, 100)
pdf_fitted_norm = stats.norm.pdf(x, mean_norm, std_norm)
plt.plot(x, pdf_fitted_norm, 'r--', lw=2, label='Fitted Normal Distribution')

# 生成对数正态分布曲线
pdf_fitted_lognorm = stats.lognorm.pdf(x, shape_lognorm, loc_lognorm, scale_lognorm)
plt.plot(x, pdf_fitted_lognorm, 'g--', lw=2, label='Fitted Log-normal Distribution')

plt.title('Score Distribution with Fitted Distributions')
plt.xlabel('Score')
plt.ylabel('Density')
plt.legend()
plt.grid(True)

# 显示图表
plt.show()
