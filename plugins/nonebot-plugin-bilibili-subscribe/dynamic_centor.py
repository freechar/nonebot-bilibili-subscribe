import asyncio
import base64
from uuid import uuid4
import aiohttp
from .utils import get_dynamic_message, create_tables_from_sql_file, generatine_pic_of_dyn, get_dict_value
import time
from nonebot.adapters.onebot.v11 import Bot
from base64 import b64encode

from nonebot import logger
import os
from nonebot.adapters.onebot.v11 import MessageSegment
from .sqlite_proxy import SQLiteProxy

class DynamicCenter:
    def __init__(self) -> None:

        self.sqlite_path = os.path.join(os.path.dirname(
            os.path.abspath(__file__)), "dynamic_center.db")
        self.sqlite_proxy = SQLiteProxy(self.sqlite_path)
        self.subscribe_list = {}
        self.init_sql_table()
        self.is_first_send = True
    def init_sql_table(self):
        base_url = os.path.dirname(os.path.abspath(__file__))
        sqlite_conn = self.sqlite_proxy
        # 建表从model文件夹
        create_tables_from_sql_file(
            os.path.join(base_url, "model/Subscribers.sql"), sqlite_conn
        )
        create_tables_from_sql_file(
            os.path.join(
                base_url, "model/SubscriptionRelations.sql"), sqlite_conn
        )
        create_tables_from_sql_file(
            os.path.join(base_url, "model/Subscriptions.sql"), sqlite_conn
        )
        self.load_subscribe_list()

    def load_subscribe_list(self) -> None:
        # 创建游标对象
        sqlite_conn = self.sqlite_proxy
        

        # 执行查询语句，获取所有的 Subscriptions 和对应的 Subscribers
        rows = sqlite_conn.execute("SELECT s.subscription_id, s.name AS subscription_name, s.last_dynamic_id, \
                        b.subscriber_id, b.name AS subscriber_name \
                        FROM Subscriptions AS s \
                        INNER JOIN SubscriptionRelations AS r ON s.subscription_id = r.subscription_id \
                        INNER JOIN Subscribers AS b ON r.subscriber_id = b.subscriber_id")

        # 创建一个空的字典来存储结果
        result_dict = {}

        # 处理查询结果
        for row in rows:
            subscription_id, subscription_name, last_dynamic_id, subscriber_id, subscriber_name = row
            # 检查 Subscriptions 是否已经在字典中存在，如果不存在则创建一个空的列表
            if subscription_id not in result_dict:
                result_dict[subscription_id] = {
                    'subscription_name': subscription_name,
                    'last_dynamic_id': last_dynamic_id,
                    'subscribers': []
                }
            # 将 Subscriber 添加到对应的 Subscription 的 subscribers 列表中
            result_dict[subscription_id]['subscribers'].append({
                # str to int
                'subscriber_id': subscriber_id,
                'subscriber_name': subscriber_name,
            })

            self.subscribe_list = result_dict


    @staticmethod
    def get_elements_before_dynamic_id(dynamic_message_list, target_dynamic_id):
        updated_elements = []
        for dynamic in dynamic_message_list:
            if int(dynamic['dynamic_id']) <= int(target_dynamic_id):
                break
            updated_elements.append(dynamic)
        return updated_elements

    def update_dynamic_last_dynamic_id(self, subscription_id, last_dynamic_id):
        cursor = self.sqlite_proxy

        # 更新 last_dynamic_id
        new_last_dynamic_id = last_dynamic_id  # 新的 last_dynamic_id

        # 构建 SQL 更新语句
        sql = "UPDATE Subscriptions SET last_dynamic_id = ? WHERE subscription_id = ?"
        # 执行更新
        cursor.execute(sql, (new_last_dynamic_id, subscription_id))
        

    async def update_dynamic_message(self, sender: Bot) -> None:
        if self.is_first_send:
            need_send = False
            self.is_first_send = False
        for subscription_id, subscription_info in self.subscribe_list.items():
            last_dynamic_id = self.subscribe_list[subscription_id]['last_dynamic_id']
            logger.info(f"subscription_id{subscription_id}, last_dynamic_id{last_dynamic_id}")
            dynamic_message_list = await get_dynamic_message(subscription_id)
            logger.info(f"dynamic_message_list len {len(dynamic_message_list)} subscription_id{subscription_id}")
            if (dynamic_message_list):
                latest_dynamic_id = dynamic_message_list[0]['dynamic_id']
            else:
                continue
            time.sleep(5)
            update_dynamic_message_list = self.get_elements_before_dynamic_id(
                dynamic_message_list, last_dynamic_id)
            subscribers = subscription_info['subscribers']
            for subscriber in subscribers:
                for dynamic_msg in update_dynamic_message_list:
                    # 异步函数
                    # img = await generatine_pic_of_dyn(dynamic_msg['item'])
                    # message = MessageSegment.image(f"base64://{b64encode(img).decode()}")
                    # if get_dict_value(dynamic_msg['item'],'modules','module_dynamic','major','archive','badge','text') == '投稿视频':
                    #     jump_url = get_dict_value(dynamic_msg['item'],'modules','module_dynamic','major','archive','jump_url')
                    #     message += MessageSegment.text(f"视频地址：{jump_url}")
                    # await sender.send_group_msg(
                    #         group_id=subscriber['subscriber_id'], 
                    #         message=message,
                    #         auto_escape=False
                    #     )
                    if need_send:
                        await self.send_dynamic_message_v1(sender, subscriber['subscriber_id'], dynamic_msg)
                        logger.info(f"send message successful to{subscriber['subscriber_id']}")
                    # if self.subscribe_list.get(subscription_id) and  \
                    #     int(self.subscribe_list[subscription_id].get('last_dynamic_id')) < int(dynamic_msg['dynamic_id']):
                    #     self.subscribe_list[subscription_id]['last_dynamic_id'] = dynamic_msg['dynamic_id']

                    #     logger.info(f"update last_dynamic_id cache from {self.subscribe_list[subscription_id]['last_dynamic_id']} "
                    #                 f"to {dynamic_msg['dynamic_id']}")
            logger.info(f"subscription_id{subscription_id}, last_dynamic_id{last_dynamic_id}, latest_dynamic_id{latest_dynamic_id}")      
            if last_dynamic_id != latest_dynamic_id:
                self.update_dynamic_last_dynamic_id(
                    subscription_id, latest_dynamic_id)
                self.load_subscribe_list()

    async def download_pics_file(self, urls):
        imgs = []
        for url in urls:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    img = await resp.read()
                    img = base64.b64encode(img).decode()
                    imgs.append("base64://" + img)
        return imgs
    
    async def send_dynamic_message_v1(self, sender: Bot, group_id: int, dynamic_msg) -> None:
        urls = []
        img = await generatine_pic_of_dyn(dynamic_msg['item'])
        message = MessageSegment.image(f"base64://{b64encode(img).decode()}")
        if get_dict_value(dynamic_msg['item'],'modules','module_dynamic','major','archive','badge','text') == '投稿视频':
            jump_url = get_dict_value(dynamic_msg['item'],'modules','module_dynamic','major','archive','jump_url')
            message += MessageSegment.text(f"视频地址：{jump_url}")
        if get_dict_value(dynamic_msg['item'],'modules','module_dynamic','major','opus','pics'):
            pics = get_dict_value(dynamic_msg['item'],'modules','module_dynamic','major','opus','pics')
            
            for pic in pics:
                urls.append(pic['url'])
            
        # for url in urls:
        #     message += MessageSegment.text(url)
        await sender.send_group_msg(
                group_id=group_id, 
                message=message,
                auto_escape=False
            )
        message =None
        # 异步下载图片 并且转换为base64
        imgs = await self.download_pics_file(urls)
        
        logger.info(f"imgs len {len(imgs)}")

        for img in imgs:
            try:
                logger.info(f"img is {len(img)}")
                message = MessageSegment.image(f"{img}")
                await sender.send_group_msg(
                    group_id=group_id, 
                    message=message,
                    auto_escape=False
                )
            except Exception as e:
                logger.error(f"send img error {e}")
                continue
    
    async def send_dynamic_message_v2(self, sender: Bot, group_id: int, dynamic_msg) -> None:
        module_author = get_dict_value(dynamic_msg['item'],'modules','module_author')
        module_dynamic = get_dict_value(dynamic_msg['item'],'modules','module_dynamic')

        up_name = get_dict_value(module_author,'name')
        title = get_dict_value(module_dynamic,'major','title')
        type = get_dict_value(module_dynamic,'major','type')

    def add_subscription(self, subscription_id, subscription_name, last_dynamic_id = 0):
        cursor = self.sqlite_proxy

        # 插入新的 Subscription
        # 如果不存在再插入
        sql = "INSERT OR IGNORE INTO Subscriptions (subscription_id, name, last_dynamic_id) VALUES (?, ?, ?)"
        cursor.execute(sql, (subscription_id, subscription_name, last_dynamic_id))

    def add_subscriber(self, subscriber_id, subscriber_name):
        cursor = self.sqlite_proxy

        # 插入新的 Subscriber
        # 不存在再新建
        sql = "INSERT OR IGNORE INTO Subscribers (subscriber_id, name) VALUES (?, ?)"
        cursor.execute(sql, (subscriber_id, subscriber_name))


    def add_subscription_relation(self, subscription_id, subscriber_id):
        cursor = self.sqlite_proxy

        # 插入新的 SubscriptionRelation
        # 不存在才插入
        sql = "INSERT OR IGNORE INTO SubscriptionRelations (subscription_id, subscriber_id) VALUES (?, ?)"
        cursor.execute(sql, (subscription_id, subscriber_id))

    async def subscribe(self, group_id, subscription_id):
        # get latest_dynamic_id from bilibili
        latest_dynamic_id = None
        dynamic_message_list = await get_dynamic_message(subscription_id)
        if dynamic_message_list:
            latest_dynamic_id = dynamic_message_list[0]['dynamic_id']
        if latest_dynamic_id:
            self.add_subscription(subscription_id, "test", latest_dynamic_id)
        else:
            self.add_subscription(subscription_id, "test")
        self.add_subscriber(group_id, "test")
        self.add_subscription_relation(subscription_id, group_id)
        self.load_subscribe_list()

    async def unsubscribe(self, group_id, subscription_id):
        cursor = self.sqlite_proxy

        # 删除 SubscriptionRelation
        sql = "DELETE FROM SubscriptionRelations WHERE subscription_id = ? AND subscriber_id = ?"
        cursor.execute(sql, (subscription_id, group_id))

        # 删除没有 Subscriber 的 Subscription
        sql = "DELETE FROM Subscriptions WHERE subscription_id NOT IN (SELECT subscription_id FROM SubscriptionRelations)"
        cursor.execute(sql)
        self.load_subscribe_list()