from ncatbot.core import BotClient, PrivateMessage, MessageChain, At, Reply

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

async def sendMsgToPrivate(bot: BotClient, msg: PrivateMessage, message):
    await bot.api.post_private_msg(user_id=msg.sender.user_id, rtf=message)

async def replyPokeToGroup(bot, msg, messageChain):
    message = MessageChain([])
    message = message + At(msg['user_id'])
    message += " "
    message += messageChain
    await bot.api.post_group_msg(group_id=msg['group_id'], rtf=message)