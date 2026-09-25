import telebot
from telebot import types
import json
import os

# ضع التوكن الخاص ببوتك هنا (احصل عليه من BotFather)
API_TOKEN = '8817045687:AAEMQb2is1q_GMCZhNGG75cIr9sx0iyfvTE'
# ضع الأي دي الخاص بحسابك على تليجرام هنا لتكون أنت فقط من يتحكم بالبوت
ADMIN_ID = 1754353018 

bot = telebot.TeleBot(API_TOKEN)
CHANNELS_FILE = 'channels.json'
USER_STATE = {}

def load_channels():
    if os.path.exists(CHANNELS_FILE):
        with open(CHANNELS_FILE, 'r') as f:
            try:
                return json.load(f)
            except:
                return []
    return []

def save_channels(channels):
    with open(CHANNELS_FILE, 'w') as f:
        json.dump(channels, f)

# التقط القنوات تلقائياً عند إضافة البوت كمشرف
@bot.my_chat_member_handler()
def handle_left_or_joined_channel(update):
    channels = load_channels()
    chat = update.chat
    status = update.new_chat_member.status
    
    if chat.type in ['channel']:
        if status in ['administrator']:
            if chat.id not in channels:
                channels.append(chat.id)
                save_channels(channels)
                bot.send_message(ADMIN_ID, f"✅ تم إضافة البوت بنجاح لقناة: {chat.title}")
        elif status in ['left', 'kicked']:
            if chat.id in channels:
                channels.remove(chat.id)
                save_channels(channels)
                bot.send_message(ADMIN_ID, f"❌ تم إزالة البوت من قناة: {chat.title}")

# لوحة تحكم الآدمن
@bot.message_handler(commands=['start', 'panel'])
def send_welcome(message):
    if message.from_user.id == ADMIN_ID:
        channels = load_channels()
        bot.reply_to(message, f"👋 أهلاً بك يا مطور البوت.\n👥 عدد القنوات المشتركة حالياً: {len(channels)}\n\n💡 **لإرسال منشور دعم:**\nاضغط على زر 'إنشاء منشور دعم' بالأسفل.")
        
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        markup.add(types.KeyboardButton("📝 إنشاء منشور دعم"))
        bot.send_message(message.chat.id, "اختر من القائمة المساعدة:", reply_markup=markup)

# بدء عملية إنشاء المنشور
@bot.message_handler(func=lambda message: message.from_user.id == ADMIN_ID and message.text == "📝 إنشاء منشور دعم")
def start_post(message):
    USER_STATE[message.from_user.id] = {'text': '', 'buttons': []}
    bot.send_message(message.chat.id, "✍️ أرسل الآن نص المنشور (سطر الكلام الترحيبي الذي سيظهر أعلى الزر):")

# استقبال نص المنشور
@bot.message_handler(func=lambda message: message.from_user.id == ADMIN_ID and USER_STATE.get(message.from_user.id) and USER_STATE[message.from_user.id]['text'] == '')
def get_post_text(message):
    USER_STATE[message.from_user.id]['text'] = message.text
    bot.send_message(message.chat.id, "🔗 الآن أرسل اسم الزر ورابطه بهذه الصيغة:\n`اسم الزر - الرابط`\n\nمثال:\nاضغط هنا للاشتراك - https://t.me")

# استقبال الأزرار ونشر الدعم
@bot.message_handler(func=lambda message: message.from_user.id == ADMIN_ID and USER_STATE.get(message.from_user.id) and USER_STATE[message.from_user.id]['text'] != '')
def get_buttons_and_send(message):
    state = USER_STATE[message.from_user.id]
    lines = message.text.split('\n')
    
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    buttons_list = []
    
    for line in lines:
        if '-' in line:
            parts = line.split('-')
            name = parts[0].strip()
            url = parts[1].strip()
            if url.startswith('http'):
                buttons_list.append(types.InlineKeyboardButton(text=name, url=url))
    
    keyboard.add(*buttons_list)
    
    # نشر المنشور في القنوات
    channels = load_channels()
    success_count = 0
    
    for channel_id in channels:
        try:
            bot.send_message(chat_id=channel_id, text=state['text'], reply_markup=keyboard)
            success_count += 1
        except Exception as e:
            pass
            
    bot.send_message(message.chat.id, f"📢 تم نشر المنشور والزر الشفاف بنجاح في {success_count} قناة من أصل {len(channels)}.")
    del USER_STATE[message.from_user.id] # تفريغ الذاكرة

bot.infinity_polling()
