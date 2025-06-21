import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import skewnorm, skew, kurtosis
import seaborn as sns
from index.database_design.database import *

years=[2011,2012,2013,2014,2015,2016,2017,2018,2019]
provinces = [f"{num:03}" for num in range(31)]

# 连接到数据库
sa = sa_connection()
data_feature={'year':[],'province':[],'min':[], 'max':[], 'mean':[], 'median':[], 'std':[], 'skewness':[], 'kurtosis(excess)':[],'Kurtosis (including 3)':[]}

for time in years:
    for province in provinces:
        sql = 'SELECT * FROM noip WHERE time=%s AND provinceid=%s AND tag=1'
        data = select_with_para(sa, sql, (time, province))
        data = pd.DataFrame(data)
        print(f'\nData for Time={time} and Province={province}:')
        if data.empty:
            data_feature['year'].append(time)
            data_feature['province'].append(province)
            data_feature['min'].append(0)
            data_feature['mean'].append(0)
            data_feature['max'].append(0)
            data_feature['median'].append(0)
            data_feature['std'].append(0)
            data_feature['skewness'].append(0)
            data_feature['kurtosis(excess)'].append(0)
            data_feature['Kurtosis (including 3)'].append(0)
            continue
        # 提取 'score' 列数据
        scores = data['score'].dropna()

        # 计算基本统计信息
        max_score = scores.max()
        min_score = scores.min()
        median_score = scores.median()
        mean_score = scores.mean()
        std_dev = scores.std()

        # 计算偏度和峰度
        skewness = skew(scores)
        kurt = kurtosis(scores)
        kurt_non_fisher = kurtosis(scores, fisher=False)

        # # 打印统计信息和偏度、峰度
        # print(f'Statistical Summary:')
        # print(f'Max Score: {max_score}')
        # print(f'Min Score: {min_score}')
        # print(f'Median Score: {median_score}')
        # print(f'Mean Score: {mean_score}')
        # print(f'Standard Deviation: {std_dev}')
        # print(f'Skewness: {skewness}')
        # print(f'Kurtosis (excess): {kurt}')
        # print(f'Kurtosis (including 3): {kurt_non_fisher}')
        data_feature['year'].append(time)
        data_feature['province'].append(province)
        data_feature['min'].append(min_score)
        data_feature['mean'].append(mean_score)
        data_feature['max'].append(max_score)
        data_feature['median'].append(median_score)
        data_feature['std'].append(std_dev)
        data_feature['skewness'].append(skewness)
        data_feature['kurtosis(excess)'].append(kurt)
        data_feature['Kurtosis (including 3)'].append(kurt_non_fisher)

sa.commit()
sa.close()
df=pd.DataFrame(data_feature)
df.to_excel('data_feature普及组.xlsx')
