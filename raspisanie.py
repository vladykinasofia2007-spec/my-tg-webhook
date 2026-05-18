from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# === НАСТРОЙКИ (Вставь сюда свои данные) ===
TELEGRAM_TOKEN = "8995925816:AAGKPuDuRdEgtlMycIkW84ctaje2KYhEX1o"
CHAT_ID = "1333034189"


# Функция, которая отправляет сообщение в твой Telegram
def send_to_telegram(message_text):
    # Убедись, что твои CHAT_ID и TELEGRAM_TOKEN скопированы сюда правильно!
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "CHAT_ID": 1333034189,
        "text": message_text
    }
    try:
        response = requests.post(url, json=payload)
        print(f"Telegram response: {response.status_code} - {response.text}")
        return response
    except Exception as e:
        print(f"Ошибка при отправке в Telegram: {e}")
        return None


# Создаем "точку ожидания" для вебхука. Наш адрес будет заканчиваться на /webhook
@app.route('/webhook', methods=['POST'])
def receive_webhook():
    # Программа берет данные, которые пришли из интернета
    data = request.json
    print("Получены данные:", data)  # Выведет данные в консоль, чтобы ты видел

    # Ищем в пришедших данных текст события
    # Мы ожидаем формат: {"event": "Текст вашего уведомления"}
    if data and 'event' in data:
        event_text = data['event']
        # Вызываем функцию отправки в Telegram
        send_to_telegram(f"🔔 Новое событие!\n{event_text}")
        return jsonify({"status": "success"}), 200
    else:
        return jsonify({"status": "error", "message": "Неверный формат данных"}), 400


# Запуск нашего мини-сервера на порту 5000
if __name__ == '__main__':
    app.run(port=5000)
