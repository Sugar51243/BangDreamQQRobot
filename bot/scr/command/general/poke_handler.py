from ncatbot.core import BotClient, MessageChain
import random, time
import functions.sendMessage as sendMessage

async def handle_poke(bot: BotClient, msg: dict, owner: list):
    event = 7
    idx = random.randint(0, event-1)
    if idx == 0:
        message = MessageChain(["戳我干嘛(#`O′)"])
        await sendMessage.replyPokeToGroup(bot, msg, message)
        return
    if idx == 1:
        message = MessageChain(["别戳我(。>︿<)"])
        await sendMessage.replyPokeToGroup(bot, msg, message)
        return
    if idx == 2:
        message = MessageChain(["(｡･ˇ_ˇ･｡:)"])
        await sendMessage.replyPokeToGroup(bot, msg, message)
        return
    if idx == 3:
        message = MessageChain(["咬死你＼(`Δ’)／"])
        await sendMessage.replyPokeToGroup(bot, msg, message)
        return
    if idx == 4:
        message = MessageChain(["你知道我的真身是什么吗？(●'◡'●)"])
        await sendMessage.replyPokeToGroup(bot, msg, message)
        time.sleep(1.5)
        await bot.api.send_poke(user_id=msg['user_id'], group_id=msg['group_id'])
        message = MessageChain(["其实是广东双马尾o( ❛ᴗ❛ )o︎"])
        await sendMessage.replyPokeToGroup(bot, msg, message)
        return
    if idx == 5:
        message = MessageChain(["_(:зゝ∠)_"])
        await sendMessage.replyPokeToGroup(bot, msg, message)
        return
    if idx == 6:
        message = MessageChain(["老子戳回来！(｀へ´*)"])
        await sendMessage.replyPokeToGroup(bot, msg, message)
        await bot.api.send_poke(user_id=msg['user_id'], group_id=msg['group_id'])
        return
