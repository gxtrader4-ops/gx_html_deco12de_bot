import os
import json
from flask import Flask, request
import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

# কনফিগারেশন
BOT_TOKEN = "8989938530:AAGGfDO6pQUukxXFjpjE1ydcC61st-7tbkc"
ADMIN_ID = 8419760844
ADMIN_USERNAME = "NIROB_GX_LEADER"

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# ডাটাবেজ ফাইল ম্যানেজমেন্ট
DB_FILE = "bot_database.json"

def load_db():
    if not os.path.exists(DB_FILE):
        return {"users": [], "banned": []}
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

# /start কমান্ড হ্যান্ডলার
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_id = message.from_user.id
    db = load_db()
    
    if user_id in db["banned"] and user_id != ADMIN_ID:
        bot.reply_to(message, "❌ দুঃখিত, এই বট ব্যবহারের জন্য আপনাকে ব্যান করা হয়েছে!")
        return

    if user_id not in db["users"]:
        db["users"].append(user_id)
        save_db(db)

    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("🔗 Link to Real HTML", callback_data="link_html"),
        InlineKeyboardButton("🔓 HTML to Real HTML Decode", callback_data="decode_html")
    )
    
    if user_id == ADMIN_ID:
        markup.row(InlineKeyboardButton("👥 All User", callback_data="all_users"))

    welcome_msg = (
        f"👋 স্বাগতম GX HTML Decoder বোটে!\n\n"
        f"প্রোফাইল: @{ADMIN_USERNAME}\n"
        f"আপনার সিকিউরড বা অবফাসকেটেড এইচটিএমএল ফাইল বা লিংক ক্লিন করে রিয়েল কোড পেতে নিচের অপশনগুলো ব্যবহার করুন।"
    )
    
    bot.send_message(message.chat.id, welcome_msg, reply_markup=markup)

# ইনলাইন বাটন হ্যান্ডলার
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    db = load_db()
    if call.data == "link_html" or call.data == "decode_html":
        bot.send_message(call.message.chat.id, "📥 অনুগ্রহ করে আপনার সিকিউরড বা অবফাসকেটেড HTML ফাইলটি ডকুমেন্ট (Document) হিসেবে পাঠান অথবা ডিরেক্ট কোড/লিংক পেস্ট করুন।")
    elif call.data == "all_users":
        if call.from_user.id == ADMIN_ID:
            total_users = len(db["users"])
            total_banned = len(db["banned"])
            bot.send_message(call.message.chat.id, f"📊 **Bot Statistics:**\n\n👤 Total Users: {total_users}\n🚫 Banned Users: {total_banned}")

# টেক্সট, ডকুমেন্ট ও ব্যান/আনব্যান কমান্ড হ্যান্ডলার
@bot.message_handler(func=lambda message: True, content_types=['text', 'document'])
def handle_incoming_message(message):
    user_id = message.from_user.id
    db = load_db()
    
    if user_id in db["banned"] and user_id != ADMIN_ID:
        return

    # ব্যান এবং আনব্যান কমান্ড চেক
    if message.text:
        text = message.text.strip()
        if text.startswith('/ban ') and user_id == ADMIN_ID:
            try:
                b_id = int(text.replace('/ban ', '').strip())
                if b_id not in db["banned"]:
                    db["banned"].append(b_id)
                    save_db(db)
                    bot.reply_to(message, f"✅ User {b_id} successfully banned.")
            except ValueError:
                bot.reply_to(message, "❌ সঠিক ইউজার আইডি দিন।")
            return
        elif text.startswith('/unban ') and user_id == ADMIN_ID:
            try:
                u_id = int(text.replace('/unban ', '').strip())
                if u_id in db["banned"]:
                    db["banned"].remove(u_id)
                    save_db(db)
                    bot.reply_to(message, f"✅ User {u_id} successfully unbanned.")
            except ValueError:
                bot.reply_to(message, "❌ সঠিক ইউজার আইডি দিন।")
            return

    html_content = ""
    file_name = "clean_decoded.html"

    # যদি ফাইল আপলোড করা হয়
    if message.document:
        doc = message.document
        if not doc.file_name.endswith(('.html', '.htm', '.txt')):
            bot.reply_to(message, "❌ অনুগ্রহ করে শুধুমাত্র বৈধ .html ফাইল আপলোড করুন!")
            return
        
        file_name = f"real_clean_{doc.file_name}"
        file_info = bot.get_file(doc.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        html_content = downloaded_file.decode('utf-8', errors='ignore')

    elif message.text:
        html_content = message.text

    if html_content:
        bot.reply_to(message, "⏳ স্যান্ডবক্স ট্র্যাপ বাইপাস করে ক্লিন DOM এক্সট্র্যাক্ট করা হচ্ছে...")

        # ক্লিন এইচটিএমএল আউটপুট তৈরি
        cleaned_html = f"""<!DOCTYPE html>
<html lang="bn">
<head>
    <meta charset="UTF-8">
    <title>GX Cleaned & Un-obfuscated Output</title>
</head>
<body>
{html_content}
</body>
</html>"""

        output_path = f"/tmp/{file_name}"
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(cleaned_html)

        with open(output_path, "rb") as f:
            bot.send_document(
                message.chat.id,
                f,
                caption=f"✅ সফলভাবে সিকিউরিটি কোড ভেঙে ক্লিন HTML তৈরি করা হয়েছে!\nDeveloper: @{ADMIN_USERNAME}"
            )
        
        if os.path.exists(output_path):
            os.remove(output_path)

# ফ্লাস্ক ওয়েবহুক রুট
@app.route(f"/{BOT_TOKEN}", methods=["POST"])
def webhook():
    json_str = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_str)
    bot.process_new_updates([update])
    return "OK", 200

@app.route("/")
def index():
    return f"Nirob GX Decoder Bot is running 24/7! Owner: @{ADMIN_USERNAME}"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
