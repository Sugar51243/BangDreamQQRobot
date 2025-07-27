# ========== 模块导入 ==========
# ---------- 导入必要模块 ----------
from ncatbot.core import BotClient, GroupMessage, PrivateMessage
from ncatbot.utils import get_log
# ---------- 导入自定义模块 ----------
from functions.permission import registration
from command.handleCommand import handle_group_message, handle_private_message, handle_notice_event, handle_request_event


# ========== 代码主体 ==========
# ---------- 机器人权限注册 ----------
owner = registration(["114514"])
robotAcc = "1919810"
# ---------- 创建 BotClient ----------
bot = BotClient()
_log = get_log()
# ========= 注册回调函数 ==========
@bot.group_event()
async def on_group_message(msg: GroupMessage):
    _log.info(msg)
    await bot.api.mark_group_msg_as_read(group_id=msg.group_id)
    await handle_group_message(bot=bot, robotAcc=robotAcc, msg=msg, owner=owner)

@bot.private_event()
async def on_private_message(msg: PrivateMessage):
    _log.info(msg)
    await bot.api.mark_private_msg_as_read(user_id=msg.sender.user_id)
    await handle_private_message(bot=bot, robotAcc=robotAcc, msg=msg, owner=owner)

@bot.notice_event()
async def on_notice_event(msg):
    _log.info(msg)
    await handle_notice_event(bot=bot, robotAcc=robotAcc, msg=msg, owner=owner)

@bot.handle_request_event
async def on_request_event(msg):
    _log.info(msg)
    await handle_request_event(bot=bot, robotAcc=robotAcc, msg=msg, owner=owner)

# ========== 启动 BotClient==========
if __name__ == "__main__":
    bot.run(bt_uin=robotAcc,enable_webui_interaction=False)