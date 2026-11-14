import os
import time
import threading
import telebot
from telebot import types

TOKEN = os.environ.get("BOT_TOKEN")
ADMIN_ID = 6144650191

bot = telebot.TeleBot(TOKEN)

# Умный поиск файлов (найдёт файл даже если буквы .MP3 / .MP4 заглавные или в формате .ogg)
def find_media(path):
    if os.path.exists(path):
        return path
    base, _ = os.path.splitext(path)
    for ext in ['.mp3', '.MP3', '.ogg', '.OGG', '.mp4', '.MP4', '.mov', '.MOV']:
        if os.path.exists(base + ext):
            return base + ext
    return path

# Вспомогательные функции для нагнетания жути
def send_typing(chat_id, text, delay=3):
    bot.send_chat_action(chat_id, 'typing')
    time.sleep(delay)
    bot.send_message(chat_id, text, parse_mode="Markdown")

def send_scary_voice(chat_id, file_path, delay=4):
    bot.send_chat_action(chat_id, 'record_voice')
    time.sleep(delay)
    real_path = find_media(file_path)
    with open(real_path, 'rb') as audio:
        bot.send_voice(chat_id, audio)

# 1. Команда /start — уведомляем админа и кидаем дисклеймер
@bot.message_handler(commands=['start'])
def start(message):
    user = message.from_user
    username = f"@{user.username}" if user.username else f"id: {user.id} (нет ника)"
    
    # Отправляем тебе в личку отчёт о новом игроке
    try:
        bot.send_message(
            ADMIN_ID,
            f"👁 **Новая жертва зашла в хоррор-бот!**\n\n"
            f"👤 **Имя:** {user.first_name}\n"
            f"🔗 **Профиль:** {username}",
            parse_mode="Markdown"
        )
    except Exception:
        pass

    markup = types.InlineKeyboardMarkup(row_width=1)
    btn_start = types.InlineKeyboardButton("💀 Я готов(а). Начать квест", callback_data="act_1")
    btn_exit = types.InlineKeyboardButton("🚪 Я боюсь, выйти", callback_data="exit_game")
    markup.add(btn_start, btn_exit)

    warning_text = (
        "⚠️ **ВНИМАНИЕ! СТРОГО 18+ / НЕ ДЛЯ СЛАБОНЕРВНЫХ!**\n\n"
        "В этом квесте используются пугающие звуки и резкие видео. "
        "Не рекомендуется людям со слабой психикой и проблемами с сердцем.\n\n"
        "🎧 **Для полного погружения:**\n"
        "1. Наденьте наушники.\n"
        "2. Выключите свет в комнате.\n"
        "3. Сделайте громкость на 80%.\n\n"
        "Вы уверены, что хотите продолжить?"
    )
    bot.send_message(message.chat.id, warning_text, parse_mode="Markdown", reply_markup=markup)

# Выход, если человек испугался сразу
@bot.callback_query_handler(func=lambda call: call.data == "exit_game")
def handle_exit(call):
    bot.answer_callback_query(call.id)
    bot.edit_message_text(
        "🚪 Правильное решение. Некоторым дверям лучше оставаться закрытыми...",
        chat_id=call.message.chat.id,
        message_id=call.message.message_id
    )

# АКТ 1: Иллюзия слежки
def run_act_1(chat_id, first_name):
    send_typing(chat_id, "Хорошо. Только не сворачивай этот чат...", 3)
    send_typing(chat_id, "`[Система]: Подключение к фронтальной камере...`", 3)
    send_typing(chat_id, "`[Система]: Микрофон активен. Геолокация определена.`", 4)
    send_typing(chat_id, f"Я вижу тебя, **{first_name}**.", 4)
    
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("🏢 1–3 этаж", callback_data="floor_low"),
        types.InlineKeyboardButton("🏢 4–9 этаж", callback_data="floor_high"),
        types.InlineKeyboardButton("🏙 Выше 9-го этажа", callback_data="floor_high")
    )
    bot.send_chat_action(chat_id, 'typing')
    time.sleep(3)
    bot.send_message(chat_id, "На каком этаже ты сейчас находишься?", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "act_1")
