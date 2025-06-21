import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import skewnorm
import seaborn as sns
from index.database_design.database import *

# 定义要遍历的文件夹路径
folder_path = r'/index/database_design/datas/noip/2011'

# 连接到数据库
sa = sa_connection()

sql = 'select * from noip where tag=0 and time=2016'

data = select(sa, sql)
data = pd.DataFrame(data)
print(data)
# 提交更改并关闭数据库连接
sa.commit()
sa.close()

# 提取 'score' 列数据
scores = data['score'].dropna()

# 计算基本统计信息
max_score = scores.max()
min_score = scores.min()
median_score = scores.median()
mean_score = scores.mean()
std_dev = scores.std()

# 拟合偏态分布
a, loc, scale = skewnorm.fit(scores)

# 计算拟合曲线
x = np.linspace(scores.min(), scores.max(), 1000)
pdf_fitted = skewnorm.pdf(x, a, loc, scale)

# 绘制原始数据的频率分布曲线、偏态分布的拟合曲线和核密度估计曲线
plt.figure(figsize=(10, 6))

# 绘制直方图
sns.histplot(scores, kde=False, bins=30, stat='density', color='blue', alpha=0.6, label='Data Histogram')

# 绘制偏态分布拟合曲线
plt.plot(x, pdf_fitted, 'r-', lw=2, label='Skew-Normal Fit')

# 绘制核密度估计曲线
sns.kdeplot(scores, bw_adjust=0.5, color='green', label='KDE')

plt.title('Score Frequency Distribution with Skew-Normal Fit and KDE')
plt.xlabel('Score')
plt.ylabel('Density')
plt.legend()
plt.grid(True)

# 显示图表
plt.show()

# 打印统计信息和偏态分布参数
print(f'Statistical Summary:')
print(f'Max Score: {max_score}')
print(f'Min Score: {min_score}')
print(f'Median Score: {median_score}')
print(f'Mean Score: {mean_score}')
print(f'Standard Deviation: {std_dev}')

print(f'\nSkew-Normal Distribution Parameters:')
print(f'Skewness parameter (a): {a}')
print(f'Scale parameter (scale): {scale}')
print(f'Location parameter (loc): {loc}')
