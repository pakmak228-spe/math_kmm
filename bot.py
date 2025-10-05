import os
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.enums import ParseMode
from datetime import datetime, timedelta
import asyncio
import json
from typing import Dict, List

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Обновленное расписание для 4 курса КММ согласно вашему тексту
SCHEDULE = {
    "Понедельник": {
        "числитель": [
            {"time": "13:25-15:00", "subject": "Матмодели фин. рынков", "teacher": "Сухочева Л.И.", "room": "312"},
            {"time": "15:10-16:45", "subject": "Исслед. операций", "teacher": "Михайлова И.В.", "room": "321"},
            {"time": "16:55-18:30", "subject": "Числ. методы", "teacher": "Костин Д.В.", "room": "319"},
            {"time": "18:40-20:00", "subject": "Проектир. ПО", "teacher": "Белоглазова Т.В.", "room": "501П"}
        ],
        "знаменатель": [
            {"time": "13:25-15:00", "subject": "Исслед. операций", "teacher": "Михайлова И.В.", "room": "306"},
            {"time": "15:10-16:45", "subject": "Методы оптимизации", "teacher": "Зверева М.Б.", "room": "319"},
            {"time": "16:55-18:30", "subject": "Числ. методы", "teacher": "Костин В.А.", "room": "305"},
            {"time": "18:40-20:00", "subject": "Проектир. ПО", "teacher": "Белоглазова Т.В.", "room": "501П"}
        ]
    },
    "Вторник": {
        "числитель": [
            {"time": "09:45-11:20", "subject": "Динам. теор. инф.", "teacher": "Сухочева Л.И.", "room": "Дистант"},
            {"time": "11:30-13:05", "subject": "Динам. теор. инф.", "teacher": "Сухочева Л.И.", "room": "Дистант"},
            {"time": "16:55-18:30", "subject": "Элем. теор. игр", "teacher": "Орлов В.П.", "room": "325"},
            {"time": "18:40-20:00", "subject": "Элем. теор. игр", "teacher": "Орлов В.П.", "room": "325"}
        ],
        "знаменатель": [
            {"time": "09:45-11:20", "subject": "Динам. теор. инф.", "teacher": "Сухочева Л.И.", "room": "Дистант"},
            {"time": "15:10-16:45", "subject": "Элем. теор. игр", "teacher": "Орлов В.П.", "room": "325"},
            {"time": "16:55-18:30", "subject": "Элем. теор. игр", "teacher": "Орлов В.П.", "room": "325"}
        ]
    },
    "Среда": {
        "числитель": [
            {"time": "08:00-09:35", "subject": "БЖД", "teacher": "Скоробогатова Л.Г.", "room": "Дистант"},
            {"time": "11:30-13:05", "subject": "Числ. методы", "teacher": "Силаева М.Б.", "room": "501П"},
            {"time": "13:25-15:00", "subject": "Макростат. анал. и прогн.", "teacher": "Сухочева Л.И.", "room": "305"},
            {"time": "15:10-16:45", "subject": "Макростат. анал. и прогн.", "teacher": "Сухочева Л.И.", "room": "305"}
        ],
        "знаменатель": [
            {"time": "11:30-13:05", "subject": "Числ. методы", "teacher": "Силаева М.Н.", "room": "312"},
            {"time": "13:25-15:00", "subject": "Макростат. анал. и прогн.", "teacher": "Сухочева Л.И.", "room": "305"},
            {"time": "15:10-16:45", "subject": "Макростат. анал. и прогн.", "teacher": "Сухочева Л.И.", "room": "305"},
            {"time": "16:55-18:30", "subject": "Матмодели фин. рынков", "teacher": "Сухочева Л.И.", "room": "305"}
        ]
    },
    "Четверг": {
        "числитель": [
            {"time": "13:25-15:00", "subject": "Матметоды в социол.", "teacher": "Царев С.Л.", "room": "365/409П"},
            {"time": "15:10-16:45", "subject": "Матметоды в естеств.", "teacher": "Бурлуцкая М.Ш.", "room": "335/409П"}
        ],
        "знаменатель": [
            {"time": "13:25-15:00", "subject": "Матметоды в социол.", "teacher": "Царев С.Л.", "room": "365/409П"},
            {"time": "15:10-16:45", "subject": "Матметоды в естеств.", "teacher": "Бурлуцкая М.Ш.", "room": "335/409П"}
        ]
    },
    "Пятница": {
        "числитель": [
            {"time": "08:00-16:00", "subject": "ВОЕННАЯ КАФЕДРА", "teacher": "", "room": ""}
        ],
        "знаменатель": [
            {"time": "08:00-16:00", "subject": "ВОЕННАЯ КАФЕДРА", "teacher": "", "room": ""}
        ]
    },
    "Суббота": {
        "числитель": [
            {"time": "09:45-11:20", "subject": "Теория управления", "teacher": "Зубова С.П.", "room": "Дистант"},
            {"time": "11:30-13:05", "subject": "Теория управления", "teacher": "Зубова С.П.", "room": "Дистант"}
        ],
        "знаменатель": [
            {"time": "09:45-11:20", "subject": "Теория управления", "teacher": "Зубова С.П.", "room": "Дистант"}
        ]
    }
}

