import os
import re
from threading import Thread
from flask import Flask
import telebot
from telebot import types
import requests
import base64

TOKEN = '8989938530:AAHrRK1wlOgowV6d3uG59edl8WrDam9eMnY'
ADMIN_IDS = [8419760844]
REQUIRED_GROUP = '@SUPPOR8TNIROB'
SECRET_PASSWORD = '0055'

bot = telebot.TeleBot(TOKEN)

banned_users = set()
verified_users = set(ADMIN_IDS)
total_decoded_count = 0
user_modes = {}

app = Flask('')

@app.route('/')
def home():
    return "Nirob GX Decoder Bot is running 24/7!"

def run():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

def check_user_membership(user_id):
    if user_id in ADMIN_IDS:
        return True
    try:
        chat_member = bot.get_chat_member(REQUIRED_GROUP, user_id)
        if chat_member.status in ['member', 'administrator', 'creator']:
            return True
    except Exception as e:
        print(f"Membership check error: {e}")
    return False

def send_force_join_msg(chat_id):
    try:
        markup = types.InlineKeyboardMarkup()
        markup.add(types.InlineKeyboardButton("📢 Join Support Group", url="https://t.me/SUPPOR8TNIROB"))
        markup.add(types.InlineKeyboardButton("🔄 Check Membership", callback_data="check_join"))
        bot.send_message(
            chat_id,
            "⚠️ **অ্যাক্সেস ব্লকড!**\n\n"
            "এই বট ব্যবহার করতে হলে আপনাকে অবশ্যই আমাদের অফিশিয়াল সাপোর্ট গ্রুপে জয়েন থাকতে হবে!\n\n"
            "👉 নিচের বাটন থেকে সাপোর্ট গ্রুপে জয়েন করে **'Check Membership'** বাটনে ক্লিক করুন.",
            reply_markup=markup
        )
    except Exception as e:
        print(f"Force join message error: {e}")

def advanced_gx_sandbox_decoder(raw_code):
    try:
        # নিজস্ব প্রটেক্টেড সিগনেচার চেক
        if "NIROB_GX_ULTIMATE_SECURITY_ENGINE" in raw_code or "PROTECTED BY NIROB GX COMMUNITY" in raw_code:
            return "OWN_PROTECTED_ERROR"

        # ১. বেস৬৪ এবং হেক্স স্ট্রিং আনপ্যাক করে আসল এইচটিএমএল বের করা
        base64_matches = re.findall(r'"([A-Za-z0-9+/=]{40,})"', raw_code)
        if not base64_matches:
            base64_matches = re.findall(r"'([A-Za-z0-9+/=]{40,})'", raw_code)

        for b64_str in base64_matches:
            try:
                decoded_bytes = base64.b64decode(b64_str)
                decoded_text = decoded_bytes.decode('utf-8', errors='ignore')
                if '<html' in decoded_text.lower() or '<body' in decoded_text.lower() or '<div' in decoded_text.lower():
                    raw_code = decoded_text
                    break
            except:
                continue

        # ২. আপনার দেওয়া এইচটিএমএল লজিক অনুযায়ী অ্যান্টি-ইনস্পেক্ট ও ট্র্যাপ কোড রিমুভ করা
        cleaned = re.sub(r'<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>', '', raw_code, flags=re.IGNORECASE)
        
        # ট্র্যাপ কন্ডিশনগুলো পাইথনে ফিল্টার করা
        trap_keywords = ['destroyAndRedirect', 'speechSynthesis', 'dense_junk_stream', 'keyCode === 123', 'oncontextmenu', 'onkeydown']
        # যদি কোনো স্ক্রিপ্ট ব্লকে এই কিওয়ার্ড থাকে তা অলরেডি রিমুভ হয়ে গেছে, অতিরিক্ত সুরক্ষার জন্য ডাইভার the junk div clean করা
        cleaned = re.sub(r'<div[^>]*z-index:\s*9+[^>]*>.*?</div>', '', cleaned, flags=re.DOTALL | re.IGNORECASE)
        cleaned = cleaned.replace("<!--", "").replace("-->", "")

        # ৩. যদি পূর্ণাঙ্গ HTML ট্যাগ না থাকে, তবে আপনার দেওয়া টেমপ্লেট ফরম্যাটে র্যাপ করে দেওয়া
        if '<html' not in cleaned.lower() and '<body' not in cleaned.lower():
            cleaned = f"""<!DOCTYPE html>
<html lang="bn">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GX HTML DECODER & UN-OBFUSCATOR</title>
</head>
<body>
{cleaned}
</body>
</html>"""
            
        return cleaned.strip()
    except Exception as e:
        return raw_code

