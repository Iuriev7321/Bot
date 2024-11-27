import telebot
import asyncio
import datetime
from telegram_bot_calendar import DetailedTelegramCalendar
bot = telebot.TeleBot('5216878959:AAFUdhGYAKrEK3FscgPIdZxvU_rZuR_VMvo');

LSTEP = {'y':'год', 'm':'месяц', 'd':'день'}
Temp_dict = dict()

@bot.message_handler(content_types=['text'])
def start(message):
    if message.text == "/start":
        bot.send_message(message.from_user.id, "Приветсувую\nЭтот бот - удобный и простой инструмент создания напоминаний\nБот находится в разработке")
    elif message.text == "/create_notify":
        bot.send_message(message.from_user.id, "Введите сообщение напоминания")
        bot.register_next_step_handler(message, get_text)
    elif message.text == "Ня":
        bot.send_message(message.from_user.id, "Я коть")

def get_text(message):
    global Temp_dict
    Temp_dict[str(message.chat.id)+"_text"] = message.text
    bot.send_message(message.from_user.id, "Сообщение напоминания сохранено")
    bot.send_message(message.from_user.id, "Укажите дату напоминания")
    calendar, step = DetailedTelegramCalendar(locale='ru').build()
    bot.send_message(message.from_user.id, f"Укажите {LSTEP[step]}", reply_markup=calendar)

@bot.callback_query_handler(func=DetailedTelegramCalendar.func())
def cal(c):
    global Temp_dict
    result, key, step = DetailedTelegramCalendar(locale='ru').process(c.data)
    if not result and key:
        bot.edit_message_text(f"Укажите {LSTEP[step]}", c.message.chat.id, c.message.message_id, reply_markup=key)
    elif result:
        year, month, day = str(result).split('-');
        bot.edit_message_text("Вы выбрали " + day + "." + month + "." + year, c.message.chat.id, c.message.message_id)
        delta = datetime.datetime(int(year), int(month), int(day)) - datetime.datetime.now()
        Temp_dict[str(c.message.chat.id)+"_date"] = delta.total_seconds()
        bot.send_message(c.message.chat.id, "Введите время напоминания (часы.минуты)")
        bot.register_next_step_handler(c.message, get_time)

def get_time(message):
    global Temp_dict
    if '.' in (message.text):
        hrs, mins = (message.text).split('.')
        if hrs.isdigit() and mins.isdigit():
            hrs = int(hrs)
            mins = int(mins)
            if hrs <= 23 and hrs >= 0 and mins <= 59 and mins >= 0:
                time_to_note = (60 * 60 * 3) + (hrs * 60 * 60) + (mins * 60) + Temp_dict[str(message.chat.id)+"_date"]
                asyncio.run(notify(time_to_note, message))
            else:
                bot.send_message(message.from_user.id, "Неверный формат времени, повторите ввод")
                bot.register_next_step_handler(message, get_time)
        else:
            bot.send_message(message.from_user.id, "Неверный формат времени, повторите ввод")
            bot.register_next_step_handler(message, get_time)
    else:
        bot.send_message(message.from_user.id, "Неверный формат времени, повторите ввод")
        bot.register_next_step_handler(message, get_time)

async def notify(time_to_note, message):
    global Temp_dict
    text_to_note = Temp_dict[str(message.chat.id)+"_text"]
    Temp_dict.clear()
    bot.send_message(message.chat.id, "Напоминание установлено")
    await asyncio.sleep(time_to_note)
    bot.send_message(message.chat.id, "На сегодня установлено напоминание:\n" + text_to_note)

bot.polling(none_stop=True, interval=0)