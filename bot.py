import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.enums import ParseMode
from datetime import datetime, timedelta
import asyncio

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Расписание для 4 курса КММ (Прикладная математика)
SCHEDULE = {
    "Понедельник": {
        "числитель": [
            {"time": "8.00-9.35", "subject": "Матмодели финансовых рынков", "teacher": "Сухочева Л.И.", "room": "312"},
            {"time": "9.45-11.20", "subject": "Матмодели физических процессов", "teacher": "Костин В.А.", "room": "Дистант"},
            {"time": "11.30-13.05", "subject": "Методы оптимизаций", "teacher": "Зверева М.Б.", "room": "319"},
            {"time": "13.25-15.00", "subject": "Исследование операций", "teacher": "Михайлова И.В.", "room": "306"},
            {"time": "15.10-16.45", "subject": "Спецкурс Методика решения задач с параметрами", "teacher": "Рябенко А.С.", "room": "305"}
        ],
        "знаменатель": [
            {"time": "8.00-9.35", "subject": "Матмодели финансовых рынков", "teacher": "Сухочева Л.И.", "room": "312"},
            {"time": "9.45-11.20", "subject": "Матмодели физических процессов", "teacher": "Костин В.А.", "room": "Дистант"},
            {"time": "11.30-13.05", "subject": "Методы оптимизаций", "teacher": "Зверева М.Б.", "room": "319"},
            {"time": "13.25-15.00", "subject": "Исследование операций", "teacher": "Михайлова И.В.", "room": "321"},
            {"time": "15.10-16.45", "subject": "Численные методы", "teacher": "Костин Д.В.", "room": "319"}
        ]
    },
    "Вторник": {
        "числитель": [
            {"time": "8.00-9.35", "subject": "Практика", "teacher": "", "room": ""},
            {"time": "9.45-11.20", "subject": "Динамическая теория информации", "teacher": "Сухочева Л.И.", "room": "Дистант"},
            {"time": "11.30-13.05", "subject": "Спецкурс Эллиптические уравнения с параметром", "teacher": "Рябенко А.С.", "room": "306"},
            {"time": "13.25-15.00", "subject": "Спецкурс Теория Лере-Шаудера", "teacher": "Звягин В.Г.", "room": "НИИМ"},
            {"time": "15.10-16.45", "subject": "Элементы теории игр", "teacher": "Орлов В.П.", "room": "325"}
        ],
        "знаменатель": [
            {"time": "8.00-9.35", "subject": "Практика", "teacher": "", "room": ""},
            {"time": "9.45-11.20", "subject": "Динамическая теория информации", "teacher": "Сухочева Л.И.", "room": "Дистант"},
            {"time": "11.30-13.05", "subject": "Спецкурс Эллиптические уравнения с параметром", "teacher": "Рябенко А.С.", "room": "306"},
            {"time": "13.25-15.00", "subject": "Спецкурс Теория Лере-Шаудера", "teacher": "Звягин В.Г.", "room": "НИИМ"},
            {"time": "15.10-16.45", "subject": "Элементы теории игр", "teacher": "Орлов В.П.", "room": "325"}
        ]
    },
    "Среда": {
        "числитель": [
            {"time": "8.00-9.35", "subject": "БЖД", "teacher": "Каленикина Д.А.", "room": "Дистант"},
            {"time": "9.45-11.20", "subject": "БЖД", "teacher": "Каленикина Д.А.", "room": "Дистант"},
            {"time": "11.30-13.05", "subject": "Численные методы", "teacher": "Силаева М.Б.", "room": "501П"},
            {"time": "13.25-15.00", "subject": "Макростатистический анализ и прогнозирование", "teacher": "Сухочева Л.И.", "room": "305"},
            {"time": "15.10-16.45", "subject": "Универсальные матпакеты", "teacher": "Ткачева С.А.", "room": "312"}
        ],
        "знаменатель": [
            {"time": "8.00-9.35", "subject": "БЖД", "teacher": "Скоробогатова Л.Г.", "room": "Дистант"},
            {"time": "9.45-11.20", "subject": "БЖД", "teacher": "Скоробогатова Л.Г.", "room": "Дистант"},
            {"time": "11.30-13.05", "subject": "Численные методы", "teacher": "Силаева М.Н.", "room": "312"},
            {"time": "13.25-15.00", "subject": "Макростатистический анализ и прогнозирование", "teacher": "Сухочева Л.И.", "room": "305"},
            {"time": "15.10-16.45", "subject": "Методика преподавания физико-математических дисциплин", "teacher": "Давыдова М.Б.", "room": "325"}
        ]
    },
    "Четверг": {
        "числитель": [
            {"time": "8.00-9.35", "subject": "Спецкурс Статистический анализ данных", "teacher": "Бахтина Ж.И.", "room": "Дистант"},
            {"time": "9.45-11.20", "subject": "Спецкурс Статистический анализ данных", "teacher": "Бахтина Ж.И.", "room": "Дистант"},
            {"time": "11.30-13.05", "subject": "Численные методы", "teacher": "Силаева М.Н.", "room": "312"},
            {"time": "13.25-15.00", "subject": "Методы оптимизации", "teacher": "Зверева М.Б.", "room": "501П"},
            {"time": "15.10-16.45", "subject": "Матметоды в естествознании", "teacher": "Бурлуцкая М.Ш.", "room": "335/409П"}
        ],
        "знаменатель": [
            {"time": "8.00-9.35", "subject": "Спецкурс Статистический анализ данных", "teacher": "Бахтина Ж.И.", "room": "Дистант"},
            {"time": "9.45-11.20", "subject": "Спецкурс Статистический анализ данных", "teacher": "Бахтина Ж.И.", "room": "Дистант"},
            {"time": "11.30-13.05", "subject": "Численные методы", "teacher": "Силаева М.Н.", "room": "312"},
            {"time": "13.25-15.00", "subject": "Спецкурс Матметоды в страховании", "teacher": "Бахтина Ж.И.", "room": "Дистант"},
            {"time": "15.10-16.45", "subject": "БЖД", "teacher": "Скоробогатова Л.Г.", "room": "Дистант"}
        ]
    },
    "Пятница": {
        "числитель": [
            {"time": "8.00-9.35", "subject": "Военная подготовка", "teacher": "", "room": ""},
            {"time": "9.45-11.20", "subject": "Практика", "teacher": "", "room": ""},
            {"time": "11.30-13.05", "subject": "Основы военной подготовки", "teacher": "Кречун А.Д.", "room": "Никитинская 14б ауд. 22"},
            {"time": "13.25-15.00", "subject": "Основы военной подготовки", "teacher": "Кречун А.Д.", "room": "Никитинская 14б ауд. 22"}
        ],
        "знаменатель": [
            {"time": "8.00-9.35", "subject": "Военная подготовка", "teacher": "", "room": ""},
            {"time": "9.45-11.20", "subject": "Практика", "teacher": "", "room": ""},
            {"time": "11.30-13.05", "subject": "Основы военной подготовки", "teacher": "Кречун А.Д.", "room": "Никитинская 14б ауд. 22"},
            {"time": "13.25-15.00", "subject": "Основы военной подготовки", "teacher": "Скоробогатова Л.Г.", "room": "Никитинская 14б ауд. 32"}
        ]
    },
    "Суббота": {
        "числитель": [
            {"time": "8.00-9.35", "subject": "Теория управления", "teacher": "Зубова С.П.", "room": "Дистант"},
            {"time": "9.45-11.20", "subject": "Теория управления", "teacher": "Зубова С.П.", "room": "Дистант"},
            {"time": "11.30-13.05", "subject": "Теория управления", "teacher": "Зубова С.П.", "room": "Дистант"},
            {"time": "13.25-15.00", "subject": "Нелинейная динамика и хаос", "teacher": "Мелешенко П.А.", "room": "Дистант"}
        ],
        "знаменатель": [
            {"time": "8.00-9.35", "subject": "Матмодели физических процессов", "teacher": "Костин В.А.", "room": "Дистант"},
            {"time": "9.45-11.20", "subject": "Матмодели физических процессов", "teacher": "Костин В.А.", "room": "Дистант"},
            {"time": "11.30-13.05", "subject": "Матмодели физических процессов", "teacher": "Костин В.А.", "room": "Дистант"},
            {"time": "13.25-15.00", "subject": "Нелинейная динамика и хаос", "teacher": "Мелешенко П.А.", "room": "Дистант"}
        ]
    }
}

class ScheduleBot:
    def __init__(self):
        self.base_date = datetime(2025, 10, 6)  # 6 октября 2025 - знаменатель
        
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

async def main():
    """Основная функция запуска бота"""
    logger.info("Бот запускается...")
    await dp.start_polling(bot)

if __name__ == '__main__':
    # Проверка наличия токена
    if not os.getenv('TELEGRAM_TOKEN'):
        logger.error("❌ Токен не найден! Установите переменную TELEGRAM_TOKEN")
        exit(1)
    
    # Запуск бота
    asyncio.run(main())
