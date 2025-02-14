import nonebot
from nonebot.adapters.onebot.v11 import Adapter as ONEBOT_V11Adapter



nonebot.init()

driver = nonebot.get_driver()
driver.register_adapter(ONEBOT_V11Adapter)

nonebot.load_builtin_plugins('echo')


nonebot.load_from_toml("pyproject.toml")

config = nonebot.get_driver().config

config.port = 11488

if __name__ == "__main__":
    nonebot.run()