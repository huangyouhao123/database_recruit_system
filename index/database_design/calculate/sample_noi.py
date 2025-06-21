import random
from collections import defaultdict
import pandas as pd
import numpy as np
from index.database_design.database import *

# 创建数据库连接
sa = sa_connection()
sql='select * from province'
province=select(sa,sql)
province={i['provincename']:0 for i in province}
print(province)
sql="select * from noi where time=2018"
data=select(sa,sql)
print(data)

for row in data:
    try:
        province[row['provincename']]+=np.exp(row['score']/600)
    except:
        continue
print(province)
df={'province':province.keys(),'score':province.values()}
df=pd.DataFrame(df)
df.to_excel('province1.xlsx')