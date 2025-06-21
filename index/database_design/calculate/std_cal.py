from collections import defaultdict

import pandas as pd

from index.database_design.database import *
import numpy as np
sa = sa_connection()


def round_preserve_sum(arr):
    rounded = np.round(arr)
    diff = int(round(np.sum(arr)) - np.sum(rounded))

    # 获取误差调整的索引
    idxs = np.argsort(arr - rounded)

    for i in range(abs(diff)):
        idx = idxs[i if diff > 0 else -(i + 1)]
        if diff > 0:
            rounded[idx] += 1
        elif rounded[idx] > 0:
            rounded[idx] -= 1

    return rounded
def best_allocate(std_dct:defaultdict,data_dct:dict):
    keys=['0-100', '100-200', '200-300', '300-400', '400-500', '500-600']
    lengths=[]
    N=100
    sum=0
    for key in keys:
        lengths.append(len(data_dct[key]))
        sum+=len(data_dct[key])*std_dct[key]
    ans=[]
    if sum==0:
        return [0,0,0,0,0,0]
    for idx,key in enumerate(keys):
        ans.append(N*lengths[idx]*std_dct[key]/sum)
    ans=round_preserve_sum(np.array(ans))
    return ans

years=[2011,2012,2013,2014,2015,2016,2017,2018,2019]
provinces = [f"{num:03}" for num in range(31)]


all_all=[]
for time in years:
    p_all=[]
    for province in provinces:
        # 左开右闭
        score_slice={'0-100':[],'100-200':[],'200-300':[],'300-400':[],'400-500':[],'500-600':[]}
        sql='select * from noip where time=%s and provinceid=%s and tag=0'
        res=select_with_para(sa,sql,(time,province))
        for data in res:
            score=data['score']
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
            elif 500 < score <=600:
                score_slice['500-600'].append(score)
        std_dict=defaultdict(float)
        for key,value in score_slice.items():
            if len(value)>1:
                std_dict[key]=np.std(score_slice[key], ddof=1)  # 使用ddof=1来计算样本标准差
            else:
                std_dict[key]=0
        try:
            allocate_list=best_allocate(std_dict,data_dct=score_slice)
        except:
            print(time,province,score_slice,std_dict)
        p_all.append(allocate_list)
    all_all.append(p_all)
print(len(all_all),len(all_all[0]),len(all_all[0][0]))
all_all=np.array(all_all)
print(all_all)
# 将数组转换为DataFrame
# df = pd.DataFrame(all_all, columns=["Values"])
#
# # 导出到Excel
# df.to_excel(r"E:\djangoProject2\index\database_design\calculate\output.xlsx", index=False)
#
# print("Data has been exported to output.xlsx")
allocate_dict={'time':[],'province':[],'0-100':[],'100-200':[],'200-300':[],'300-400':[],'400-500':[],'500-600':[]}

for idx_t,time in enumerate(years):
    for idx_p,province in enumerate(provinces):
        d1,d2,d3,d4,d5,d6=all_all[idx_t,idx_p]
        allocate_dict['time'].append(time)
        allocate_dict['province'].append(province)
        allocate_dict['0-100'].append(d1)
        allocate_dict['100-200'].append(d2)
        allocate_dict['200-300'].append(d3)
        allocate_dict['300-400'].append(d4)
        allocate_dict['400-500'].append(d5)
        allocate_dict['500-600'].append(d6)

df=pd.DataFrame(allocate_dict)
df.to_excel(r"E:\djangoProject2\index\database_design\calculate\tigaozu.xlsx", index=False)