class ScheduleBot:
    def __init__(self):
        self.base_date = datetime(2025, 10, 6)  # 6 октября 2025 - знаменатель
        self.reminders_file = "reminders.json"
        self.reminders = self.load_reminders()
        
    def load_reminders(self):
        """Загрузка напоминаний из файла"""
        try:
            if os.path.exists(self.reminders_file):
                with open(self.reminders_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading reminders: {e}")
        return {}
    
    def save_reminders(self):
        """Сохранение напоминаний в файл"""
        try:
            with open(self.reminders_file, 'w', encoding='utf-8') as f:
                json.dump(self.reminders, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Error saving reminders: {e}")
    
    def add_reminder(self, user_id: int, lesson_info: dict, reminder_time: datetime):
        """Добавление напоминания"""
        if str(user_id) not in self.reminders:
            self.reminders[str(user_id)] = []
        
        reminder = {
            "lesson_info": lesson_info,
            "reminder_time": reminder_time.isoformat(),
            "notified": False
        }
        
        self.reminders[str(user_id)].append(reminder)
        self.save_reminders()
    
    def get_week_type(self, target_date):
        """Определяет тип недели (числитель/знаменатель)"""
        days_diff = (target_date - self.base_date).days
        week_num = days_diff // 7
        return "знаменатель" if week_num % 2 == 0 else "числитель"
    
    def get_schedule_for_day(self, target_date):
        week_type = self.get_week_type(target_date)
        day_name_rus = self.get_russian_day_name(target_date.weekday())
        
        # Получаем расписание для дня
        day_schedule = SCHEDULE.get(day_name_rus, {}).get(week_type, [])
        
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
    
    def create_reminder_keyboard(self, schedule_data):
        """Создает клавиатуру для выбора пары для напоминания"""
        if not schedule_data["schedule"]:
            return None
            
        keyboard = []
        for i, lesson in enumerate(schedule_data["schedule"], 1):
            button_text = f"{i}. {lesson['time']} - {lesson['subject']}"
            callback_data = f"remind_{i-1}_{schedule_data['day']}_{schedule_data['week_type']}"
            keyboard.append([InlineKeyboardButton(text=button_text, callback_data=callback_data)])
        
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

# Инициализация бота и диспетчера
schedule_bot = ScheduleBot()
bot = Bot(token=os.getenv('TELEGRAM_TOKEN'))
dp = Dispatcher()

@dp.message(Command("start"))
async def start_handler(message: Message):
    """Обработчик команды /start"""
    welcome_text = """
👋 Привет! Я бот расписания математического факультета.

Доступные команды:
/start - показать это сообщение
/day - расписание на сегодня
/tomorrow - расписание на завтра  
/week - расписание на неделю
/week_type - какая сейчас неделя
/remind - напомнить о паре (за 5 минут до начала)

🏫 4 курс КММ (Прикладная математика)
📋 Учитываю числитель/знаменатель
    """
    await message.answer(welcome_text)

@dp.message(Command("day"))
async def today_schedule(message: Message):
    """Обработчик команды /day - расписание на сегодня"""
    try:
        today = datetime.now()
        schedule_data = schedule_bot.get_schedule_for_day(today)
        message_text = schedule_bot.format_schedule_message(schedule_data)
        await message.answer(message_text, parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        logger.error(f"Error in today_schedule: {e}")
        await message.answer("❌ Произошла ошибка при получении расписания на сегодня")

@dp.message(Command("tomorrow"))
async def tomorrow_schedule(message: Message):
    """Обработчик команды /tomorrow - расписание на завтра"""
    try:
        tomorrow = datetime.now() + timedelta(days=1)
        schedule_data = schedule_bot.get_schedule_for_day(tomorrow)
        message_text = schedule_bot.format_schedule_message(schedule_data)
        await message.answer(message_text, parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        logger.error(f"Error in tomorrow_schedule: {e}")
        await message.answer("❌ Произошла ошибка при получении расписания на завтра")

@dp.message(Command("week"))
async def week_schedule(message: Message):
    """Обработчик команды /week - расписание на неделю"""
    try:
        today = datetime.now()
        message_text = "📅 *Расписание на неделю*\n🏫 *4 курс КММ*\n\n"
        
        for i in range(6):  # Пн-Сб
            day_date = today + timedelta(days=i)
            schedule_data = schedule_bot.get_schedule_for_day(day_date)
            
            message_text += f"*{schedule_data['day']}, {schedule_data['date']}*\n"
            message_text += f"📋 *Неделя: {schedule_data['week_type']}*\n"
            
            if not schedule_data["schedule"]:
                message_text += "❌ Занятий нет\n\n"
            else:
                for lesson in schedule_data["schedule"]:
                    message_text += f"⏰ {lesson['time']} - {lesson['subject']}"
                    if lesson['room']:
                        message_text += f" ({lesson['room']})"
                    message_text += "\n"
                message_text += "\n"
        
        await message.answer(message_text, parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        logger.error(f"Error in week_schedule: {e}")
        await message.answer("❌ Произошла ошибка при получении расписания на неделю")

@dp.message(Command("week_type"))
async def week_type_handler(message: Message):
    """Обработчик команды /week_type - тип текущей недели"""
    try:
        today = datetime.now()
        week_type = schedule_bot.get_week_type(today)
        next_week_type = "числитель" if week_type == "знаменатель" else "знаменатель"
        next_monday = today + timedelta(days=(7 - today.weekday()))
        
        message_text = f"📋 *Текущая неделя: {week_type}*\n"
        message_text += f"📅 Следующая неделя ({next_monday.strftime('%d.%m.%Y')}): {next_week_type}"
        await message.answer(message_text, parse_mode=ParseMode.MARKDOWN)
    except Exception as e:
        logger.error(f"Error in week_type_handler: {e}")
        await message.answer("❌ Произошла ошибка при определении типа недели")

@dp.message(Command("remind"))
async def remind_handler(message: Message):
    """Обработчик команды /remind - настройка напоминаний"""
    try:
        today = datetime.now()
        schedule_data = schedule_bot.get_schedule_for_day(today)
        
        if not schedule_data["schedule"]:
            await message.answer("❌ На сегодня занятий нет")
            return
        
        keyboard = schedule_bot.create_reminder_keyboard(schedule_data)
        if keyboard:
            await message.answer(
                "🔔 Выберите пару для напоминания (уведомление придет за 5 минут до начала):",
                reply_markup=keyboard
            )
        else:
            await message.answer("❌ Не удалось создать список пар для напоминаний")
            
    except Exception as e:
        logger.error(f"Error in remind_handler: {e}")
        await message.answer("❌ Произошла ошибка при настройке напоминаний")

@dp.callback_query(F.data.startswith("remind_"))
async def process_reminder_callback(callback: CallbackQuery):
    """Обработчик выбора пары для напоминания"""
    try:
        data_parts = callback.data.split("_")
        lesson_index = int(data_parts[1])
        day_name = data_parts[2]
        week_type = data_parts[3]
        
        # Получаем информацию о выбранной паре
        day_schedule = SCHEDULE.get(day_name, {}).get(week_type, [])
        if lesson_index >= len(day_schedule):
            await callback.answer("❌ Ошибка: пара не найдена")
            return
        
        lesson = day_schedule[lesson_index]
        
        # Парсим время начала пары
        start_time_str = lesson['time'].split('-')[0]
        start_time = datetime.strptime(start_time_str, "%H:%M").time()
        
        # Получаем дату занятия
        today = datetime.now()
        target_date = today
        
        # Если день не сегодня, находим дату этого дня на текущей неделе
        days_mapping = {"Понедельник": 0, "Вторник": 1, "Среда": 2, "Четверг": 3, "Пятница": 4, "Суббота": 5}
        target_day_index = days_mapping.get(day_name)
        if target_day_index is not None:
            current_day_index = today.weekday()
            days_diff = target_day_index - current_day_index
            if days_diff < 0:
                days_diff += 7  # Переход на следующую неделю
            target_date = today + timedelta(days=days_diff)
        
        # Создаем datetime для начала пары
        lesson_datetime = datetime.combine(target_date.date(), start_time)
        
        # Время напоминания (за 5 минут до начала)
        reminder_time = lesson_datetime - timedelta(minutes=5)
        
        # Добавляем напоминание
        schedule_bot.add_reminder(callback.from_user.id, lesson, reminder_time)
        
        await callback.answer(f"✅ Напоминание установлено на {reminder_time.strftime('%H:%M %d.%m.%Y')}")
        await callback.message.edit_text(
            f"🔔 Напоминание установлено!\n\n"
            f"📚 *{lesson['subject']}*\n"
            f"⏰ {lesson['time']}\n"
            f"👨‍🏫 {lesson.get('teacher', '')}\n"
            f"🏛 {lesson.get('room', '')}\n\n"
            f"Уведомление придет за 5 минут до начала пары",
            parse_mode=ParseMode.MARKDOWN
        )
        
    except Exception as e:
        logger.error(f"Error in process_reminder_callback: {e}")
        await callback.answer("❌ Ошибка при установке напоминания")

async def check_reminders():
    """Фоновая задача для проверки напоминаний"""
    while True:
        try:
            current_time = datetime.now()
            notifications_sent = False
            
            for user_id_str, user_reminders in schedule_bot.reminders.items():
                for reminder in user_reminders[:]:  # Копируем список для безопасного удаления
                    if reminder.get("notified"):
                        continue
                    
                    reminder_time = datetime.fromisoformat(reminder["reminder_time"])
                    if current_time >= reminder_time:
                        # Отправляем уведомление
                        lesson = reminder["lesson_info"]
                        try:
                            await bot.send_message(
                                int(user_id_str),
                                f"🔔 *Скоро пара!*\n\n"
                                f"📚 *{lesson['subject']}*\n"
                                f"⏰ Начинается в {lesson['time'].split('-')[0]}\n"
                                f"👨‍🏫 {lesson.get('teacher', '')}\n"
                                f"🏛 {lesson.get('room', '')}",
                                parse_mode=ParseMode.MARKDOWN
                            )
                            reminder["notified"] = True
                            notifications_sent = True
                        except Exception as e:
                            logger.error(f"Error sending reminder to {user_id_str}: {e}")
                            # Удаляем невалидные напоминания
                            user_reminders.remove(reminder)
            
            if notifications_sent:
                schedule_bot.save_reminders()
                
            await asyncio.sleep(30)  # Проверяем каждые 30 секунд
            
        except Exception as e:
            logger.error(f"Error in check_reminders: {e}")
            await asyncio.sleep(60)

async def main():
    """Основная функция запуска бота"""
    logger.info("Бот запускается...")
    
    # Запускаем фоновую задачу для напоминаний
    asyncio.create_task(check_reminders())
    
    await dp.start_polling(bot)

if __name__ == '__main__':
    # Проверка наличия токена
    if not os.getenv('TELEGRAM_TOKEN'):
        logger.error("❌ Токен не найден! Установите переменную TELEGRAM_TOKEN")
        exit(1)
    
    # Запуск бота
    asyncio.run(main())
