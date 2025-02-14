from pathlib import Path

import nonebot
from nonebot import get_plugin_config
from nonebot import on_command
from nonebot.rule import to_me
from nonebot.plugin import PluginMetadata
from nonebot.exception import MatcherException
from nonebot.matcher import Matcher
from nonebot import require
from .config import Config
from .dynamic_centor import DynamicCenter
from nonebot.params import Arg, CommandArg
from nonebot.adapters import Message
from nonebot.adapters.onebot.v11 import GroupMessageEvent, MessageSegment, MessageEvent
from nonebot import logger
from datetime import datetime
import threading
import time

# 创建一个锁
lock = threading.Lock()

require("nonebot_plugin_apscheduler")

from nonebot_plugin_apscheduler import scheduler


__plugin_meta__ = PluginMetadata(
    name="bilibili-subscribe",
    description="",
    usage="",
    type="library",
    homepage="",
    config=Config,
    supported_adapters={"nonebot.adapters.onebot.v11"},
)

config = get_plugin_config(Config)

sub_plugins = nonebot.load_plugins(
    str(Path(__file__).parent.joinpath("plugins").resolve())
)
dynamic_center = DynamicCenter() 

BiliSub = on_command("bilibili_subscribe", aliases={"subscribe_bilibili"}, priority=10, block=True)

@BiliSub.handle()
async def BiliBiliSub(
    event: MessageEvent,
    matcher: Matcher,
    args: Message = CommandArg()
):
    logger.info(f"BiliBiliSub: {args.extract_plain_text()}")
    if Subscription_id := args.extract_plain_text():
        if Subscription_id == "test":
            logger.info("test START")
            await dynamic_center.send_test_msg(nonebot.get_bot())
            logger.info("test END")
            return
        # 判断是否是纯数字
        if not Subscription_id.isdigit():
            await BiliSub.finish(MessageSegment.text("请输入正确的订阅号"))
        else:
            Subscription_id = int(Subscription_id)
            # 订阅
            await dynamic_center.subscribe(event.group_id, Subscription_id)
            await BiliSub.finish(MessageSegment.text(f"订阅成功，订阅号为{Subscription_id}"))
    else:
        await BiliSub.finish(MessageSegment.text("FINISH"))

BiliunSub = on_command("bilibili_unsubscribe", aliases={"unsubscribe_bilibili"}, priority=10, block=True)
@BiliunSub.handle()
async def BiliBiliUnSub(
        event: MessageEvent,
        matcher: Matcher,
        args: Message = CommandArg()
):
    logger.info(f"BiliBiliUnSub: {args.extract_plain_text()}")
    if Subscription_id := args.extract_plain_text():
        # 判断是否是纯数字
        if not Subscription_id.isdigit():
            await BiliunSub.finish(MessageSegment.text("请输入正确的订阅号"))
        else:
            Subscription_id = int(Subscription_id)
            # 取消订阅
            await dynamic_center.unsubscribe(event.group_id, Subscription_id)
            await BiliunSub.finish(MessageSegment.text(f"取消订阅成功，订阅号为{Subscription_id}"))
    else:
        await BiliunSub.finish(MessageSegment.text("FINISH"))



# 基于装饰器的方式
@scheduler.scheduled_job("interval", minutes = 5, id="send_message",start_date=datetime.now(), args=[1])
async def run_every_5_minutes(arg1: int):
    if lock.acquire(timeout=0.1):
        try:
            await dynamic_center.update_dynamic_message(nonebot.get_bot())
            print("run_every_5_minutes")
        finally:
            lock.release()
    else:
        print(f"Failed to acquire lock in {threading.current_thread().name}")

