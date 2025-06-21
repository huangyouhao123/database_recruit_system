import matplotlib.pyplot as plt
import numpy as np
from matplotlib import rcParams
from index.database_design.database import *

# 设置支持中文的字体
rcParams['font.sans-serif'] = ['SimHei']  # 使用SimHei字体来显示中文标签
rcParams['axes.unicode_minus'] = False  # 解决负号'-'显示为方块的问题

# 获取数据
sa = sa_connection()
sql = '''select provincename from province'''
province = select(sa, sql)
province = {pro['provincename']: [0, 0, 0] for pro in province}

sql = '''select provincename, medal, count(*) as nums 
         from noi 
         where time='2018' 
         group by provincename, medal 
         order by provincename, medal'''
data = select(sa, sql)

for row in data:
    try:
        if row['medal'] == '金牌':
            province[row['provincename']][0] = row['nums']
        elif row['medal'] == '银牌':
            province[row['provincename']][1] = row['nums']
        elif row['medal'] == '铜牌':
            province[row['provincename']][2] = row['nums']
    except KeyError:
        continue

# 处理数据
categories = list(province.keys())
subcategories = ['金牌', '银牌', '铜牌']
data = np.array(list(province.values()))

# 创建图形和轴
fig, ax = plt.subplots(figsize=(12, 8))  # 调整图形大小

# 颜色设置
colors = ['#FFD700', '#C0C0C0', '#CD7F32']  # 金色、银色、铜色

# 堆叠条形图
left = np.zeros(len(categories))
for i, (subcat, color) in enumerate(zip(subcategories, colors)):
    bars = ax.barh(categories, data[:, i], left=left, label=subcat, color=color, edgecolor='white')
    left += data[:, i]

    # 在条块上显示数量
    for bar in bars:
        width = bar.get_width()

# 添加标签和标题
ax.set_xlabel('数值', fontsize=14)
ax.set_ylabel('类别', fontsize=14)
ax.set_title('堆叠横向条形图', fontsize=16, fontweight='bold')
ax.legend(title='子类别', fontsize=12, title_fontsize='13', loc='upper right')

# 美化图表
ax.grid(True, linestyle='--', alpha=0.6)
ax.set_axisbelow(True)

# 设置 x 轴和 y 轴刻度字体
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)

# 调整图例位置
ax.legend(loc='upper left', bbox_to_anchor=(1, 1))

# 显示图表
plt.tight_layout()
plt.show()
