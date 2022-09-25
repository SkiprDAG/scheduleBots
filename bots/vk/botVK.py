from vkbottle import API, PhotoMessageUploader, LoopWrapper, BaseStateGroup
from vkbottle import Keyboard, KeyboardButtonColor, Text, EMPTY_KEYBOARD
from vkbottle.bot import Bot, Message
from custom_rules import Permission

from config import CANCEL, dayWeek, sunday, USER_ID_VK
from config import TOKEN_VK, GROUP_VK, MSG_HELLO_VK, MSG_CHECK_BUTTON, CHECK
from data.pars import mainIrgups, mainIrnitu
from db.database import create, getDay, checkGroup

bot_group_id = GROUP_VK
bot_token = TOKEN_VK

bot = Bot(bot_token, bot_group_id)
api = API(token=bot_token)
bot.labeler.message_view.replace_mention = True
bot.on.vbml_ignore_case = True
uploader = PhotoMessageUploader(bot.api)
lw = LoopWrapper()

primaryKeyboard = (Keyboard(one_time=False, inline=False)
                   .add(Text('This Day', {'cmd': 'Day'}), color=KeyboardButtonColor.POSITIVE)
                   .add(Text('Next Day', {'cmd': 'Day'}), color=KeyboardButtonColor.POSITIVE)
                   .row()
                   .add(Text('This Week', {'cmd': 'Week'}), color=KeyboardButtonColor.POSITIVE)
                   .add(Text('Next Week', {'cmd': 'Week'}), color=KeyboardButtonColor.POSITIVE))


async def messageToMe(msg):
    await bot.api.messages.send(user_id=USER_ID_VK, message=msg, random_id=0)


@bot.loop_wrapper.interval(days=1)
async def looper():
    await messageToMe('start pars')
    await messageToMe(mainIrgups())
    await messageToMe(mainIrnitu())


lw.add_task(looper())


class RegGroup(BaseStateGroup):
    GroupId = 0


@bot.on.message(Permission(), lev="/start")
async def start(message: Message):
    await bot.state_dispenser.set(message.peer_id, RegGroup.GroupId)
    await message.answer(
        message=MSG_HELLO_VK,
        keyboard=Keyboard(one_time=False, inline=False)
        .add(Text('Cancel'), color=KeyboardButtonColor.NEGATIVE)
    )


@bot.on.message(state=RegGroup.GroupId)
async def hand(message: Message):
    if message.text == 'Cancel':
        await message.answer(message=CANCEL, keyboard=await cancel(message))
        await bot.state_dispenser.delete(message.peer_id)
        return
    await message.answer(CHECK)
    group = message.text.upper().replace(" ", "")
    msg = create(message.peer_id, group, message.from_id)
    if msg[0]:
        await message.answer(
            message=f'Не существует группы {group}\nПовторите попытку\nПример: @softenginebot ПИ.1-20-1(И,О)-2')
        await bot.state_dispenser.set(message.peer_id, RegGroup.GroupId)
    else:
        await bot.state_dispenser.delete(message.peer_id)
        await message.answer(
            message=msg[1],
            keyboard=primaryKeyboard
        )
        await messageToMe(f'{message.peer_id}, {message.text}')
        return MSG_CHECK_BUTTON


async def cancel(message: Message):
    return primaryKeyboard if checkGroup(message.peer_id) else EMPTY_KEYBOARD


@bot.on.message(payload={'cmd': 'Week'})
async def scheduleWeek(message: Message):
    msg = message.text.split(' ')
    photo = getDay(message.peer_id, msg[1].lower(), msg[0].lower())
    attachment = await uploader.upload(photo)
    await message.answer(
        attachment=attachment
    )


@bot.on.message(payload={'cmd': 'Day'})
async def scheduleDay(message: Message):
    msg = message.text.split(' ')
    day = dayWeek(msg)
    try:
        photo = getDay(message.peer_id, day[0], day[1])
        attachment = await uploader.upload(photo)
        await message.answer(
            attachment=attachment
        )
    except Exception:
        await message.answer(
            message=sunday(msg, day[0])
        )


@bot.on.message(Permission(), lev="/pars")
async def start(message: Message):
    await messageToMe('pars')
    await messageToMe(mainIrgups())
    await messageToMe(mainIrnitu())


def startVK():
    bot.run_forever()


if __name__ == '__main__':
    startVK()
