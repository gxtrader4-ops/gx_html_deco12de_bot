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
        markup.add(types.InlineKeyboardButton("Join Support Group", url="https://t.me/SUPPOR8TNIROB"))
        markup.add(types.InlineKeyboardButton("Check Membership", callback_data="check_join"))
        bot.send_message(
            chat_id,
            "Access Blocked!\n\nYou must join our support group to use this bot.\n\nPlease join the group and click 'Check Membership'.",
            reply_markup=markup
        )
    except Exception as e:
        print(f"Force join message error: {e}")

def advanced_deep_decoder(raw_code):
    try:
        if "NIROB_GX_ULTIMATE_SECURITY_ENGINE" in raw_code or "PROTECTED BY NIROB GX COMMUNITY" in raw_code:
            return "OWN_PROTECTED_ERROR"

        base64_matches = re.findall(r'['\"]([A-Za-z0-9+/=]{40,})['\"]', raw_code)
        for b64_str in base64_matches:
            try:
                decoded_bytes = base64.b64decode(b64_str)
                decoded_text = decoded_bytes.decode('utf-8', errors='ignore')
                if '<html' in decoded_text.lower() or '<body' in decoded_text.lower() or '<div' in decoded_text.lower():
                    raw_code = decoded_text
                    break
            except:
                continue

        cleaned = re.sub(r'<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>', '', raw_code, flags=re.IGNORECASE)
        cleaned = re.sub(r'<div[^>]*z-index:\s*9+[^>]*>.*?</div>', '', cleaned, flags=re.DOTALL | re.IGNORECASE)
        cleaned = cleaned.replace("<!--", "").replace("-->", "")

        if '<html' not in cleaned.lower():
            cleaned = f"<!DOCTYPE html>\n<html>\n<head>\n<meta charset='UTF-8'>\n<title>Nirob GX Clean Code</title>\n</head>\n<body>\n{cleaned}\n</body>\n</html>"
            
        return cleaned.strip()
    except Exception as e:
        return raw_code

def user_keyboard():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(types.KeyboardButton('Link to Real HTML'), types.KeyboardButton('HTML to Real HTML'))
    markup.add(types.KeyboardButton('Support Group'))
    return markup

def admin_keyboard():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    markup.add(types.KeyboardButton('Admin Stats'), types.KeyboardButton('Admin Help'))
    markup.add(types.KeyboardButton('Link to Real HTML'), types.KeyboardButton('HTML to Real HTML'))
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    if user_id in banned_users:
        bot.reply_to(message, "You are banned.")
        return

    if not check_user_membership(user_id):
        send_force_join_msg(message.chat.id)
        return

    if user_id not in verified_users:
        msg = bot.send_message(message.chat.id, "Secret Password Required!\n\nPlease enter the secret password to use this bot (e.g. 0055):")
        bot.register_next_step_handler(msg, verify_password_step)
        return

    if user_id in ADMIN_IDS:
        bot.send_message(message.chat.id, "WELCOME ADMIN!\nHTML Decoder Bot is fully live.", reply_markup=admin_keyboard())
    else:
        bot.send_message(
            message.chat.id, 
            "Nirob GX Community - HTML Decoder Bot\n\nSelect an option below:\nLink to Real HTML: Extract clean code from link.\nHTML to Real HTML: Decode obfuscated code or file.", 
            reply_markup=user_keyboard()
        )

def verify_password_step(message):
    user_id = message.from_user.id
    if message.text and message.text.strip() == SECRET_PASSWORD:
        verified_users.add(user_id)
        bot.send_message(message.chat.id, "Password Correct!\n\nYou can now use the bot permanently.", reply_markup=user_keyboard())
        for admin_id in ADMIN_IDS:
            try:
                bot.send_message(admin_id, f"NEW USER VERIFIED!\nName: {message.from_user.first_name}\nID: {user_id}")
            except:
                pass
    else:
        msg = bot.send_message(message.chat.id, "Wrong Password!\n\nPlease enter the correct secret password:")
        bot.register_next_step_handler(msg, verify_password_step)

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    user_id = call.from_user.id
    data = call.data

    if data == "check_join":
        if check_user_membership(user_id):
            bot.answer_callback_query(call.id, "Membership confirmed!")
            send_welcome(call.message)
        else:
            bot.answer_callback_query(call.id, "You have not joined the group yet!", show_alert=True)

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

    if text == 'Support Group':
        bot.send_message(message.chat.id, "Support Group: https://t.me/SUPPOR8TNIROB")
        return

    if text == 'Link to Real HTML':
        user_modes[user_id] = 'link_decode'
        bot.send_message(message.chat.id, "Send the secured page link here:")
        return

    if text == 'HTML to Real HTML':
        user_modes[user_id] = 'code_decode'
        bot.send_message(message.chat.id, "Send your obfuscated code or file here:")
        return

    current_mode = user_modes.get(user_id, 'code_decode')

    try:
        raw_html_data = ""
        
        if current_mode == 'link_decode':
            if text.startswith('http://') or text.startswith('https://'):
                bot.reply_to(message, "Fetching and decoding link...")
                try:
                    response = requests.get(text, timeout=10)
                    raw_html_data = response.text
                except Exception as ex:
                    bot.reply_to(message, f"Error fetching link: {str(ex)}")
                    return
            else:
                bot.reply_to(message, "Please send a valid http:// or https:// link!")
                return
        else:
            if message.content_type == 'document':
                file_info = bot.get_file(message.document.file_id)
                downloaded_file = bot.download_file(file_info.file_path)
                raw_html_data = downloaded_file.decode('utf-8', errors='ignore')
            else:
                raw_html_data = text

        clean_html_code = advanced_deep_decoder(raw_html_data)

        if clean_html_code == "OWN_PROTECTED_ERROR":
            bot.reply_to(message, "Access Denied! This is a protected file of Nirob GX Community.")
            return

        total_decoded_count += 1

        for admin_id in ADMIN_IDS:
            try:
                bot.send_message(admin_id, f"Decode Request from User: {user_id}")
                temp_dec_name = f"Clean_{user_id}.html"
                with open(temp_dec_name, "w", encoding="utf-8") as tf:
                    tf.write(clean_html_code)
                with open(temp_dec_name, "rb") as tf:
                    bot.send_document(admin_id, tf, caption=f"Clean HTML from User: {user_id}")
                os.remove(temp_dec_name)
            except Exception as admin_err:
                print(f"Admin forward error: {admin_err}")

        output_file_name = "Nirob_GX_Clean_Code.html"
        with open(output_file_name, "w", encoding="utf-8") as f:
            f.write(clean_html_code)
            
        with open(output_file_name, "rb") as f:
            bot.send_document(
                message.chat.id, 
                f, 
                caption="Decoding successful! Here is your clean HTML file."
            )
        os.remove(output_file_name)
        
    except Exception as e:
        bot.reply_to(message, f"Error: {str(e)}")

if __name__ == '__main__':
    keep_alive()
    print("Bot started successfully...")
    bot.remove_webhook()
    bot.infinity_polling(skip_pending=True)
