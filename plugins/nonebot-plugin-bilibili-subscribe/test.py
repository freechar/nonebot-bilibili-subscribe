
import asyncio
import base64
import time
from bilibili_api import user, sync, Credential
from nonebot import logger
import skia
from dynrender_skia.Core import DynRender
from dynamicadaptor.DynamicConversion import formate_message

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
            logger.error(f"get dynamic error {ex} userid:{user_id} dynamic_list length:{len(dynamic_list)} retry_count:{retry_count}")
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

async def test():
    id = '35040323'
    dynamic_message_list = await get_dynamic_message(id)
    item = dynamic_message_list[0]
    img = await generatine_pic_of_dyn(item['item'])
    base64_image_string = f"{base64.b64encode(img).decode()}"
    image_data = base64.b64decode(base64_image_string)
    with open("output_image.png", "wb") as file:
        file.write(image_data)


if __name__ == "__main__":
    asyncio.run(test())