def handle_act_1(call):
    bot.answer_callback_query(call.id)
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    threading.Thread(target=run_act_1, args=(call.message.chat.id, call.from_user.first_name)).start()

# АКТ 2: Шаги в подъезде + Голосовое №1
def run_act_2(chat_id, floor_type):
    if floor_type == "floor_low":
        send_typing(chat_id, "Отлично. До твоего окна легко дотянуться с улицы...", 3)
    else:
        send_typing(chat_id, "Высоко... Но через подъезд я поднимусь очень быстро.", 3)
        
    send_typing(chat_id, "Я уже зашёл в твой подъезд.", 4)
    send_typing(chat_id, "Прислушайся. Слышишь?", 3)
    
    # Отправляем первый звук (voice1.mp3)
    send_scary_voice(chat_id, "media/voice.mp3.mp3", 5)
    
    time.sleep(4)
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(
        types.InlineKeyboardButton("👀 Посмотреть в глазок", callback_data="door_peek"),
        types.InlineKeyboardButton("🙈 Спрятаться в комнате", callback_data="door_hide")
    )
    send_typing(chat_id, "Я стою прямо перед твоей входной дверью. Что будешь делать?", 4)
    bot.send_message(chat_id, "Выбирай быстрее:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("floor_"))
def handle_act_2(call):
    bot.answer_callback_query(call.id)
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    threading.Thread(target=run_act_2, args=(call.message.chat.id, call.data)).start()

# АКТ 3: Проникновение + Голосовое №2 + Финальный Скример
def run_act_3(chat_id, choice, user):
    if choice == "door_peek":
        send_typing(chat_id, "Никого нет на площадке? Конечно...", 3)
        send_typing(chat_id, "Потому что я зашёл в квартиру 5 минут назад, пока ты отвлекался.", 4)
    else:
        send_typing(chat_id, "Ты правда думаешь, что межкомнатная дверь меня остановит?", 4)

    send_typing(chat_id, "Посмотри в тёмный угол своей комнаты. Или под кровать.", 4)
    
    # Отправляем второй звук (voice2.mp3)
    send_scary_voice(chat_id, "media/voice2.mp3.mp3", 4)
    
    time.sleep(5)
    send_typing(chat_id, "Не оборачивайся. Просто посчитай вместе со мной...", 3)
    send_typing(chat_id, "**Раз...**", 2)
    send_typing(chat_id, "**Два...**", 2)
    send_typing(chat_id, "**ТРИ!**", 2)
    
    # Отправляем финальный видео-скример (screamer.mp4)
    time.sleep(1)
    bot.send_chat_action(chat_id, 'upload_video')
    video_path = find_media("media/screamer.mp4.mp4")
    with open(video_path, 'rb') as video:
        bot.send_video(chat_id, video)
        
    # Пауза после скримера и финал
    time.sleep(7)
    bot_username = bot.get_me().username
    share_url = f"https://t.me{bot_username}&text=Рискнёшь%20пройти%20этот%20хоррор-квест%20в%20наушниках%20и%20темноте%3F%20💀"
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("😱 Переслать другу (проверить его нервы)", url=share_url))
    
    bot.send_message(
        chat_id,
        "😈 **Фух, живой?**\n\nТы прошёл квест до самого конца! Отправь этого бота друзьям — посмотрим, как испугаются они 👇",
        parse_mode="Markdown",
        reply_markup=markup
    )
    
    # Сообщаем тебе в личку, что жертва дошла до скримера
    try:
        username = f"@{user.username}" if user.username else f"id: {user.id}"
        bot.send_message(ADMIN_ID, f"💀 **Жертва {user.first_name} ({username}) дошла до финального скримера!**", parse_mode="Markdown")
    except Exception:
        pass

@bot.callback_query_handler(func=lambda call: call.data.startswith("door_"))
def handle_act_3(call):
    bot.answer_callback_query(call.id)
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
    threading.Thread(target=run_act_3, args=(call.message.chat.id, call.data, call.from_user)).start()

print("Хоррор-бот запущен...")
bot.infinity_polling()
