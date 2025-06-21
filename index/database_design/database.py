import pymssql

import base64


def sa_connection():
    return pymssql.connect(server='HUANGYOUHAO\\SQLEXPRESS', user='sa', password='123', database='math',
                           charset='cp936', as_dict=True)


def change_encode(string: str):
    return string.encode('cp936')


def shift_image(binary_image_data):
    base64_image_data = base64.b64encode(binary_image_data).decode('utf-8')
    return base64_image_data


def open_connection(user, password):
    conn = None
    try:
        conn = pymssql.connect(server='HUANGYOUHAO\\SQLEXPRESS', user=str(user), password=str(password),
                               database='Recruitment', charset='cp936', as_dict=True)
    except:
        raise Exception('连接失败')
    finally:
        return conn


# 服务器名，账号，密码，数据库名
def select_with_para(conn, sql, para):
    cursor = conn.cursor()
    cursor.execute(sql, para)
    result = cursor.fetchall()
    conn.commit()
    cursor.close()
    return result


def select(conn, sql):
    cursor = conn.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()
    conn.commit()
    cursor.close()
    return result


def insert(conn, sql, values):
    cursor = conn.cursor()
    cursor.execute(sql, values)
    # conn.commit()
    # cursor.close()


def delete(conn, sql, parameters):
    cursor = conn.cursor()
    cursor.execute(sql, parameters)
    conn.commit()
    cursor.close()


def update(conn, sql, values):
    insert(conn, sql, values)


def execute(conn, name, parameters):
    cursor = conn.cursor()
    cursor.callproc(name, parameters)
    conn.commit()
    cursor.close()


def execute_without_para(conn, name):
    cursor = conn.cursor()
    cursor.callproc(name)
    conn.commit()
    cursor.close()


if __name__ == '__main__':
    sa = sa_connection()
    sql = 'select * from [dbo].[province]'
    school = select(sa, sql)
    print(school[0])
