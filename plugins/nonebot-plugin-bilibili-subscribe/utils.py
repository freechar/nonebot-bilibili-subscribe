import time
from bilibili_api import user, sync, Credential
from nonebot import logger
from .sqlite_proxy import SQLiteProxy
import skia
from dynrender.Core import DynRender
from dynamicadaptor.DynamicConversion import formate_message


async def get_dynamic_message(user_id: int):
    credential = Credential(
        sessdata="XXX",
        bili_jct="XXX",
        buvid3="XXX",
        dedeuserid="XXX"
    )
    user_id = int(user_id)
    u = user.User(uid=user_id, credential=credential)
    offset = ''
    dynamic_list = []
    retry_count = 0
    while dynamic_list.__len__() < 10 and retry_count < 3:
        print(f'fetch, offset->{offset}')
        try:
            res = await u.get_dynamics_new(offset)
        except BaseException as ex:
            print(ex)
            logger.error(f"get dynamic error {ex}")
            retry_count += 1
            time.sleep(5)
            continue
        else:
            for item in res['items']:
                dynamic = {
                    'dynamic_id': int(item['id_str']),
                    'timestamp': item['modules']['module_author']['pub_ts'],
                    'item': item
                }
                dynamic_list.append(dynamic)
            if not res['has_more']:
                break
            offset = res['offset']
        time.sleep(5)
    # sort by dynamic_id
    dynamic_list.sort(key=lambda x: x['dynamic_id'], reverse=True)
    return dynamic_list

def create_tables_from_sql_file(file_path, db_conn: SQLiteProxy):
    # 读取 SQL 文件中的建表语句
    with open(file_path, 'r') as sql_file:
        sql_statements = sql_file.read().split(';')

    # 去除语句列表中的空语句
    sql_statements = [statement.strip() for statement in sql_statements if statement.strip()]

    # 执行每个建表语句
    for statement in sql_statements:
        db_conn.execute(statement)

# 定义异步函数，用于执行Web测试
async def generatine_pic_of_dyn(item):

    # 格式化消息数据
    message_formate = await formate_message("web", item)

    # 使用DynRender执行动态渲染
    img = await DynRender().run(message_formate)

    # 将渲染后的图像转换为Skia Image对象
    img = skia.Image.fromarray(img, colorType=skia.ColorType.kRGBA_8888_ColorType)

    # 保存图像为PNG文件
    data = img.encodeToData()

    bytes_data = bytearray(data.bytes())
    return bytes_data

# 多层dict get 存在返回值，不存在返回None
def get_dict_value(data, *keys):
    # sample
    # data = {'a': {'b': {'c': 1}}}
    # get_dict_value(data, 'a', 'b', 'c') => 1
    if data is None:
        return None
    for key in keys:
        if isinstance(data, dict) and key in data:
            data = data[key]
        else:
            return None
    return data