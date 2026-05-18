import logging
from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from database import init_db, get_schedule_by_day

# Включаем логирование, чтобы видеть всё в панели Render
logging.basicConfig(level=logging.INFO)

TELEGRAM_TOKEN = "8995925816:AAGKPuDuRdEgtlMycIkW84ctaje2KYhEX1o"
CHAT_ID = 1333034189

# Инициализируем FastAPI, Bot и современный Dispatcher
app = FastAPI()
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

# Принудительно создаем и заполняем базу данных SQLite при импорте/старте
init_db()

# Создаем красивую клавиатуру для aiogram 3.x
menu_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📅 Расписание на сегодня")],
        [KeyboardButton(text="📝 Все пары")]
    ],
    resize_keyboard=True
)

# Исправленный обработчик команды /start для aiogram 3.x (через магический фильтр)
@dp.message(lambda message: message.text == "/start")
async def cmd_start(message: types.Message):
    await message.answer(
        f"Привет, {message.from_user.first_name}! Бот системы расписания ГУАП готов к работе.",
        reply_markup=menu_keyboard
    )

# Обработчик кнопки расписания
@dp.message(lambda message: message.text == "📅 Расписание на сегодня")
async def get_today_schedule(message: types.Message):
    day = "Понедельник"  # Тестовый день
    pairs = get_schedule_by_day(day)
    
    if not pairs:
        await message.answer(f"🎉 На {day} пар нет!")
        return
        
    response_text = f"📚 Расписание на {day}:\n\n"
    for time, subject in pairs:
        response_text += f"⏰ {time} — {subject}\n"
    
    await message.answer(response_text)

# Кнопка "Все пары"
@dp.message(lambda message: message.text == "📝 Все пары")
async def get_all_schedule(message: types.Message):
    all_days = ["Понедельник", "Вторник", "Среда"]
    response_text = "📋 Полное расписание:\n\n"
    
    for day in all_days:
        pairs = get_schedule_by_day(day)
        if pairs:
            response_text += f"🔹 {day}:\n"
            for time, subject in pairs:
                response_text += f"  {time} — {subject}\n"
            response_text += "\n"
            
    await message.answer(response_text)

# Хэндлер вебхука от Telegram
@app.post("/tg-webhook")
async def telegram_webhook(request: Request):
    try:
        updates = await request.json()
        update = types.Update(**updates)
        await dp.feed_update(bot, update)
    except Exception as e:
        logging.error(f"Ошибка обработки вебхука: {e}")
    return {"status": "ok"}

# Хэндлер генерации внешних событий (для индивидуального задания)
@app.post("/generate-event")
async def external_event(request: Request):
    payload = await request.json()
    event_message = payload.get("event", "Произошло системное событие")
    
    try:
        await bot.send_message(chat_id=CHAT_ID, text=f"⚠️ Системное уведомление:\n{event_message}")
    except Exception as e:
        logging.error(f"Ошибка отправки сообщения: {e}")
        
    return {"status": "event_delivered"}

# Короткий проверочный роут, чтобы проверять сервер в браузере
@app.get("/")
def read_root():
    return {"status": "FastAPI is running successfully!"}
