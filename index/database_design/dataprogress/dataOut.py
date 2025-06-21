import pandas as pd
import pyodbc  # 或者使用适合你的数据库的库，例如 pymssql
from index.database_design.database import *


# 连接到数据库
def get_connection():
    conn = sa_connection()  # 根据你的实际函数名称或连接方式调整
    return conn


# 从数据库中获取数据
def fetch_data_from_db():
    conn = get_connection()
    query = '''SELECT
    provincename,
    name,
    score,
    medal,
    tag1,
    tag2,
	grade,
	time
FROM
    all_info
ORDER BY
    provincename,
    name;
''' # 替换为你的实际查询
    data = pd.read_sql(query, conn)
    conn.close()
    return data


# 将 DataFrame 导出为 Excel 文件
def export_to_excel(data, file_path):
    data.to_excel(file_path, index=False)


def main():
    # 获取数据
    data = fetch_data_from_db()

    # 导出为 Excel 文件
    output_file_path = r'E:\djangoProject2\index\database_design\all.xlsx'  # 替换为你的输出路径
    export_to_excel(data, output_file_path)
    print(data)
    print("Data export completed.")


if __name__ == "__main__":
    main()
