import os
import pandas as pd
from ..database import *

# 定义要遍历的文件夹路径
folder_path = r'/index/database_design/datas/noip/2011'

# 连接到数据库
sa = sa_connection()

sql='select * from noip'

data=select(sa,sql)

# 提交更改并关闭数据库连接
sa.commit()
sa.close()
print("Data insertion completed.")
