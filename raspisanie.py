from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
import uvicorn
from database import init_db, get_schedule_by_day

# Токены и конфигурация
TELEGRAM_TOKEN = "8995925816:AAGKPuDuRdEgtlMycIkW84ctaje2KYhEX1o"
CHAT_ID = 1333034189  # Твой ID для системных уведомлений

# Инициализируем FastAPI, Bot и Dispatcher (aiogram)
app = FastAPI()
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

# Инициализируем базу данных при старте
init_db()

# Создаем клавиатуру для бота
menu_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📅 Расписание на сегодня")],
        [KeyboardButton(text="📝 Все пары")]
    ],
    resize_keyboard=True
)


# Обычный обработчик команды /start внутри Telegram
@dp.message(commands=["start"])
async def cmd_start(message: types.Message):
    await message.answer(
        f"Привет, {message.from_user.first_name}! Я бот твоей системы расписания.",
        reply_markup=menu_keyboard
    )


# Обработчик кнопки расписания
@dp.message(lambda message: message.text == "📅 Расписание на сегодня")
async def get_today_schedule(message: types.Message):
    # Для примера возьмем Понедельник, в реальном коде можно использовать datetime
    day = "Понедельник"
    pairs = get_schedule_by_day(day)

    if not pairs:
        await message.answer(f"🎉 На {day} пар нет, можно отдыхать!")
        return

    response_text = f"📚 Расписание на {day}:\n"
    for time, subject in pairs:
        response_text += f"⏰ {time} — {subject}\n"

    await message.answer(response_text)


# ВЕБХУК 1: Для самого Telegram (чтобы aiogram получал клики по кнопкам в облаке)
@app.post("/tg-webhook")
async def telegram_webhook(request: Request):
    updates = await request.json()
    update = types.Update(**updates)
    await dp.feed_update(bot, update)
    return {"status": "ok"}


# ВЕБХУК 2: Для генерации внешних событий (как требует задание: HTTP-запросы для генерации событий)
@app.post("/generate-event")
async def external_event(request: Request):
    payload = await request.json()
    event_message = payload.get("event", "Произошло неопознанное событие")

    # Отправляем экстренное уведомление в Telegram через бота
    await bot.send_message(chat_id=CHAT_ID, text=f"⚠️ Внешнее системное уведомление:\n{event_message}")
    return {"status": "event_delivered"}


if name == "__main__":
    # Запуск локально для тестов
    uvicorn.run("main.py:app", host="0.0.0.0", port=10000, reload=True)
