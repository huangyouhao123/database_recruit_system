import random
from collections import defaultdict
import pandas as pd
import numpy as np

from index.database_design.database import *

# 创建数据库连接
sa = sa_connection()

# 读取 Excel 文件
sample_num = pd.read_excel(r'E:\djangoProject2\index\database_design\calculate\提高组.xlsx')

# 选择 time 为 2018 的数据
data_2018 = sample_num[sample_num['time'] == 2018]

sample_result=[]
provincename=[]
# 遍历每一行的数据并获取特定属性
for index, row in data_2018.iterrows():
    score_slice = {'0-100': [], '100-200': [], '200-300': [], '300-400': [], '400-500': [], '500-600': []}
    provinceid=row['province']
    formatted_number = str(provinceid).zfill(3)
    sql='select * from noip where provinceid=%s and tag=0'
    res=select_with_para(sa,sql,(formatted_number,))
    sql='select provincename from province where provinceid=%s'
    p=select_with_para(sa,sql,(formatted_number,))[0]['provincename']
    provincename.append(p)
    for data in res:
        score = data['score']
        if 0 <= score <= 100:
            score_slice['0-100'].append(score)
        elif 100 < score <= 200:
            score_slice['100-200'].append(score)
        elif 200 < score <= 300:
            score_slice['200-300'].append(score)
        elif 300 < score <= 400:
            score_slice['300-400'].append(score)
        elif 400 < score <= 500:
            score_slice['400-500'].append(score)
        elif 500 < score <= 600:
            score_slice['500-600'].append(score)
            #0-100	100-200	200-300	300-400	400-500	500-600
    n1=row['0-100']
    n2=row['100-200']
    n3=row['200-300']
    n4=row['300-400']
    n5=row['400-500']
    n6=row['500-600']
    nk=[n1,n2,n3,n4,n5,n6]
    ans=list()
    for idx,key in enumerate(score_slice.keys()):
        sampled_numbers = random.choices(score_slice[key], k=nk[idx])
        sampled_numbers=sampled_numbers
        ans.extend(sampled_numbers)

    if len(ans)==0:
        ans=np.array([0 for _ in range(100)])
    if len(ans)!=100:
        print(row['province'])
    sample_result.append(ans)
ans=sample_result
province_Score=[]
for i in range(len(ans)):
    sum=0
    for j in range(len(ans[0])):
        ans[i][j]=ans[i][j]*1.0/600
        sum+=np.exp(ans[i][j])
    province_Score.append(sum-100)
print(ans)
print(province_Score)

df={'province':provincename,'score':province_Score}
print(df)
df=pd.DataFrame(df)
df.to_excel('province.xlsx',index=False)
# ans=pd.DataFrame(ans)
# ans.to_excel('sample_pujizu.xlsx')
