import logging
import datetime
from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from database import init_db, get_schedule_by_day, add_user, get_all_users

logging.basicConfig(level=logging.INFO)

TELEGRAM_TOKEN = "8995925816:AAGKPuDuRdEgtlMycIkW84ctaje2KYhEX1o"
CHAT_ID = 1333034189

app = FastAPI()
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

init_db()

menu_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📅 Расписание на сегодня")],
        [KeyboardButton(text="📝 Все пары")]
    ],
    resize_keyboard=True
)

# Функция для автоматического определения текущей четности недели
def get_current_parity():
    # Получаем номер текущей недели в году
    week_number = datetime.datetime.now().isocalendar()[1]
    
    if week_number % 2 == 0:
        return "Нечетная"
    else:
        return "Четная"

# Функция для перевода английских дней недели на русский (для datetime)
def get_russian_day():
    days = {
        "Monday": "Понедельник",
        "Tuesday": "Вторник",
        "Wednesday": "Среда",
        "Thursday": "Четверг",
        "Friday": "Пятница",
        "Saturday": "Суббота",
        "Sunday": "Воскресенье"
    }
    eng_day = datetime.datetime.now().strftime("%A")
    return days.get(eng_day, "Понедельник")


@dp.message(lambda message: message.text == "/start")
async def cmd_start(message: types.Message):
    add_user(message.chat.id)
    await message.answer(
        f"Привет, {message.from_user.first_name}! Ты успешно подписан на расписание и важные уведомления группы 4542.",
        reply_markup=menu_keyboard
    )

# Кнопка расписания на сегодня
@dp.message(lambda message: message.text == "📅 Расписание на сегодня")
async def get_today_schedule(message: types.Message):
    day = get_russian_day()       # Авто-определение дня (например, Вторник)
    parity = get_current_parity() # Авто-определение четности (Четная/Нечетная)
    
    pairs = get_schedule_by_day(day, parity)
    
    if not pairs:
        await message.answer(f"🎉 На сегодня ({day}, {parity} неделя) пар нет!")
        return
        
    response_text = f"📚 Расписание на сегодня ({day}, {parity} неделя):\n\n"
    for time, subject, p_type in pairs:
        # Если пара идет каждую неделю, пометим её особо
        note = " (каждую неделю)" if p_type == "Обе" else ""
        response_text += f"⏰ {time} — {subject}{note}\n"
    
    await message.answer(response_text)


@dp.message(lambda message: message.text == "📝 Все пары")
async def get_all_schedule(message: types.Message):
    # Показываем отдельно обе недели, чтобы пользователю было удобно смотреть наперед
    all_days = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота"]
    
    response_text = "📋 Полное расписание по неделям:\n\n"
    
    for parity in ["Нечетная", "Четная"]:
        response_text += f"== 🏛️ {parity.upper()} НЕДЕЛЯ ==\n"
        has_pairs_in_week = False
        
        for day in all_days:
            pairs = get_schedule_by_day(day, parity)
            response_text += f"🔹 {day}:\n"
            if pairs:
                has_pairs_in_week = True
                for time, subject, _ in pairs:
                    response_text += f"  {time} — {subject}\n"
            else:
                response_text += " Пар нет\n"
            
    await message.answer(response_text)


@app.post("/tg-webhook")
async def telegram_webhook(request: Request):
    try:
        updates = await request.json()
        update = types.Update(**updates)
        await dp.feed_update(bot, update)
    except Exception as e:
        logging.error(f"Ошибка обработки вебхука: {e}")
    return {"status": "ok"}

@app.post("/generate-event")
async def external_event(request: Request):
    payload = await request.json()
    event_message = payload.get("event", "Произошло системное событие")
    all_users = get_all_users()
    for chat_id in all_users:
        try:
            await bot.send_message(chat_id=chat_id, text=f"⚠️ Важное уведомление:\n{event_message}")
        except Exception as e:
            logging.error(f"Ошибка отправки сообщения: {e}")
    return {"status": "event_delivered", "notified_users": len(all_users)}

@app.get("/")
def read_root():
    return {"status": "FastAPI is running successfully!"}


# Секретный ключ для защиты от спама (придумай любую строчку)
CRON_SECRET_TOKEN = "guap_practice_secret_2026"

@app.get("/send-morning-schedule")
async def send_morning_schedule(token: str = None):
    # Проверяем, что запрос пришел именно от нашего будильника
    if token != CRON_SECRET_TOKEN:
        return {"status": "error", "message": "Unauthorized"}
        
    day = get_russian_day()       # Определяем текущий день недели
    parity = get_current_parity() # Определяем чётность недели
    
    pairs = get_schedule_by_day(day, parity)
    
    if not pairs:
        message_text = f"☀️ Доброе утро! Сегодня {day} ({parity} неделя).\nПар нет, можно отдыхать! 🎉"
    else:
        message_text = f"☀️ Доброе утро! Твое расписание на сегодня ({day}, {parity} неделя):\n\n"
        for time, subject, p_type in pairs:
            note = " (каждую неделю)" if p_type == "Обе" else ""
            message_text += f"⏰ {time} — {subject}{note}\n"
            
    try:
        # Отправляем сообщение в твой личный чат Telegram
        await bot.send_message(chat_id=CHAT_ID, text=message_text)
        return {"status": "success", "message": "Morning schedule sent"}
    except Exception as e:
        logging.error(f"Ошибка утренней отправки: {e}")
        return {"status": "error", "message": str(e)}
