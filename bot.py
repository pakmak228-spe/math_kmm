import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from datetime import datetime, timedelta
import json

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Ваши данные расписания (вставьте ваш JSON)
SCHEDULE_DATA = [
# ⚠️ ВСТАВЬТЕ ВЕСЬ ВАШ JSON ФАЙЛ СЮДА!
# Скопируйте ВСЁ содержимое из 2_5330117481635805732.json
# между этими квадратными скобками
]

class ScheduleBot:
    def __init__(self, json_data):
        self.schedule_data = json_data
        self.base_date = datetime(2025, 10, 6)
        
    def get_week_type(self, target_date):
        days_diff = (target_date - self.base_date).days
        week_num = days_diff // 7
        return "знаменатель" if week_num % 2 == 0 else "числитель"
    
    def parse_subject(self, subject_str, week_type):
        if not subject_str or subject_str.strip() == "":
            return None
        
        if '\n' in subject_str:
            parts = subject_str.strip().split('\n')
            if week_type == "числитель" and len(parts) > 0:
                subject_str = parts[0].strip()
            elif week_type == "знаменатель" and len(parts) > 1:
                subject_str = parts[1].strip()
            else:
                return None
        
        parts = subject_str.strip().split(' ')
        if len(parts) < 2:
            return {"subject": subject_str, "teacher": "", "room": ""}
        
        teacher_parts = []
        subject_parts = []
        room_parts = []
        
        for part in parts:
            if '.' in part and len(part) <= 5:
                teacher_parts.append(part)
            elif teacher_parts:
                room_parts.append(part)
            else:
                subject_parts.append(part)
        
        if teacher_parts and subject_parts:
            teacher_name = subject_parts[-1] + ' ' + ' '.join(teacher_parts)
            subject_parts = subject_parts[:-1]
        else:
            teacher_name = ""
        
        return {
            "subject": ' '.join(subject_parts).strip(),
            "teacher": teacher_name.strip(),
            "room": ' '.join(room_parts).strip()
        }
    
    def get_schedule_for_day(self, target_date):
        week_type = self.get_week_type(target_date)
        day_name_rus = self.get_russian_day_name(target_date.weekday())
        
        day_schedule = []
        
        for row in self.schedule_data:
            if not row:
                continue
                
            for key, value in row.items():
                if value and day_name_rus in str(value):
                    current_time = None
                    start_collecting = False
                    
                    for data_row in self.schedule_data:
                        if not data_row:
                            continue
                            
                        for k, v in data_row.items():
                            if v and v in ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота"]:
                                if v != day_name_rus:
                                    start_collecting = False
                                else:
                                    start_collecting = True
                        
                        if start_collecting:
                            if 'Column37' in data_row and data_row['Column37']:
                                current_time = data_row['Column37']
                            
                            if 'Column39' in data_row and data_row['Column39'] and current_time:
                                subject_info = self.parse_subject(data_row['Column39'], week_type)
                                if subject_info and subject_info["subject"]:
                                    existing_lesson = next((lesson for lesson in day_schedule if lesson["time"] == current_time), None)
                                    if not existing_lesson:
                                        day_schedule.append({
                                            "time": current_time,
                                            **subject_info
                                        })
        
        return {
            "day": day_name_rus,
            "date": target_date.strftime("%d.%m.%Y"),
            "week_type": week_type,
            "schedule": day_schedule
        }
    
    def get_russian_day_name(self, weekday):
        days = ["Понедельник", "Вторник", "Среда", "Четверг", "Пятница", "Суббота", "Воскресенье"]
        return days[weekday]
    
    def format_schedule_message(self, schedule_data):
        if not schedule_data["schedule"]:
            return f"📅 *{schedule_data['day']}, {schedule_data['date']}*\n🏫 *4 курс КММ*\n📋 *Неделя: {schedule_data['week_type']}*\n\n❌ Занятий нет"
        
        message = f"📅 *{schedule_data['day']}, {schedule_data['date']}*\n"
        message += f"🏫 *4 курс КММ*\n"
        message += f"📋 *Неделя: {schedule_data['week_type']}*\n\n"
        
        for i, lesson in enumerate(schedule_data["schedule"], 1):
            message += f"*{i}. {lesson['time']}*\n"
            message += f"   🎯 {lesson['subject']}\n"
            if lesson['teacher']:
                message += f"   👨‍🏫 {lesson['teacher']}\n"
            if lesson['room']:
                message += f"   🏛 {lesson['room']}\n"
            message += "\n"
        
        return message

# Глобальная переменная для бота
schedule_bot = ScheduleBot(SCHEDULE_DATA)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = """
👋 Привет! Я бот расписания математического факультета.

Доступные команды:
/start - показать это сообщение
/day - расписание на сегодня
/tomorrow - расписание на завтра  
/week - расписание на неделю
/week_type - какая сейчас неделя

🏫 4 курс КММ (Прикладная математика)
📋 Учитываю числитель/знаменатель
    """
    await update.message.reply_text(welcome_text)

async def today_schedule(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        today = datetime.now()
        schedule_data = schedule_bot.get_schedule_for_day(today)
        message = schedule_bot.format_schedule_message(schedule_data)
        await update.message.reply_text(message, parse_mode='Markdown')
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {str(e)}")

async def tomorrow_schedule(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        tomorrow = datetime.now() + timedelta(days=1)
        schedule_data = schedule_bot.get_schedule_for_day(tomorrow)
        message = schedule_bot.format_schedule_message(schedule_data)
        await update.message.reply_text(message, parse_mode='Markdown')
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {str(e)}")

async def week_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        today = datetime.now()
        week_type = schedule_bot.get_week_type(today)
        message = f"📋 Сейчас *{week_type}* неделя"
        await update.message.reply_text(message, parse_mode='Markdown')
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {str(e)}")

def main():
    """Запуск бота"""
    # Токен бота (замените на ваш!)
    TOKEN = os.getenv('TELEGRAM_TOKEN', 'ВАШ_ТОКЕН_БОТА')
    
    application = Application.builder().token(TOKEN).build()
    
    # Регистрируем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("day", today_schedule))
    application.add_handler(CommandHandler("tomorrow", tomorrow_schedule))
    application.add_handler(CommandHandler("week_type", week_type))
    
    print("Бот запущен...")
    application.run_polling()

if __name__ == '__main__':
    main()
