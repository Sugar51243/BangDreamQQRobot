from ncatbot.core import MessageChain, At, Reply

async def replyMsgToGroup(bot, msg, messageChain):
    message = MessageChain([
        Reply(msg.message_id),
    ])
    message = message + At(msg.sender.user_id)
    message += " "
    message += messageChain
    await bot.api.post_group_msg(group_id=msg.group_id, rtf=message)


async def sendMsgToGroup(bot, msg, message):
    await bot.api.post_group_msg(group_id=msg.group_id, rtf=message)