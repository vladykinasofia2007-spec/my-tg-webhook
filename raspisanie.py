from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# === НАСТРОЙКИ (Вставь сюда свои данные) ===
TELEGRAM_TOKEN = "8995925816:AAGKPuDuRdEgtlMycIkW84ctaje2KYhEX1o"
CHAT_ID = "1333034189"


# Функция, которая отправляет сообщение в твой Telegram
def send_to_telegram(message_text):
    TELEGRAM_TOKEN = "8995925816:AAGKPuDuRdEgtlMycIkW84ctaje2KYhEX1o"
    
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    
    payload = {
        "chat_id": 1333034189,  # Твой ID цифрами без кавычек
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
    data = request.get_json()
    print(f"Получены данные: {data}")
    
    # Извлекаем текст события, если он есть
    event_text = data.get('event', 'Без описания')
    
    # Формируем текст для Telegram
    text_to_send = f"⚠️ Новое событие!\n{event_text}"
    
    # ВНИМАНИЕ: Вызываем отправку
    send_to_telegram(text_to_send)
    
    return {"status": "success"}, 200


# Запуск нашего мини-сервера на порту 5000
if __name__ == '__main__':
    app.run(port=5000)