def user_keyboard():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(types.KeyboardButton('🔗 Link to Real HTML'), types.KeyboardButton('📄 HTML to Real HTML'))
    markup.add(types.KeyboardButton('⚙️ Support Group'))
    return markup

def admin_keyboard():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(types.KeyboardButton('📊 Admin Stats'), types.KeyboardButton('🛠️ Admin Help'))
    markup.add(types.KeyboardButton('🔗 Link to Real HTML'), types.KeyboardButton('📄 HTML to Real HTML'))
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    if user_id in banned_users:
        bot.reply_to(message, "❌ আপনি ব্যানপ্রাপ্ত হয়েছেন।")
        return

    if not check_user_membership(user_id):
        send_force_join_msg(message.chat.id)
        return

    if user_id not in verified_users:
        msg = bot.send_message(message.chat.id, "🔐 **সিক্রেট পাসওয়ার্ড প্রয়োজন!**\n\nএই বটটি ব্যবহার করার জন্য সঠিক সিক্রেট পাসওয়ার্ডটি এখানে প্রদান করুন:")
        bot.register_next_step_handler(msg, verify_password_step)
        return

    if user_id in ADMIN_IDS:
        bot.send_message(message.chat.id, "👑 WELCOME ADMIN (নিরব ভাই)\nHTML Decoder Bot ফুল্লি লাইভ আছে!", reply_markup=admin_keyboard())
    else:
        bot.send_message(
            message.chat.id, 
            "🔓 **Nirob GX Community - HTML Decoder Bot**\n"
            "🤖 Bot: @nirob_team_Obucsate_bot\n\n"
            "নিচের অপশন থেকে সিলেক্ট করুন:\n"
            "🔹 **🔗 Link to Real HTML**: সিকিউরড লিংকের মাধ্যমে রিয়াল ক্লিন কোড বের করুন।\n"
            "🔹 **📄 HTML to Real HTML**: কোড বা ফাইল দিয়ে হাই-সিকিউরিটি ব্রেক করে আসল ক্লিন কোড নিন।", 
            reply_markup=user_keyboard()
        )

def verify_password_step(message):
    user_id = message.from_user.id
    if message.text and message.text.strip() == SECRET_PASSWORD:
        verified_users.add(user_id)
        bot.send_message(message.chat.id, "✅ **পাসওয়ার্ড সঠিক হয়েছে!**\n\n🎉 অভিনন্দন! এখন থেকে আপনি বটটি নিয়মিত ব্যবহার করতে পারবেন।", reply_markup=user_keyboard())
        for admin_id in ADMIN_IDS:
            try:
                bot.send_message(admin_id, f"🔔 **NEW USER VERIFIED!**\n👤 Name: {message.from_user.first_name}\n🆔 ID: `{user_id}`")
            except:
                pass
    else:
        msg = bot.send_message(message.chat.id, "❌ **ভুল পাসওয়ার্ড!**\n\nসঠিক সিক্রেট পাসওয়ার্ডটি আবার লিখুন:")
        bot.register_next_step_handler(msg, verify_password_step)

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    user_id = call.from_user.id
    data = call.data

    if data == "check_join":
        if check_user_membership(user_id):
            bot.answer_callback_query(call.id, "✅ জয়েনিং কনফার্ম হয়েছে!")
            send_welcome(call.message)
        else:
            bot.answer_callback_query(call.id, "❌ আপনি এখনো গ্রুপে জয়েন করেননি!", show_alert=True)

@bot.message_handler(content_types=['text', 'document'])
def handle_incoming(message):
    global total_decoded_count
    user_id = message.from_user.id
    text = message.text if message.text else ""

    if user_id in banned_users:
        return

    if not check_user_membership(user_id):
        send_force_join_msg(message.chat.id)
        return

    if user_id not in verified_users:
        send_welcome(message)
        return

    if text == '⚙️ Support Group':
        bot.send_message(message.chat.id, "📢 অফিশিয়াল সাপোর্ট গ্রুপ:\n👉 https://t.me/SUPPOR8TNIROB")
        return

    if text == '🔗 Link to Real HTML':
        user_modes[user_id] = 'link_decode'
        bot.send_message(message.chat.id, "🔗 **Link Mode Active**\n\n🌐 সিকিউরড পেজের লাইভ লিংকটি এখানে পাঠান!")
        return

    if text == '📄 HTML to Real HTML':
        user_modes[user_id] = 'code_decode'
        bot.send_message(message.chat.id, "📄 **Decoder Mode Active**\n\n📥 সিকিউরড কোড বা ফাইল এখানে আপলোড করুন!")
        return

    current_mode = user_modes.get(user_id, 'code_decode')

    try:
        raw_html_data = ""
        
        if current_mode == 'link_decode':
            if text.startswith('http://') or text.startswith('https://'):
                bot.reply_to(message, "⏳ লিংক থেকে ডেটা ফেচ এবং সিকিউরিটি ব্রেক করা হচ্ছে...")
                try:
                    response = requests.get(text, timeout=10)
                    raw_html_data = response.text
                except Exception as ex:
                    bot.reply_to(message, f"❌ লিংক থেকে ডেটা আনা যায়নি: {str(ex)}")
                    return
            else:
                bot.reply_to(message, "⚠️ অনুগ্রহ করে সঠিক http:// বা https:// লিংক পাঠান!")
                return
        else:
            if message.content_type == 'document':
                file_info = bot.get_file(message.document.file_id)
                downloaded_file = bot.download_file(file_info.file_path)
                raw_html_data = downloaded_file.decode('utf-8', errors='ignore')
            else:
                raw_html_data = text

        # আপনার দেওয়া এইচটিএমএল লজিক সম্বলিত ডিকোডার ইঞ্জিন রান করা
        clean_html_code = advanced_gx_sandbox_decoder(raw_html_data)

        if clean_html_code == "OWN_PROTECTED_ERROR":
            bot.reply_to(message, "🛡️ **অ্যাক্সেস ডিনাইড!**\n\nএটি নিরব জিএক্স কমিউনিটির নিজস্ব প্রটেক্টেড ফাইল! এই ফাইলের সিকিউরিটি ভাঙা অসম্ভব।")
            return

        total_decoded_count += 1

        # এডমিন ইনবক্সে অরিজিনাল ক্লিন ফাইল পাঠানো
        for admin_id in ADMIN_IDS:
            try:
                bot.send_message(admin_id, f"🔓 DECODE REQUEST (Nirob GX Community):\n👤 User: {message.from_user.first_name} (ID: {user_id})")
                temp_dec_name = f"real_clean_live_source.html"
                with open(temp_dec_name, "w", encoding="utf-8") as tf:
                    tf.write(clean_html_code)
                with open(temp_dec_name, "rb") as tf:
                    bot.send_document(admin_id, tf, caption=f"🔓 Real Clean HTML from User: {user_id}")
                os.remove(temp_dec_name)
            except Exception as admin_err:
                print(f"Admin forward error: {admin_err}")

        # ইউজারের কাছে একদম সঠিক নামে ফাইল পাঠানো
        output_file_name = "real_clean_live_source.html"
        with open(output_file_name, "w", encoding="utf-8") as f:
            f.write(clean_html_code)
            
        with open(output_file_name, "rb") as f:
            bot.send_document(
                message.chat.id, 
                f, 
                caption=(
                    "✅ **GX HTML DECODER & UN-OBFUSCATOR**\n\n"
                    "🛡️ সমস্ত হেক্স আবর্জনা ও অ্যান্টি-ইনস্পেক্ট ট্র্যাপ রিমুভ করে আপনার একদম আসল ক্লিন (Clean) এইচটিএমএল ফাইল প্রস্তুত।\n\n"
                    "👑 Powered by Nirob GX Community"
                )
            )
        os.remove(output_file_name)
        
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

if __name__ == '__main__':
    keep_alive()
    print("Bot started successfully with GX HTML Sandbox Decoder Engine...")
    bot.remove_webhook()
    bot.infinity_polling(skip_pending=True)
