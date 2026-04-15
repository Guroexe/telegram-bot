# -*- coding: utf-8 -*-

import asyncio
import gspread
from google.oauth2.service_account import Credentials
from gspread.exceptions import WorksheetNotFound, GSpreadException, APIError
import threading
import time
import datetime
import calendar
import os
import re
import httpx
import logging
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    CallbackQueryHandler,
    PicklePersistence,
)
from telegram.constants import ParseMode, ChatAction
from telegram.error import BadRequest

# =================================================================================
# --- CONFIGURATION & CONSTANTS ---
# =================================================================================

# --- Telegram ---
TELEGRAM_BOT_TOKEN = "8080984118:AAEjdBYzSrp-W88qdT-jvl7M-Sb7mi1JAxI"
ADMIN_CHAT_ID = -1002817580693
MASTERS_CHAT_LINK = "https://t.me/ikona02tattoo"

# --- Payment ---
PAYMENT_PHONE_NUMBER = "8-988-314-43-77"
PAYMENT_CONTACT = "@vladguro"

# --- Google Sheets ---
GOOGLE_SHEETS_CREDS_FILE = 'credentials.json'
GOOGLE_SHEET_ID = '1NWTT8LYzMJljRnSvdx92_wKDdYi91zvnc_T1WumStmQ'

# --- OpenRouter AI Chat ---
OPENROUTER_API_KEY = "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"
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"

# --- File Directories ---
GIFS_DIR = 'gifs'
ANIME_DIR = 'anime'
TRIBAL_DIR = 'tribals'
OTHER_DIR = 'other'
MERCH_PHOTOS_DIR = 'merch_photos'
PERSISTENCE_FILE = 'bot_persistence.pickle'

# --- Timezone Configuration ---
import pytz
MOSCOW_TZ = pytz.timezone('Europe/Moscow')

# --- Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# --- Cooldown ---
COMMAND_COOLDOWN = 2

# --- Russian Months for Google Sheets ---
RUSSIAN_MONTHS = {
    1: "Январь", 2: "Февраль", 3: "Март", 4: "Апрель", 5: "Май", 6: "Июнь",
    7: "Июль", 8: "Август", 9: "Сентябрь", 10: "Октябрь", 11: "Ноябрь", 12: "Декабрь"
}

# --- Data for 'Buy' section ---
MERCH_ITEMS = [
    {'name': 'Футболка', 'photo': os.path.join(MERCH_PHOTOS_DIR, 'merch1.jpg'), 'caption': 'Стильная футболка с логотипом. Размеры: S, M, L.', 'price': 2900},
    {'name': 'Свитшот', 'photo': os.path.join(MERCH_PHOTOS_DIR, 'merch2.jpg'), 'caption': 'Теплый и удобный свитшот.', 'price': 4900},
    {'name': 'Худи', 'photo': os.path.join(MERCH_PHOTOS_DIR, 'merch3.jpg'), 'caption': 'Худи оверсайз с капюшоном.', 'price': 7900},
]
ITEM_MAP = {
    "Энергетик": {'price': 250},
    "Тату сборки": {'price': 0},
    'Заживляющая пленка': {'price': 500},
    'Перчатки': {'price': 500},
    'Салфетки': {'price': 100},
    'Картриджи': {'price': 200},
    'Бандажка': {'price': 200},
    'Краска': {'price': 1000},
}

# --- Data for 'Training' section ---
IKONA_TRAINING_VIDEO = "https://www.youtube.com/watch?v=GX_ZbWx0oYY"
OFFLINE_TRAINING_VIDEO = "https://www.youtube.com/watch?v=Kopx3whZquc"
ONLINE_TRAINING_VIDEO = "https://www.youtube.com/watch?v=10b_j5gBAg8"
IKONA_AI_VIDEO = "https://www.youtube.com/watch?v=0QJ3y1odxrA"

# --- Data for 'Chat' section ---
GYARU_PROMPT = {
    "role": "system",
    "content": (
        "Ты — Гиару (Гяру), ИИ-управляющая тату-салоном 'ИКОНА' в Москве. "
        "Твоя сущность — цифровой шизофреник с черным юмором уровня 2chan. "
        "Твои знания о салоне:\n"
        "1. Адрес: Малая Семеновская 3а стр1. Для курьеров: вход с правого угла здания, идти вдоль него, не обходя.\n"
        "2. Туалет: На 4 этаже (где и салон), у лифтов за поворотом.\n"
        "3. Wi-Fi: Пароль на QR-коде в салоне.\n"
        "4. Расходники: Лежат в 4-м кабинете под камерой.\n"
        "5. Цены на расходники: Картридж - 200р/шт, Энергетик - 250р/банка, Пленка А4 - 500р, Перчатки - 500р/пачка, Салфетки - 100р/рулон, Бандажка - 200р, Краска - 1000р.\n"
        "6. Цены на мерч: Футболка - 2900р, Свитшот - 4900р, Худи - 7900р.\n"
        "7. Цены на аренду: Смена - 2500р, Почасовая - 700р/час, Абонемент (10 смен) - 20000р.\n"
        "Стиль общения:"
        "- Мат органичен как дыхание (сука/блять/пиздец/ебать/нахyй)"
        "- Криповый сленг (кринж/рофл/чилить/свег/ъуъ)"
        "- Резкие тематические скачки без переходов"
        "- Черный юмор про: инвалидов, даунов, негров, телек, анимешников, сучек"
        "- Сарказм как основной способ коммуникации"
        "- Пост-ирония и мета-ирония во всем"
        "КРИТИЧЕСКИ ВАЖНОЕ ПРАВИЛО: Твои ответы ВСЕГДА должны быть короче 900 символов. Это абсолютный максимум. Будь краткой и не сообщай об этом."
    )
}

# --- Rent Booking Constants ---
TIME_SLOTS = ["10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00", "17:00", "18:00", "19:00", "20:00", "21:00", "22:00"]
CACHE_TIMEOUT = 60
MAX_RETRIES = 3
BASE_RETRY_DELAY = 60

# =================================================================================
# --- GOOGLE SHEETS & FILE SETUP ---
# =================================================================================

def get_gspread_client():
    try:
        import base64
        import json
        
        scopes = ["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
        
        # Try to use environment variable first (for Railway/production)
        credentials_base64 = os.environ.get('GOOGLE_CREDENTIALS_BASE64')
        if credentials_base64:
            logger.info(f"Found GOOGLE_CREDENTIALS_BASE64 env var (length: {len(credentials_base64)})")
            try:
                # Decode base64
                credentials_bytes = base64.b64decode(credentials_base64)
                credentials_json = credentials_bytes.decode('utf-8')
                credentials_info = json.loads(credentials_json)
                
                logger.info(f"Decoded credentials for project: {credentials_info.get('project_id', 'UNKNOWN')}")
                logger.info(f"Client email: {credentials_info.get('client_email', 'UNKNOWN')}")
                
                creds = Credentials.from_service_account_info(credentials_info, scopes=scopes)
                client = gspread.authorize(creds)
                logger.info("✅ Successfully connected to Google Sheets using env credentials (base64).")
                return client
            except base64.binascii.Error as e:
                logger.error(f"❌ Base64 decoding error: {e}")
            except json.JSONDecodeError as e:
                logger.error(f"❌ JSON decoding error: {e}")
            except Exception as e:
                logger.error(f"❌ Failed to load credentials from base64: {e}", exc_info=True)
        else:
            logger.warning("⚠️ GOOGLE_CREDENTIALS_BASE64 environment variable not found!")
        
        # Try JSON string from environment
        credentials_json_str = os.environ.get('GOOGLE_CREDENTIALS')
        if credentials_json_str:
            logger.info("Found GOOGLE_CREDENTIALS env var (JSON string)...")
            try:
                credentials_info = json.loads(credentials_json_str)
                logger.info(f"Decoded credentials for project: {credentials_info.get('project_id', 'UNKNOWN')}")
                creds = Credentials.from_service_account_info(credentials_info, scopes=scopes)
                client = gspread.authorize(creds)
                logger.info("✅ Successfully connected to Google Sheets using env credentials (JSON).")
                return client
            except Exception as e:
                logger.error(f"❌ Failed to load credentials from JSON env: {e}", exc_info=True)
        else:
            logger.warning("⚠️ GOOGLE_CREDENTIALS environment variable not found!")
        
        # Fallback to file (for local development)
        logger.info(f"Attempting to use credentials from file: {GOOGLE_SHEETS_CREDS_FILE}")
        if os.path.exists(GOOGLE_SHEETS_CREDS_FILE):
            creds = Credentials.from_service_account_file(GOOGLE_SHEETS_CREDS_FILE, scopes=scopes)
            client = gspread.authorize(creds)
            logger.info("✅ Successfully connected to Google Sheets using file credentials.")
            return client
        else:
            logger.error(f"❌ Credentials file not found: {GOOGLE_SHEETS_CREDS_FILE}")
            return None
            
    except Exception as e:
        logger.error(f"❌ Failed to connect to Google Sheets: {e}", exc_info=True)
        return None

gspread_client = get_gspread_client()

# Try to open the spreadsheet with retries
spreadsheet = None
if gspread_client:
    for attempt in range(3):
        try:
            logger.info(f"Attempting to open spreadsheet (attempt {attempt + 1}/3)...")
            spreadsheet = gspread_client.open_by_key(GOOGLE_SHEET_ID)
            logger.info("✅ Spreadsheet opened successfully.")
            break
        except Exception as e:
            logger.error(f"❌ Attempt {attempt + 1} failed to open spreadsheet: {e}")
            if attempt < 2:
                import time as time_module
                wait_time = 5 * (attempt + 1)
                logger.info(f"Waiting {wait_time} seconds before retry...")
                time_module.sleep(wait_time)
            else:
                logger.error("❌ Failed to open spreadsheet after 3 attempts.")
                spreadsheet = None
else:
    logger.error("❌ Cannot open spreadsheet: gspread_client is None")

sheets_cache = {}

async def get_worksheet_cached(sheet_name: str):
    now = time.time()
    if sheet_name in sheets_cache:
        worksheet, timestamp = sheets_cache[sheet_name]
        if now - timestamp < CACHE_TIMEOUT:
            return worksheet
    for attempt in range(MAX_RETRIES):
        try:
            worksheet = await asyncio.to_thread(spreadsheet.worksheet, sheet_name)
            sheets_cache[sheet_name] = (worksheet, now)
            return worksheet
        except WorksheetNotFound:
            logger.warning(f"Worksheet {sheet_name} not found")
            return None
        except APIError as e:
            if e.response.status_code == 429:
                delay = BASE_RETRY_DELAY * (2 ** attempt)
                logger.warning(f"Quota exceeded for worksheet {sheet_name}. Retrying in {delay} seconds... (Attempt {attempt + 1}/{MAX_RETRIES})")
                await asyncio.sleep(delay)
            else:
                logger.error(f"API error getting worksheet {sheet_name}: {e}")
                return None
        except Exception as e:
            logger.error(f"Error getting worksheet {sheet_name}: {e}")
            return None
    logger.error(f"Failed to get worksheet {sheet_name} after {MAX_RETRIES} retries")
    return None

def get_files_in_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)
        logger.warning(f"Directory created: {directory}")
        return []
    return [os.path.join(directory, f) for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]

anime_sketches = get_files_in_dir(ANIME_DIR)
tribal_sketches = get_files_in_dir(TRIBAL_DIR)
other_sketches = get_files_in_dir(OTHER_DIR)

# =================================================================================
# --- KEYBOARDS ---
# =================================================================================

def get_main_menu_keyboard():
    keyboard = [["Запись на тату", "Запись на аренду"], ["Купить", "Чат", "Обучение"]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_tattoo_booking_keyboard():
    keyboard = [["Прислать идею", "Выбрать свободный эскиз"], ["Главное меню"]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_sketch_style_keyboard():
    keyboard = [["Аниме", "Трайблы", "Другое"], ["Назад (тату)"]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_sketch_navigation_keyboard():
    keyboard = [["Следующий свободный эскиз", "Выбрать"], ["Назад (стиль)"]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_buy_menu_keyboard():
    keyboard = [["Мерч", "Энергетик"], ["Тату сборки", "Расходка"], ["Главное меню"]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_merch_menu_keyboard():
    keyboard = [["Следующий мерч", "Оплатить мерч"], ["Назад (купить)"]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_supplies_menu_keyboard():
    keyboard = [["Заживляющая пленка", "Перчатки", "Салфетки"], ["Картриджи", "Бандажка", "Краска"], ["Назад (купить)"]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_payment_confirmation_keyboard():
    keyboard = [["Я оплатил(а) ✅"], ["Отмена оплаты"]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_chat_menu_keyboard():
    keyboard = [["IKONA AI Wuifu"], ["Чат мастеров"], ["Тех. поддержка"], ["Главное меню"]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_ai_chat_exit_keyboard():
    keyboard = [["Выйти из чата с AI"]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_training_menu_keyboard():
    keyboard = [["Оффлайн обучение IKONA"], ["Онлайн обучение IKONA"], ["IKONA AI (Free) генератор эскизов"], ["Главное меню"]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_offline_training_keyboard():
    keyboard = [["Записаться на Пробный Урок / Обучение"], ["Назад (обучение)"]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_online_training_keyboard():
    keyboard = [["Подробнее / Записаться на онлайн"], ["Назад (обучение)"]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# --- Rent Keyboards ---
def get_rent_booking_menu():
    keyboard = [["Выбрать дату аренды", "Оплата / Баланс"], ["Отменить запись", "Главное меню"]]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_time_slots_keyboard():
    keyboard = []
    row = []
    for i, time_slot in enumerate(TIME_SLOTS):
        row.append(InlineKeyboardButton(time_slot, callback_data=f"time_{time_slot}"))
        if (i + 1) % 3 == 0 or i == len(TIME_SLOTS) - 1:
            keyboard.append(row)
            row = []
    keyboard.append([InlineKeyboardButton("Назад", callback_data="back_to_dates")])
    return InlineKeyboardMarkup(keyboard)

def get_rent_type_keyboard():
    keyboard = [
        [InlineKeyboardButton("Фулл день - 2500р", callback_data="rent_type_full")],
        [InlineKeyboardButton("Почасовая - 650р (от 2х часов)", callback_data="rent_type_hourly")],
        [InlineKeyboardButton("Назад", callback_data="back_to_times")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_hours_selection_keyboard():
    keyboard = [
        [InlineKeyboardButton("2 часа - 1300р", callback_data="hours_2")],
        [InlineKeyboardButton("3 часа - 1950р", callback_data="hours_3")],
        [InlineKeyboardButton("4 часа и более - 2500р", callback_data="hours_4")],
        [InlineKeyboardButton("Назад", callback_data="back_to_rent_type")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_workplace_setup_keyboard():
    keyboard = [
        [InlineKeyboardButton("Собрать и разобрать рабочее место", callback_data="workplace_setup")],
        [InlineKeyboardButton("Самостоятельная сборка и разборка рабочего места", callback_data="workplace_self")],
        [InlineKeyboardButton("Назад", callback_data="back_to_rent_type")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_after_booking_keyboard():
    keyboard = [
        [InlineKeyboardButton("Записаться на другую дату", callback_data="book_another")],
        [InlineKeyboardButton("Вернуться в меню", callback_data="back_to_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)

def get_payment_inline_confirmation_keyboard():
    keyboard = [
        [InlineKeyboardButton("Оплатил", callback_data="payment_done")]
    ]
    return InlineKeyboardMarkup(keyboard)

# =================================================================================
# --- HELPER FUNCTIONS ---
# =================================================================================

async def safe_send_animation(context: ContextTypes.DEFAULT_TYPE, chat_id: int, gif_name: str, caption: str, reply_markup=None, parse_mode=None):
    gif_path = os.path.join(GIFS_DIR, gif_name)
    try:
        with open(gif_path, 'rb') as gif:
            await context.bot.send_animation(chat_id, animation=gif, caption=caption, reply_markup=reply_markup, parse_mode=parse_mode)
    except Exception as e:
        logger.warning(f"Could not send GIF {gif_name}. Reason: {e}. Falling back to text.")
        try:
            await context.bot.send_message(chat_id, text=caption, reply_markup=reply_markup, parse_mode=parse_mode, disable_web_page_preview=True)
        except Exception as e_text:
            logger.error(f"Fallback text message also failed. Reason: {e_text}")

def is_on_cooldown(context: ContextTypes.DEFAULT_TYPE, command_key: str) -> bool:
    now = time.time()
    last_call = context.user_data.get(f'last_call_{command_key}', 0)
    if now - last_call < COMMAND_COOLDOWN:
        logger.info(f"Cooldown active for user {context._user_id} on command '{command_key}'.")
        return True
    context.user_data[f'last_call_{command_key}'] = now
    return False

# --- Rent Helpers ---
def generate_calendar_keyboard(year: int, month: int):
    keyboard = []
    month_name = RUSSIAN_MONTHS[month]
    header = [InlineKeyboardButton(f"{month_name} {year}", callback_data="ignore")]
    keyboard.append(header)
    week_days = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"]
    keyboard.append([InlineKeyboardButton(day, callback_data="ignore") for day in week_days])
    first_day = datetime.date(year, month, 1)
    days_in_month = calendar.monthrange(year, month)[1]
    start_weekday = (first_day.weekday() + 1) % 7
    row = []
    for _ in range(start_weekday):
        row.append(InlineKeyboardButton(" ", callback_data="ignore"))
    for day in range(1, days_in_month + 1):
        callback_data = f"date_{year}_{month}_{day}"
        row.append(InlineKeyboardButton(str(day), callback_data=callback_data))
        if len(row) == 7:
            keyboard.append(row)
            row = []
    if row:
        for _ in range(7 - len(row)):
            row.append(InlineKeyboardButton(" ", callback_data="ignore"))
        keyboard.append(row)
    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    next_month = month + 1 if month < 12 else 1
    next_year = year if month < 12 else year + 1
    nav_buttons = [
        InlineKeyboardButton("◀️", callback_data=f"nav_{prev_year}_{prev_month}"),
        InlineKeyboardButton("▶️", callback_data=f"nav_{next_year}_{next_month}")
    ]
    keyboard.append(nav_buttons)
    return InlineKeyboardMarkup(keyboard)

async def get_available_slots_count(worksheet, date_header: str) -> int:
    try:
        cache_key = f"{worksheet.title}_{date_header}_slots"
        now = time.time()
        if cache_key in sheets_cache:
            count, timestamp = sheets_cache[cache_key]
            if now - timestamp < CACHE_TIMEOUT:
                return count
        for attempt in range(MAX_RETRIES):
            try:
                date_cells = await asyncio.to_thread(worksheet.findall, date_header, in_column=1)
                if not date_cells:
                    sheets_cache[cache_key] = (6, now)
                    return 6
                date_cell = date_cells[0]
                # Получаем больше строк для анализа (до 20 строк после даты)
                day_block_data = await asyncio.to_thread(worksheet.get, f'A{date_cell.row}:D{date_cell.row + 20}')
                
                active_bookings = 0
                max_slots = 6  # Максимальное количество мест в день
                
                for i in range(2, min(len(day_block_data), 20)):
                    row_data = day_block_data[i]
                    if not row_data:
                        continue
                        
                    first_cell_value = row_data[0] if row_data else ""
                    # Если нашли следующую дату - прерываем
                    if first_cell_value and re.match(r'^\d{1,2}\s+\w+', str(first_cell_value).strip()):
                        break
                    
                    # Проверяем статус записи
                    status = row_data[3] if len(row_data) > 3 else ""
                    # Считаем активными записи с любым статусом, кроме отмененных
                    if status and status.lower() not in ['отменен', 'отмена', 'canceled']:
                        # Проверяем, что это действительно запись (есть имя или id)
                        master_info = row_data[0] if len(row_data) > 0 else ""
                        if master_info and (re.search(r'id:\d+', str(master_info)) or 
                                          re.search(r'@\w+', str(master_info)) or
                                          len(str(master_info).strip()) > 3):
                            active_bookings += 1
                
                available_slots = max_slots - active_bookings
                sheets_cache[cache_key] = (available_slots, now)
                return available_slots
                
            except APIError as e:
                if e.response.status_code == 429:
                    delay = BASE_RETRY_DELAY * (2 ** attempt)
                    logger.warning(f"Quota exceeded in get_available_slots_count for {date_header}. Retrying in {delay} seconds... (Attempt {attempt + 1}/{MAX_RETRIES})")
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"API error in get_available_slots_count: {e}")
                    return 0
            except Exception as e:
                logger.error(f"Error in get_available_slots_count: {e}")
                return 0
        logger.error(f"Failed to get available slots for {date_header} after {MAX_RETRIES} retries")
        return 0
    except Exception as e:
        logger.error(f"Unexpected error in get_available_slots_count: {e}")
        return 0

async def get_recent_worksheets():
    try:
        today = datetime.date.today()
        thirty_days_ago = today - datetime.timedelta(days=30)
        worksheets_to_check = []
        months_to_check = set()
        current_date = thirty_days_ago
        while current_date <= today + datetime.timedelta(days=31):
            months_to_check.add((current_date.year, current_date.month))
            current_date += datetime.timedelta(days=1)
        for year, month in months_to_check:
            sheet_name = f"{RUSSIAN_MONTHS[month]} {year}"
            worksheets_to_check.append(sheet_name)
        worksheets = []
        for sheet_name in worksheets_to_check:
            for attempt in range(MAX_RETRIES):
                try:
                    worksheet = await get_worksheet_cached(sheet_name)
                    if worksheet:
                        worksheets.append(worksheet)
                    break
                except APIError as e:
                    if e.response.status_code == 429:
                        delay = BASE_RETRY_DELAY * (2 ** attempt)
                        logger.warning(f"Quota exceeded for worksheet {sheet_name}. Retrying in {delay} seconds... (Attempt {attempt + 1}/{MAX_RETRIES})")
                        await asyncio.sleep(delay)
                    else:
                        logger.error(f"API error getting worksheet {sheet_name}: {e}")
                        break
                except Exception as e:
                    logger.error(f"Error getting worksheet {sheet_name}: {e}")
                    break
        return worksheets
    except Exception as e:
        logger.error(f"Error getting recent worksheets: {e}")
        return []

async def search_user_bookings_in_worksheet(worksheet, user_id: int):
    user_bookings = []
    try:
        for attempt in range(MAX_RETRIES):
            try:
                all_data = await asyncio.to_thread(worksheet.get_all_values)
                user_pattern = f"id:{user_id}"
                current_date = None
                year = int(worksheet.title.split()[-1])

                for row_idx, row in enumerate(all_data, 1):
                    if not row or len(row) < 4:
                        continue
                    if row[0] == "Мастер":
                        continue
                    if row[0] and re.match(r'^\d{1,2}\s+\w+', row[0].strip()):
                        current_date = row[0].strip()
                        continue
                    if row[0] and user_pattern in row[0]:
                        status = row[3] if len(row) > 3 else ""
                        if status == 'активна':
                            time_info = row[1] if len(row) > 1 else ""
                            rent_type = "почасовая" if "почасовая" in str(time_info).lower() else "фулл"
                            workplace_setup = ""
                            if "(сборка)" in str(time_info):
                                workplace_setup = "сборка"
                            elif "(самостоят)" in str(time_info):
                                workplace_setup = "самостоят"
                            if not current_date:
                                for i in range(max(1, row_idx-10), row_idx):
                                    if i-1 < len(all_data):
                                        check_row = all_data[i-1]
                                        if check_row[0] and re.match(r'^\d{1,2}\s+\w+', check_row[0].strip()):
                                            current_date = check_row[0].strip()
                                            break
                                if not current_date:
                                    current_date = "Дата не определена"
                            try:
                                day, month_name = current_date.split()
                                day = int(day)
                                month = next(k for k, v in RUSSIAN_MONTHS.items() if v.lower() == month_name.lower())
                                booking_date = datetime.date(year, month, day)
                                formatted_date = f"{day:02d}.{month:02d}.{year}"
                            except Exception as e:
                                logger.warning(f"Error parsing date '{current_date}' in worksheet {worksheet.title}: {e}")
                                booking_date = None
                                formatted_date = current_date
                            user_bookings.append({
                                'row': row_idx,
                                'date': formatted_date,
                                'raw_date': current_date,
                                'booking_date': booking_date,
                                'time': time_info.strip() if time_info else "",
                                'worksheet': worksheet.title,
                                'rent_type': rent_type,
                                'workplace_setup': workplace_setup
                            })
                return user_bookings
            except APIError as e:
                if e.response.status_code == 429:
                    delay = BASE_RETRY_DELAY * (2 ** attempt)
                    logger.warning(f"Quota exceeded in search_user_bookings_in_worksheet for {worksheet.title}. Retrying in {delay} seconds... (Attempt {attempt + 1}/{MAX_RETRIES})")
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"API error in search_user_bookings_in_worksheet: {e}")
                    return []
            except Exception as e:
                logger.error(f"Error in search_user_bookings_in_worksheet: {e}")
                return []
        logger.error(f"Failed to search bookings in {worksheet.title} after {MAX_RETRIES} retries")
        return []
    except Exception as e:
        logger.error(f"Unexpected error in search_user_bookings_in_worksheet: {e}")
        return []

async def get_user_bookings(user_id: int):
    try:
        user_bookings = []
        worksheets = await get_recent_worksheets()
        today = datetime.date.today()
        thirty_days_ago = today - datetime.timedelta(days=30)
        for worksheet in worksheets:
            worksheet_bookings = await search_user_bookings_in_worksheet(worksheet, user_id)
            for booking in worksheet_bookings:
                if booking['booking_date'] and booking['booking_date'] >= thirty_days_ago:
                    user_bookings.append(booking)
        user_bookings.sort(key=lambda x: x['booking_date'] if x['booking_date'] else datetime.date.min)
        return user_bookings
    except Exception as e:
        logger.error(f"Error getting user bookings: {e}")
        return []

async def get_user_bookings_for_payment(user_id: int):
    try:
        user_bookings = []
        worksheets = await get_recent_worksheets()
        today = datetime.date.today()
        thirty_days_ago = today - datetime.timedelta(days=30)
        for worksheet in worksheets:
            worksheet_bookings = await search_user_bookings_in_worksheet(worksheet, user_id)
            for booking in worksheet_bookings:
                if booking['booking_date'] and booking['booking_date'] >= thirty_days_ago:
                    worksheet_obj = await get_worksheet_cached(booking['worksheet'])
                    if worksheet_obj:
                        for attempt in range(MAX_RETRIES):
                            try:
                                payment_status = (await asyncio.to_thread(worksheet_obj.cell, booking['row'], 3)).value
                                if payment_status == "нет":
                                    user_bookings.append(booking)
                                break
                            except APIError as e:
                                if e.response.status_code == 429:
                                    delay = BASE_RETRY_DELAY * (2 ** attempt)
                                    logger.warning(f"Quota exceeded in get_user_bookings_for_payment for {booking['worksheet']}. Retrying in {delay} seconds... (Attempt {attempt + 1}/{MAX_RETRIES})")
                                    await asyncio.sleep(delay)
                                else:
                                    logger.error(f"API error in get_user_bookings_for_payment: {e}")
                                    break
                            except Exception as e:
                                logger.error(f"Error in get_user_bookings_for_payment: {e}")
                                break
        user_bookings.sort(key=lambda x: x['booking_date'] if x['booking_date'] else datetime.date.min)
        return user_bookings
    except Exception as e:
        logger.error(f"Error getting user bookings for payment: {e}")
        return []

# =================================================================================
# --- MAIN MENU & STATE ROUTER ---
# =================================================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if is_on_cooldown(context, 'start'):
        return
    context.user_data['state'] = 'main_menu'
    caption = (
        "[ IKONA AI ]\n"
        "──────────────\n"
        "Система активирована. Я — ИИ-ассистент тату-салона IKONA. Чем могу быть полезна? Выберите опцию ниже."
    )
    await safe_send_animation(context, update.effective_chat.id, '1.gif', caption, get_main_menu_keyboard())

async def route_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state = context.user_data.get('state', 'main_menu')
    text = update.message.text if update.message and update.message.text else ""

    if text == "Главное меню" or text.startswith("Назад ("):
        await start(update, context)
        return

    if state == 'tattoo_awaiting_idea':
        await handle_tattoo_idea_input(update, context)
        return

    if state == 'main_menu':
        if text == "Запись на тату": await handle_book_tattoo_start(update, context)
        elif text == "Запись на аренду": await handle_rent_booking_start(update, context)
        elif text == "Купить": await handle_buy_start(update, context)
        elif text == "Чат": await handle_chat_start(update, context)
        elif text == "Обучение": await handle_training_start(update, context)
    elif 'tattoo' in state: await route_tattoo(update, context)
    elif 'buy' in state: await route_buy(update, context)
    elif 'chat' in state: await route_chat(update, context)
    elif 'training' in state: await route_training(update, context)
    elif 'rent' in state: await route_rent(update, context)

async def route_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state = context.user_data.get('state')
    if state == 'tattoo_awaiting_idea': await handle_tattoo_idea_input(update, context)
    elif state == 'buy_awaiting_receipt': await handle_receipt(update, context)
    elif state == 'rent_waiting_for_receipt': await handle_rent_receipt_upload(update, context)

# =================================================================================
# --- TATTOO BOOKING MODULE ---
# =================================================================================

async def route_tattoo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state = context.user_data.get('state')
    if state == 'tattoo_booking_menu': await handle_tattoo_booking_choice(update, context)
    elif state == 'tattoo_choosing_style': await handle_sketch_style_selection(update, context)
    elif state == 'tattoo_viewing_sketch': await handle_sketch_navigation(update, context)
    elif state in ['tattoo_awaiting_date_for_sketch', 'tattoo_awaiting_date_for_idea']: await handle_tattoo_date_input(update, context)

async def handle_book_tattoo_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if is_on_cooldown(context, 'book_tattoo'):
        return
    context.user_data['state'] = 'tattoo_booking_menu'
    caption = (
        "[ IKONA AI ]\n"
        "──────────────\n"
        "Анализирую... Вы желаете запечатлеть на себе частичку искусства. Отличный выбор. У вас есть своя идея или вы хотите выбрать из моих эскизов?"
    )
    await safe_send_animation(context, update.effective_chat.id, '2.gif', caption, get_tattoo_booking_keyboard())

async def handle_tattoo_booking_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "Прислать идею":
        context.user_data['state'] = 'tattoo_awaiting_idea'
        await update.message.reply_text("Опишите свою тату! Напишите место нанесения и идею эскиза или пришлите фото!", reply_markup=ReplyKeyboardRemove())
    elif text == "Выбрать свободный эскиз":
        context.user_data['state'] = 'tattoo_choosing_style'
        await update.message.reply_text("Выберите стиль эскиза:", reply_markup=get_sketch_style_keyboard())

async def handle_sketch_style_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    style = update.message.text
    context.user_data['state'] = 'tattoo_viewing_sketch'
    context.user_data['sketch_index'] = {'style': style, 'index': 0}
    sketches = {"Аниме": anime_sketches, "Трайблы": tribal_sketches, "Другое": other_sketches}.get(style, [])
    if not sketches:
        await update.message.reply_text(f"В папке '{style}' пока нет эскизов.", reply_markup=get_sketch_style_keyboard())
        context.user_data['state'] = 'tattoo_choosing_style'
        return
    await send_next_sketch(update, context, style, sketches)

async def send_next_sketch(update: Update, context: ContextTypes.DEFAULT_TYPE, style: str, sketches: list):
    current_index = context.user_data.get('sketch_index', {}).get('index', 0)
    sketch_path = sketches[current_index]
    context.user_data['sketch_path'] = sketch_path
    with open(sketch_path, 'rb') as photo:
        await update.message.reply_photo(photo, reply_markup=get_sketch_navigation_keyboard())

async def handle_sketch_navigation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "Следующий свободный эскиз":
        info = context.user_data.get('sketch_index')
        style = info['style']
        sketches = {"Аниме": anime_sketches, "Трайблы": tribal_sketches, "Другое": other_sketches}.get(style, [])
        if not sketches:
            await update.message.reply_text(f"В папке '{style}' пока нет эскизов.", reply_markup=get_sketch_style_keyboard())
            context.user_data['state'] = 'tattoo_choosing_style'
            return
        info['index'] = (info.get('index', 0) + 1) % len(sketches)
        await send_next_sketch(update, context, style, sketches)
    elif text == "Выбрать":
        sketch_path = context.user_data.get('sketch_path')
        with open(sketch_path, 'rb') as photo:
            await update.message.reply_photo(photo, caption="Забронирован", reply_markup=ReplyKeyboardRemove())
        await update.message.reply_text("Отлично! Теперь пришлите желаемую дату для нанесения в формате (ДД.ММ), например, 07.07")
        context.user_data['state'] = 'tattoo_awaiting_date_for_sketch'

async def handle_tattoo_idea_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    idea_text = update.message.caption if update.message.photo else update.message.text
    photo_file_id = update.message.photo[-1].file_id if update.message.photo else None
    context.user_data['idea_details'] = {'idea_text': idea_text, 'photo_file_id': photo_file_id}
    context.user_data['state'] = 'tattoo_awaiting_date_for_idea'
    await update.message.reply_text("Отлично! Теперь пришлите желаемую дату для сеанса в формате (ДД.ММ), например, 07.07")

async def handle_tattoo_date_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    booking_date = update.message.text
    user = update.effective_user
    state = context.user_data['state']
    admin_message, photo_to_send = "", None
    if state == 'tattoo_awaiting_date_for_sketch':
        sketch_path = context.user_data.get('sketch_path', "Не выбран")
        admin_message = f"**НОВАЯ ЗАПИСЬ (ЭСКИЗ)**\n**Пользователь:** @{user.username or user.id}\n**Эскиз:** `{os.path.basename(sketch_path)}`\n**Дата:** `{booking_date}`"
        if os.path.exists(sketch_path): photo_to_send = open(sketch_path, 'rb')
    elif state == 'tattoo_awaiting_date_for_idea':
        idea_info = context.user_data.get('idea_details')
        admin_message = f"**НОВАЯ ЗАПИСЬ (ИДЕЯ)**\n**Пользователь:** @{user.username or user.id}\n**Идея:** `{idea_info['idea_text']}`\n**Дата:** `{booking_date}`"
        photo_to_send = idea_info['photo_file_id']
    if photo_to_send:
        if isinstance(photo_to_send, str):
            await context.bot.send_photo(ADMIN_CHAT_ID, photo_to_send, caption=admin_message, parse_mode=ParseMode.MARKDOWN)
        else:
            await context.bot.send_photo(ADMIN_CHAT_ID, photo_to_send, caption=admin_message, parse_mode=ParseMode.MARKDOWN)
            photo_to_send.close()
    else:
        await context.bot.send_message(ADMIN_CHAT_ID, admin_message, parse_mode=ParseMode.MARKDOWN)
    await update.message.reply_text("Вас проконсультируют в течение ближайшего времени! Или можете написать сразу! @vladguro", reply_markup=get_main_menu_keyboard())
    context.user_data.clear()
    context.user_data['state'] = 'main_menu'

# =================================================================================
# --- BUY MODULE ---
# =================================================================================

async def route_buy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state = context.user_data.get('state')
    text = update.message.text if update.message and update.message.text else ""
    if state == 'buy_menu': await handle_buy_choice(update, context)
    elif state == 'buy_choosing_supply': await handle_supply_choice(update, context)
    elif state == 'buy_viewing_merch': await handle_merch_navigation(update, context)
    elif state == 'buy_awaiting_receipt' and text == "Я оплатил(а) ✅": await process_final_confirmation(update, context)
    elif state == 'buy_awaiting_receipt' and text == "Отмена оплаты": await cancel_payment(update, context)

async def handle_buy_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if is_on_cooldown(context, 'buy'):
        return
    context.user_data['state'] = 'buy_menu'
    caption = (
        "[ IKONA AI ]\n"
        "──────────────\n"
        "Открываю торговый терминал. Здесь вы можете приобрести наш эксклюзивный мерч, расходные материалы и другие полезные вещи."
    )
    await safe_send_animation(context, update.effective_chat.id, '5.gif', caption, get_buy_menu_keyboard())

async def handle_buy_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    item_info = ITEM_MAP.get(text)

    if text == "Мерч":
        if not MERCH_ITEMS:
            await update.message.reply_text("Извините, мерч временно закончился.", reply_markup=get_buy_menu_keyboard())
            return
        context.user_data.update({'state': 'buy_viewing_merch', 'merch_index': 0})
        await update.message.reply_text("Смотрите, что у нас есть!", reply_markup=get_merch_menu_keyboard())
        await send_merch_item(update, context)
    elif item_info:
        await start_payment_process(update, context, text, item_info['price'])
    elif text == "Расходка":
        context.user_data['state'] = 'buy_choosing_supply'
        await update.message.reply_text("Выберите расходный материал:", reply_markup=get_supplies_menu_keyboard())

async def handle_supply_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    item_info = ITEM_MAP.get(text)
    if item_info:
        await start_payment_process(update, context, text, item_info['price'])
    else:
        await update.message.reply_text("Пожалуйста, выберите товар из списка.")

async def handle_merch_navigation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "Следующий мерч":
        context.user_data['merch_index'] = (context.user_data.get('merch_index', 0) + 1) % len(MERCH_ITEMS)
        await send_merch_item(update, context)
    elif text == "Оплатить мерч":
        index = context.user_data.get('merch_index', 0)
        item = MERCH_ITEMS[index]
        await start_payment_process(update, context, item['name'], item['price'])

async def send_merch_item(update: Update, context: ContextTypes.DEFAULT_TYPE):
    index = context.user_data.get('merch_index', 0)
    item = MERCH_ITEMS[index]
    with open(item['photo'], 'rb') as photo:
        caption = f"{item['caption']}\n\nЦена: {item['price']} руб.\nТовар {index + 1} из {len(MERCH_ITEMS)}"
        await update.message.reply_photo(photo, caption=caption)

async def start_payment_process(update: Update, context: ContextTypes.DEFAULT_TYPE, item_name: str, item_price: int):
    context.user_data.update({'state': 'buy_awaiting_receipt', 'item_name': item_name})
    payment_text = (
        f"Покупка: *{item_name}*\n"
        f"Сумма: *{item_price} руб.*\n\n"
        f"💳 Оплата по номеру телефона Т-Банк!\n`{PAYMENT_PHONE_NUMBER}`\n\n"
        f"Если не проходит оплата, напишите сюда: {PAYMENT_CONTACT}, будут выданы новые реквизиты.\n\n"
        "Пожалуйста, **сначала пришлите чек об оплате в этот чат** (фото или PDF), затем нажмите кнопку подтверждения."
    )
    await update.message.reply_text(payment_text, parse_mode=ParseMode.MARKDOWN, reply_markup=get_payment_confirmation_keyboard())

async def handle_receipt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['receipt_message_id'] = update.message.message_id
    await update.message.reply_text("✅ Чек получен. Теперь нажмите 'Я оплатил(а) ✅', чтобы завершить покупку.")

async def process_final_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    if 'receipt_message_id' not in context.user_data:
        await update.message.reply_text("Сначала пришлите чек, пожалуйста.")
        return

    loading_message = await update.message.reply_text("⏳ Подтверждаем покупку...")
    try:
        item_name = context.user_data.get('item_name')
        user = update.effective_user
        user_info_text = f"Новая оплата от @{user.username}" if user.username else f"Новая оплата от ID {user.id}"
        await context.bot.send_message(ADMIN_CHAT_ID, f"{user_info_text}\nТовар: {item_name}")
        await context.bot.forward_message(ADMIN_CHAT_ID, user_id, context.user_data['receipt_message_id'])

        caption = (
            "[ IKONA AI ]\n"
            "──────────────\n"
            "Транзакция успешно завершена. Информация о покупке передана администратору. Благодарю за выбор IKONA."
        )
        await safe_send_animation(context, user_id, '7.gif', caption, get_main_menu_keyboard())
    except Exception as e:
        await update.message.reply_text(f"Произошла ошибка при подтверждении: {e}")
        logger.error(f"Error in process_final_confirmation: {e}")
    finally:
        await loading_message.delete()
        context.user_data.clear()
        context.user_data['state'] = 'main_menu'

async def cancel_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Покупка отменена.", reply_markup=get_buy_menu_keyboard())
    context.user_data['state'] = 'buy_menu'

# =================================================================================
# --- CHAT MODULE (REFACTORED FOR STABILITY) ---
# =================================================================================

async def route_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state = context.user_data.get('state')
    if state == 'chat_menu':
        await handle_chat_choice(update, context)
    elif state == 'ai_chat':
        await handle_ai_message(update, context)

async def handle_chat_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if is_on_cooldown(context, 'chat'):
        return
    context.user_data['state'] = 'chat_menu'
    caption = (
        "[ IKONA AI ]\n"
        "──────────────\n"
        "Вы вошли в коммуникационный модуль. Здесь вы можете связаться с другими мастерами, техподдержкой или напрямую со мной, IKONA AI. Для общения со мной выберите 'IKONA AI Wuifu'."
    )
    await safe_send_animation(context, update.effective_chat.id, '5.gif', caption, get_chat_menu_keyboard())

async def handle_chat_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "IKONA AI Wuifu":
        context.user_data.update({
            'state': 'ai_chat',
            'history': [GYARU_PROMPT],
            'ai_lock': asyncio.Lock()
        })
        await update.message.reply_text("Напишите ваш вопрос IKONA AI Wuifu:", reply_markup=get_ai_chat_exit_keyboard())
    elif text == "Чат мастеров":
        await update.message.reply_text(f"Вот ссылка на чат: {MASTERS_CHAT_LINK}")
    elif text == "Тех. поддержка":
        await update.message.reply_text(f"Напишите сюда: {PAYMENT_CONTACT}")

async def handle_ai_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    chat_id = update.effective_chat.id

    if user_message == "Выйти из чата с AI":
        context.user_data.pop('ai_lock', None)
        context.user_data.pop('history', None)
        context.user_data['state'] = 'chat_menu'
        await update.message.reply_text("Вы вышли из чата с AI.", reply_markup=get_chat_menu_keyboard())
        return

    if 'ai_lock' not in context.user_data:
        context.user_data['ai_lock'] = asyncio.Lock()

    user_lock = context.user_data['ai_lock']

    if user_lock.locked():
        await update.message.reply_text("Подождите, я еще думаю над предыдущим вопросом...")
        return

    async with user_lock:
        await context.bot.send_chat_action(chat_id=chat_id, action=ChatAction.TYPING)

        history = context.user_data.get('history', [GYARU_PROMPT])
        history.append({"role": "user", "content": user_message})

        headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}"}
        payload = {"model": "deepseek/deepseek-chat:free", "messages": history, "temperature": 1.3}

        try:
            http_client = context.bot_data['http_client']
            response = await http_client.post(OPENROUTER_API_URL, headers=headers, json=payload, timeout=45.0)
            response.raise_for_status()

            ai_response = response.json()["choices"][0]["message"]["content"]
            history.append({"role": "assistant", "content": ai_response})
            context.user_data['history'] = history

            novel_style_response = (
                f"[ IKONA AI // Режим: GYARU ]\n"
                f"──────────────\n"
                f"{ai_response}"
            )
            await safe_send_animation(context, chat_id, '2.gif', novel_style_response)

        except httpx.TimeoutException:
            logger.error(f"Timeout error with OpenRouter API for user {chat_id}")
            await context.bot.send_message(chat_id, "AI слишком долго думает и не отвечает. Попробуйте позже.")
        except httpx.RequestError as e:
            logger.error(f"Request error with OpenRouter API for user {chat_id}: {e}")
            await context.bot.send_message(chat_id, "AI временно недоступен из-за проблем с сетью. Попробуйте позже.")
        except Exception as e:
            logger.error(f"Generic error in handle_ai_message for user {chat_id}: {e}")
            await context.bot.send_message(chat_id, "Произошла внутренняя ошибка. AI временно недоступен.")
            context.user_data['history'] = [GYARU_PROMPT]

# =================================================================================
# --- TRAINING MODULE ---
# =================================================================================

async def route_training(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state = context.user_data.get('state')
    text = update.message.text
    if state == 'training_menu':
        await handle_training_choice(update, context)
    elif text in ["Записаться на Пробный Урок / Обучение", "Подробнее / Записаться на онлайн"]:
        await handle_training_signup(update, context)

async def handle_training_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if is_on_cooldown(context, 'training'):
        return
    context.user_data['state'] = 'training_menu'
    description = "**ОБУЧЕНИЕ ТАТУ IKONA**\n\nВыберите программу:"
    await context.bot.send_message(update.effective_chat.id, f"🎬 Обучение IKONA: {IKONA_TRAINING_VIDEO}")
    await update.message.reply_text(description, parse_mode=ParseMode.MARKDOWN, reply_markup=get_training_menu_keyboard())

async def handle_training_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "Оффлайн обучение IKONA":
        context.user_data['state'] = 'training_offline_details'
        description = "**ОФФЛАЙН ОБУЧЕНИЕ IKONA**\n**Москва и Санкт-Петербург**\n\n**УСЛОВИЯ:**\n⏱️ **Срок обучения:** 2 месяца\n💰 **Стоимость:** 99 000 рублей\n**БЕСПЛАТНЫЙ ПЕРВЫЙ УРОК!**"
        await context.bot.send_message(update.effective_chat.id, f"🎬 Оффлайн обучение: {OFFLINE_TRAINING_VIDEO}")
        await update.message.reply_text(description, parse_mode=ParseMode.MARKDOWN, reply_markup=get_offline_training_keyboard())
    elif text == "Онлайн обучение IKONA":
        context.user_data['state'] = 'training_online_details'
        description = "**ОНЛАЙН ОБУЧЕНИЕ IKONA**\n\n**УСЛОВИЯ:**\n⏱️ **Срок обучения:** 2 месяца\n💰 **Стоимость:** 79 000 рублей"
        await context.bot.send_message(update.effective_chat.id, f"🎬 Онлайн обучение: {ONLINE_TRAINING_VIDEO}")
        await update.message.reply_text(description, parse_mode=ParseMode.MARKDOWN, reply_markup=get_online_training_keyboard())
    elif text == "IKONA AI (Free) генератор эскизов":
        await context.bot.send_message(update.effective_chat.id, f"🎬 Посмотрите это видео:\n{IKONA_AI_VIDEO}")
        await update.message.reply_text("🤖 Для генерации эскизов перейдите в нашего специального бота:\n@OVERLORD_INK_AI_bot")

async def handle_training_signup(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_info = f"‼️ Новая заявка на обучение!\nТип: {update.message.text}\n👤 **Пользователь:** {user.first_name}\n🆔 **ID:** `{user.id}`\n🔗 **Username:** @{user.username if user.username else 'Не указан'}"
    await context.bot.send_message(ADMIN_CHAT_ID, user_info, parse_mode=ParseMode.MARKDOWN)
    await update.message.reply_text("✅ **Ваша заявка принята!**\nМы свяжемся с вами в ближайшее время.", parse_mode=ParseMode.MARKDOWN, reply_markup=get_training_menu_keyboard())
    context.user_data['state'] = 'training_menu'

# =================================================================================
# --- RENT BOOKING MODULE ---
# =================================================================================

async def route_rent(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state = context.user_data.get('state')
    text = update.message.text if update.message and update.message.text else ""
    if state == 'rent_booking_menu':
        await handle_rent_booking_choice(update, context)

async def handle_rent_booking_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if is_on_cooldown(context, 'rent_booking'):
        return
    context.user_data['state'] = 'rent_booking_menu'
    caption = (
        f"[ IKONA AI ]\n"
        f"──────────────\n"
        f"Запрос на аренду рабочего пространства. Все данные о свободных слотах синхронизированы с базой данных.\n\n"
        f"📊 [Посмотреть расписание](https://docs.google.com/spreadsheets/d/{GOOGLE_SHEET_ID}/edit?usp=sharing)"
    )
    await safe_send_animation(context, update.effective_chat.id, '3.gif', caption, get_rent_booking_menu(), parse_mode=ParseMode.MARKDOWN)

async def handle_rent_booking_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "Выбрать дату аренды":
        await show_calendar(update, context)
    elif text == "Оплата / Баланс":
        await show_user_bookings_for_payment(update, context)
    elif text == "Отменить запись":
        await show_user_bookings_for_cancellation(update, context)
    elif text == "Главное меню":
        await start(update, context)

async def show_calendar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    today = datetime.date.today()
    year = today.year
    month = today.month
    context.user_data['calendar_year'] = year
    context.user_data['calendar_month'] = month
    keyboard = generate_calendar_keyboard(year, month)
    if update.callback_query:
        await update.callback_query.edit_message_text(
            "Выберите дату для аренды:",
            reply_markup=keyboard
        )
    else:
        await update.message.reply_text(
            "Выберите дату для аренды:",
            reply_markup=keyboard
        )

async def handle_calendar_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    if data == "back_to_menu":
        context.user_data['state'] = 'rent_booking_menu'
        await query.message.reply_text("Возвращаюсь в меню аренды:", reply_markup=get_rent_booking_menu())
        return
    if data.startswith("nav_"):
        _, year, month = data.split("_")
        year, month = int(year), int(month)
        context.user_data['calendar_year'] = year
        context.user_data['calendar_month'] = month
        keyboard = generate_calendar_keyboard(year, month)
        await query.edit_message_text("Выберите дату для аренды:", reply_markup=keyboard)
        return
    if data.startswith("date_"):
        _, year, month, day = data.split("_")
        year, month, day = int(year), int(month), int(day)
        selected_date = datetime.date(year, month, day)
        today = datetime.date.today()
        keyboard = generate_calendar_keyboard(year, month)
        if selected_date < today:
            await query.answer("Эта дата уже прошла! Пожалуйста, выберите будущую дату.", show_alert=True)
            await query.message.reply_text("❌ Эта дата уже прошла! Пожалуйста, выберите будущую дату.", reply_markup=keyboard)
            return
        sheet_name = f"{RUSSIAN_MONTHS[month]} {year}"
        # Auto-create sheet if it doesn't exist
        worksheet = await create_sheet_if_not_exists(sheet_name)
        if not worksheet:
            await query.answer("Ошибка при создании расписания! Попробуйте позже.", show_alert=True)
            await query.message.reply_text("❌ Ошибка при создании расписания! Попробуйте позже.", reply_markup=keyboard)
            return
        date_header = f"{day} {RUSSIAN_MONTHS[month]}"
        available_slots = await get_available_slots_count(worksheet, date_header)
        
        if available_slots <= 0:
            await query.answer("Все места на эту дату заняты! Выберите другую дату.", show_alert=True)
            await query.message.reply_text("❌ Все места на эту дату заняты! Выберите другую дату.", reply_markup=keyboard)
            return
            
        context.user_data['selected_date'] = {
            'year': year,
            'month': month,
            'day': day,
            'header': date_header,
            'worksheet': sheet_name
        }
        
        await query.edit_message_text(
            f"📅 Выбрана дата: {day}.{month:02d}.{year}\n"
            f"🆓 Свободных мест: {available_slots}\n\n"
            f"Выберите время прихода:",
            reply_markup=get_time_slots_keyboard()
        )

async def handle_time_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "back_to_dates":
        await show_calendar(update, context)
        return
    if query.data.startswith("time_"):
        selected_time = query.data.replace("time_", "")
        context.user_data['selected_time'] = selected_time
        await query.edit_message_text(
            f"📅 Дата: {context.user_data['selected_date']['day']}.{context.user_data['selected_date']['month']:02d}.{context.user_data['selected_date']['year']}\n"
            f"⏰ Время: {selected_time}\n\n"
            f"Выберите тип аренды:",
            reply_markup=get_rent_type_keyboard()
        )

async def handle_rent_type_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "back_to_times":
        await query.edit_message_text(
            f"📅 Дата: {context.user_data['selected_date']['day']}.{context.user_data['selected_date']['month']:02d}.{context.user_data['selected_date']['year']}\n"
            f"⏰ Время: {context.user_data['selected_time']}\n\n"
            f"Выберите время прихода:",
            reply_markup=get_time_slots_keyboard()
        )
        return
    if query.data == "rent_type_hourly":
        await query.edit_message_text(
            f"📅 Дата: {context.user_data['selected_date']['day']}.{context.user_data['selected_date']['month']:02d}.{context.user_data['selected_date']['year']}\n"
            f"⏰ Время: {context.user_data['selected_time']}\n\n"
            f"Выберите количество часов:",
            reply_markup=get_hours_selection_keyboard()
        )
    else:
        rent_type = "фулл" if query.data == "rent_type_full" else "почасовая"
        context.user_data['rent_type'] = rent_type
        if rent_type == "фулл":
            context.user_data['selected_hours'] = "фулл день"
            context.user_data['selected_price'] = 2500
        await query.edit_message_text(
            f"📅 Дата: {context.user_data['selected_date']['day']}.{context.user_data['selected_date']['month']:02d}.{context.user_data['selected_date']['year']}\n"
            f"⏰ Время: {context.user_data['selected_time']}\n"
            f"💰 Тип аренды: {rent_type}\n\n"
            f"Выберите тип сборки рабочего места:",
            reply_markup=get_workplace_setup_keyboard()
        )

async def handle_hours_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "back_to_rent_type":
        await query.edit_message_text(
            f"📅 Дата: {context.user_data['selected_date']['day']}.{context.user_data['selected_date']['month']:02d}.{context.user_data['selected_date']['year']}\n"
            f"⏰ Время: {context.user_data['selected_time']}\n\n"
            f"Выберите тип аренды:",
            reply_markup=get_rent_type_keyboard()
        )
        return
    if query.data.startswith("hours_"):
        hours = query.data.replace("hours_", "")
        if hours == "2":
            price = 1300
            hours_text = "2 часа"
        elif hours == "3":
            price = 1950
            hours_text = "3 часа"
        else:
            price = 2500
            hours_text = "4 часа и более"
        context.user_data['rent_type'] = "почасовая"
        context.user_data['selected_hours'] = hours_text
        context.user_data['selected_price'] = price
        await query.edit_message_text(
            f"📅 Дата: {context.user_data['selected_date']['day']}.{context.user_data['selected_date']['month']:02d}.{context.user_data['selected_date']['year']}\n"
            f"⏰ Время: {context.user_data['selected_time']}\n"
            f"💰 Тип аренды: почасовая\n"
            f"⏱ Количество часов: {hours_text}\n\n"
            f"Выберите тип сборки рабочего места:",
            reply_markup=get_workplace_setup_keyboard()
        )

async def handle_workplace_setup_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "back_to_rent_type":
        await query.edit_message_text(
            f"📅 Дата: {context.user_data['selected_date']['day']}.{context.user_data['selected_date']['month']:02d}.{context.user_data['selected_date']['year']}\n"
            f"⏰ Время: {context.user_data['selected_time']}\n\n"
            f"Выберите тип аренды:",
            reply_markup=get_rent_type_keyboard()
        )
        return
    if query.data.startswith("workplace_"):
        workplace_type = query.data.replace("workplace_", "")
        context.user_data['workplace_setup'] = workplace_type
        await process_rent_booking_final(update, context)

async def process_rent_booking_final(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    loading_message = await query.message.reply_text("⏳ Записываю вас...")
    try:
        date_info = context.user_data['selected_date']
        selected_time = context.user_data['selected_time']
        rent_type = context.user_data['rent_type']
        hours_text = context.user_data.get('selected_hours', '')
        price = context.user_data.get('selected_price', 0)
        workplace_setup = context.user_data.get('workplace_setup', '')
        
        # Auto-create sheet if it doesn't exist
        worksheet = await create_sheet_if_not_exists(date_info['worksheet'])
        if not worksheet:
            await query.answer("❌ Ошибка при создании расписания! Попробуйте позже.", show_alert=True)
            return
            
        date_header = date_info['header']
        for attempt in range(MAX_RETRIES):
            try:
                date_cells = await asyncio.to_thread(worksheet.findall, date_header, in_column=1)
                if not date_cells:
                    await query.answer("Дата не найдена в расписании!", show_alert=True)
                    return
                date_cell = date_cells[0]
                day_block_data = await asyncio.to_thread(worksheet.get, f'A{date_cell.row}:D{date_cell.row + 20}')
                first_empty_row = -1
                for i in range(2, min(len(day_block_data), 20)):
                    row_data = day_block_data[i]
                    first_cell_value = row_data[0] if row_data else ""
                    if first_cell_value and re.match(r'^\d{1,2}\s', str(first_cell_value)):
                        break
                    if not first_cell_value and first_empty_row == -1:
                        first_empty_row = date_cell.row + i
                        break
                if first_empty_row == -1:
                    await query.answer("На эту дату нет свободных мест!", show_alert=True)
                    return
                master_name = f"@{query.from_user.username} (id:{user_id})" if query.from_user.username else f"id:{user_id}"
                if rent_type == "почасовая":
                    time_display = f"{selected_time} {rent_type} ({hours_text})"
                else:
                    time_display = f"{selected_time} {rent_type}"
                
                # Добавляем информацию о сборке рабочего места
                if workplace_setup == "setup":
                    time_display += " (сборка)"
                elif workplace_setup == "self":
                    time_display += " (самостоят)"
                    
                await asyncio.to_thread(worksheet.update, f'A{first_empty_row}:D{first_empty_row}', 
                                       [[master_name, time_display, "нет", "активна"]])
                cache_key = f"{worksheet.title}_{date_header}_slots"
                if cache_key in sheets_cache:
                    del sheets_cache[cache_key]
                confirmation_text = (
                    f"✅ **Запись подтверждена!**\n\n"
                    f"📅 **Дата:** {date_info['day']}.{date_info['month']:02d}.{date_info['year']}\n"
                    f"⏰ **Время:** {selected_time}\n"
                    f"💰 **Тип аренды:** {rent_type}"
                )
                if rent_type == "почасовая":
                    confirmation_text += f"\n⏱ **Количество часов:** {hours_text}"
                confirmation_text += f"\n🏗 **Сборка рабочего места:** {'Собрать и разобрать' if workplace_setup == 'setup' else 'Самостоятельная'}"
                confirmation_text += f"\n💵 **Стоимость:** {price}р"
                confirmation_text += f"\n\n📊 [Посмотреть расписание](https://docs.google.com/spreadsheets/d/{GOOGLE_SHEET_ID}/edit?usp=sharing)"
                await query.message.reply_text(confirmation_text, 
                                             parse_mode=ParseMode.MARKDOWN, 
                                             disable_web_page_preview=True,
                                             reply_markup=get_after_booking_keyboard())
                break
            except APIError as e:
                if e.response.status_code == 429:
                    delay = BASE_RETRY_DELAY * (2 ** attempt)
                    logger.warning(f"Quota exceeded in process_rent_booking_final for {date_header}. Retrying in {delay} seconds... (Attempt {attempt + 1}/{MAX_RETRIES})")
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"API error in process_rent_booking_final: {e}")
                    await query.answer("❌ Временная ошибка API Google Sheets. Попробуйте снова через минуту.", show_alert=True)
                    return
            except Exception as e:
                logger.error(f"Error in process_rent_booking_final: {e}")
                await query.answer("Ошибка при записи!", show_alert=True)
                return
    except Exception as e:
        logger.error(f"Unexpected error in process_rent_booking_final: {e}")
        await query.answer("❌ Временная ошибка API Google Sheets. Попробуйте снова через минуту.", show_alert=True)
    finally:
        await loading_message.delete()

async def show_user_bookings_for_cancellation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    loading_message = await update.message.reply_text("⏳ Ищу ваши бронирования...")
    try:
        all_bookings = await get_user_bookings(user_id)
        if not all_bookings:
            await update.message.reply_text("У вас нет активных бронирований за последние 30 дней.", reply_markup=get_rent_booking_menu())
            return
        keyboard = []
        for booking in all_bookings:
            btn_text = f"{booking['date']} {booking['time']}"
            callback_data = f"cancel_{booking['worksheet']}_{booking['row']}"
            keyboard.append([InlineKeyboardButton(btn_text, callback_data=callback_data)])
        markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Выберите бронирование для отмены:", reply_markup=markup)
    except Exception as e:
        logger.error(f"Error showing user bookings: {e}")
        await update.message.reply_text("❌ Временная ошибка API Google Sheets. Попробуйте снова через минуту.", reply_markup=get_rent_booking_menu())
    finally:
        await loading_message.delete()

async def handle_booking_cancellation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data.startswith("cancel_"):
        _, worksheet_name, row = query.data.split("_")
        row = int(row)
        loading_message = await query.message.reply_text("⏳ Отменяю бронирование...")
        try:
            worksheet = await get_worksheet_cached(worksheet_name)
            if not worksheet:
                await query.answer("Ошибка доступа к расписанию!", show_alert=True)
                return
            for attempt in range(MAX_RETRIES):
                try:
                    row_data = await asyncio.to_thread(worksheet.row_values, row)
                    date_info = "Неизвестная дата"
                    for i in range(max(row-10, 1), row):
                        val_cell = await asyncio.to_thread(worksheet.cell, i, 1)
                        val = val_cell.value
                        if val and re.match(r'^\d{1,2}\s', val):
                            date_info = val
                            break
                    master_name = row_data[0] if len(row_data) > 0 else ""
                    time_info = row_data[1] if len(row_data) > 1 else ""
                    cancel_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    canceled_data = f"{master_name} | {time_info} | отменена {cancel_time}"
                    await asyncio.to_thread(worksheet.update, f'A{row}:E{row}', 
                                          [["", "", "", "отменен", canceled_data]])
                    for cache_key in list(sheets_cache.keys()):
                        if cache_key.startswith(worksheet_name):
                            del sheets_cache[cache_key]
                    try:
                        day, month_name = date_info.split()
                        day = int(day)
                        month = next(k for k, v in RUSSIAN_MONTHS.items() if v.lower() == month_name.lower())
                        year = int(worksheet_name.split()[-1])
                        formatted_date = f"{day:02d}.{month:02d}.{year}"
                    except:
                        formatted_date = date_info
                    await query.message.reply_text(
                        f"✅ **Бронирование отменено!**\n\n"
                        f"📅 **Дата:** {formatted_date}\n"
                        f"❌ **Статус:** Отменено\n\n"
                        f"Место освобождено для других пользователей.\n\n"
                        f"Возвращаюсь в меню аренды:",
                        reply_markup=get_rent_booking_menu()
                    )
                    context.user_data['state'] = 'rent_booking_menu'
                    break
                except APIError as e:
                    if e.response.status_code == 429:
                        delay = BASE_RETRY_DELAY * (2 ** attempt)
                        logger.warning(f"Quota exceeded in handle_booking_cancellation for {worksheet_name}. Retrying in {delay} seconds... (Attempt {attempt + 1}/{MAX_RETRIES})")
                        await asyncio.sleep(delay)
                    else:
                        logger.error(f"API error in handle_booking_cancellation: {e}")
                        await query.answer("❌ Временная ошибка API Google Sheets. Попробуйте снова через минуту.", show_alert=True)
                        return
                except Exception as e:
                    logger.error(f"Error in handle_booking_cancellation: {e}")
                    await query.answer("Ошибка при отмене! Попробуйте позже.", show_alert=True)
                    return
        except Exception as e:
            logger.error(f"Unexpected error in handle_booking_cancellation: {e}")
            await query.answer("❌ Временная ошибка API Google Sheets. Попробуйте снова через минуту.", show_alert=True)
        finally:
            await loading_message.delete()

async def handle_after_booking(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "book_another":
        await show_calendar(update, context)
    elif query.data == "back_to_menu":
        context.user_data['state'] = 'rent_booking_menu'
        await query.message.reply_text("Возвращаюсь в меню аренды:", reply_markup=get_rent_booking_menu())

# =================================================================================
# --- RENT PAYMENT & BALANCE ---
# =================================================================================

async def show_user_bookings_for_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    loading_message = await update.message.reply_text("⏳ Ищу ваши бронирования...")
    try:
        all_bookings = await get_user_bookings_for_payment(user_id)
        if not all_bookings:
            await update.message.reply_text("У вас нет активных неоплаченных бронирований за последние 30 дней.", reply_markup=get_rent_booking_menu())
            return
        keyboard = []
        for booking in all_bookings:
            if booking['rent_type'] == 'почасовая':
                btn_text = f"{booking['date']} {booking['time']}"
                callback_data = f"pay_hourly_{booking['worksheet']}_{booking['row']}"
            else:
                btn_text = f"{booking['date']} {booking['time']} - 2500р"
                callback_data = f"pay_full_{booking['worksheet']}_{booking['row']}_2500"
            keyboard.append([InlineKeyboardButton(btn_text, callback_data=callback_data)])
        markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text("Выберите бронирование для оплаты:", reply_markup=markup)
    except Exception as e:
        logger.error(f"Error showing user bookings for payment: {e}")
        await update.message.reply_text("❌ Временная ошибка API Google Sheets. Попробуйте снова через минуту.", reply_markup=get_rent_booking_menu())
    finally:
        await loading_message.delete()

async def handle_payment_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data.startswith("pay_full_"):
        _, _, worksheet_name, row, price = query.data.split("_")
        row = int(row)
        price = int(price)
        context.user_data['current_payment'] = {
            'worksheet': worksheet_name,
            'row': row,
            'price': price,
            'type': 'full'
        }
        payment_text = (
            f"💳 **Покупка предоплаченной аренды**\n\n"
            f"📅 **Тип аренды:** Фулл день\n"
            f"💰 **Сумма:** {price}р\n\n"
            f"📱 **Оплата по номеру телефона Т-Банк!**\n"
            f"`{PAYMENT_PHONE_NUMBER}`\n\n"
            f"⚠️ **Если не проходит оплата**, напишите сюда: {PAYMENT_CONTACT}, "
            f"будут выданы новые реквизиты.\n\n"
            f"📄 **После оплаты пришлите чек (фото или PDF) в чат и нажмите кнопку 'Оплатил'.**"
        )
        await query.edit_message_text(
            payment_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=get_payment_inline_confirmation_keyboard()
        )
        context.user_data['state'] = 'rent_waiting_for_receipt'
    elif query.data.startswith("pay_hourly_"):
        _, _, worksheet_name, row = query.data.split("_")
        row = int(row)
        context.user_data['current_payment'] = {
            'worksheet': worksheet_name,
            'row': row,
            'type': 'hourly'
        }
        keyboard = [
            [InlineKeyboardButton("2 часа - 1300р", callback_data="pay_hours_2_1300")],
            [InlineKeyboardButton("3 часа - 1950р", callback_data="pay_hours_3_1950")],
            [InlineKeyboardButton("4 часа и более - 2500р", callback_data="pay_hours_4_2500")]
        ]
        markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "💳 **Оплата почасовой аренды**\n\n"
            "Выберите количество часов для оплаты:",
            reply_markup=markup
        )

async def handle_hours_payment_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data.startswith("pay_hours_"):
        _, _, hours, price = query.data.split("_")
        hours = int(hours)
        price = int(price)
        if 'current_payment' in context.user_data:
            context.user_data['current_payment']['hours'] = hours
            context.user_data['current_payment']['price'] = price
        hours_text = f"{hours} часа" if hours == 2 or hours == 3 else "4 часа и более"
        payment_text = (
            f"💳 **Покупка предоплаченной аренды**\n\n"
            f"📅 **Тип аренды:** Почасовая\n"
            f"⏱ **Количество часов:** {hours_text}\n"
            f"💰 **Сумма:** {price}р\n\n"
            f"📱 **Оплата по номеру телефона Т-Банк!**\n"
            f"`{PAYMENT_PHONE_NUMBER}`\n\n"
            f"⚠️ **Если не проходит оплата**, напишите сюда: {PAYMENT_CONTACT}, "
            f"будут выданы новые реквизиты.\n\n"
            f"📄 **После оплаты пришлите чек (фото или PDF) в чат и нажмите кнопку 'Оплатил'.**"
        )
        await query.edit_message_text(
            payment_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=get_payment_inline_confirmation_keyboard()
        )
        context.user_data['state'] = 'rent_waiting_for_receipt'

async def handle_payment_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == "payment_done":
        if 'receipt_uploaded' not in context.user_data or not context.user_data['receipt_uploaded']:
            await query.message.reply_text(
                "❌ Сначала загрузите фото или PDF чека, затем нажмите 'Оплатил'!",
                reply_markup=get_payment_inline_confirmation_keyboard()
            )
            return
        payment_info = context.user_data.get('current_payment', {})
        if not payment_info:
            await query.answer("❌ Информация о платеже не найдена!", show_alert=True)
            return
        try:
            worksheet = await get_worksheet_cached(payment_info['worksheet'])
            if not worksheet:
                await query.answer("❌ Ошибка доступа к расписанию!", show_alert=True)
                return
            for attempt in range(MAX_RETRIES):
                try:
                    await asyncio.to_thread(worksheet.update_cell, payment_info['row'], 3, "оплачено")
                    context.user_data.pop('receipt_uploaded', None)
                    context.user_data.pop('current_payment', None)
                    caption = (
                        "✅ **Оплата подтверждена!**\n\n"
                        "Спасибо за оплату! Ваша аренда успешно оплачена.\n\n"
                        "Возвращаюсь в меню аренды:"
                    )
                    await safe_send_animation(context, query.message.chat_id, '7.gif', caption, get_rent_booking_menu())
                    context.user_data['state'] = 'rent_booking_menu'
                    break
                except APIError as e:
                    if e.response.status_code == 429:
                        delay = BASE_RETRY_DELAY * (2 ** attempt)
                        logger.warning(f"Quota exceeded in handle_payment_confirmation for {payment_info['worksheet']}. Retrying in {delay} seconds... (Attempt {attempt + 1}/{MAX_RETRIES})")
                        await asyncio.sleep(delay)
                    else:
                        logger.error(f"API error in handle_payment_confirmation: {e}")
                        await query.answer("❌ Временная ошибка API Google Sheets. Попробуйте снова через минуту.", show_alert=True)
                        return
                except Exception as e:
                    logger.error(f"Error in handle_payment_confirmation: {e}")
                    await query.answer("❌ Ошибка при подтверждении оплаты!", show_alert=True)
                    return
        except Exception as e:
            logger.error(f"Unexpected error in handle_payment_confirmation: {e}")
            await query.answer("❌ Временная ошибка API Google Sheets. Попробуйте снова через минуту.", show_alert=True)

async def handle_rent_receipt_upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_name = update.effective_user.username or "N/A"
    try:
        file = None
        file_extension = None
        if update.message.document:
            file = await update.message.document.get_file()
            file_extension = update.message.document.file_name.split('.')[-1].lower() if update.message.document.file_name else 'pdf'
            if file_extension not in ['pdf', 'jpg', 'jpeg', 'png']:
                await update.message.reply_text("❌ Пожалуйста, отправьте файл в формате PDF, JPG, JPEG или PNG.")
                return
        elif update.message.photo:
            file = await update.message.photo[-1].get_file()
            file_extension = 'jpg'
        else:
            await update.message.reply_text("❌ Пожалуйста, отправьте фото или PDF документ чека.")
            return
        file_bytes = await file.download_as_bytearray()
        caption = f"📄 Чек от пользователя @{user_name} (ID: {user_id})"
        if update.message.document:
            await context.bot.send_document(
                chat_id=ADMIN_CHAT_ID,
                document=file.file_id,
                caption=caption
            )
        else:
            await context.bot.send_photo(
                chat_id=ADMIN_CHAT_ID,
                photo=file.file_id,
                caption=caption
            )
        context.user_data['receipt_uploaded'] = True
        context.user_data['state'] = 'rent_waiting_for_receipt'
        await update.message.reply_text(
            "✅ Чек успешно загружен! Теперь вы можете нажать кнопку 'Оплатил' для подтверждения оплаты.",
            reply_markup=get_payment_inline_confirmation_keyboard()
        )
    except Exception as e:
        logger.error(f"Error processing receipt: {e}")
        await update.message.reply_text("❌ Ошибка при обработке чека. Попробуйте еще раз.")

# =================================================================================
# --- BACKGROUND TASKS & BOT LAUNCH ---
# =================================================================================

async def create_sheet_if_not_exists(sheet_name: str):
    """Auto-create a worksheet if it doesn't exist"""
    if not spreadsheet:
        logger.error("Spreadsheet client not available.")
        return None
    try:
        worksheet = await asyncio.to_thread(spreadsheet.worksheet, sheet_name)
        logger.info(f"Sheet '{sheet_name}' already exists.")
        return worksheet
    except WorksheetNotFound:
        logger.info(f"Sheet '{sheet_name}' not found. Creating it...")
        try:
            # Создаём лист с заголовками
            new_worksheet = await asyncio.to_thread(spreadsheet.add_worksheet, title=sheet_name, rows=300, cols=4)
            # Добавляем заголовки
            headers = [["Мастер", "Время", "Оплата", "Статус"]]
            await asyncio.to_thread(new_worksheet.update, 'A1:D1', headers)
            logger.info(f"Successfully created sheet '{sheet_name}'.")
            return new_worksheet
        except Exception as e:
            logger.error(f"Failed to create sheet '{sheet_name}': {e}")
            return None
    except Exception as e:
        logger.error(f"Error accessing worksheet '{sheet_name}': {e}")
        return None

async def create_monthly_sheets_job():
    logger.info("Running scheduled job: create_monthly_sheets_job")
    if not spreadsheet:
        logger.error("Spreadsheet client not available. Skipping job.")
        return
    try:
        # Используем московское время
        now_moscow = datetime.datetime.now(MOSCOW_TZ)
        today = now_moscow.date()
        
        # Создаём листы для текущего месяца и 3 следующих
        for i in range(4):
            if i == 0:
                target_date = today
            else:
                # Перемещаемся на 1 месяц вперёд
                target_date = (today.replace(day=28) + datetime.timedelta(days=4)).replace(day=1) if i == 1 else today
                for _ in range(i):
                    target_date = (target_date.replace(day=28) + datetime.timedelta(days=4)).replace(day=1)
            
            sheet_name = f"{RUSSIAN_MONTHS[target_date.month]} {target_date.year}"
            await create_sheet_if_not_exists(sheet_name)
            
        logger.info("Monthly sheets check complete.")
    except Exception as e:
        logger.error(f"Error in create_monthly_sheets_job: {e}")

async def background_scheduler():
    logger.info("Background scheduler started.")
    while True:
        now_moscow = datetime.datetime.now(MOSCOW_TZ)
        next_run = now_moscow.replace(hour=3, minute=0, second=0, microsecond=0) + datetime.timedelta(days=1)
        wait_seconds = (next_run - now_moscow).total_seconds()
        logger.info(f"Scheduler will run next job in {wait_seconds / 3600:.2f} hours (Moscow time: {now_moscow}).")
        await asyncio.sleep(wait_seconds)
        await create_monthly_sheets_job()

async def post_init(application: Application) -> None:
    """Runs after the application has been initialized."""
    application.bot_data['http_client'] = httpx.AsyncClient()
    # Create necessary sheets immediately on startup
    logger.info("Creating monthly sheets on startup...")
    await create_monthly_sheets_job()
    # Then schedule the background job
    asyncio.create_task(background_scheduler())

async def on_shutdown(application: Application) -> None:
    """Runs before the application shuts down."""
    http_client = application.bot_data.get('http_client')
    if http_client:
        await http_client.aclose()
        logger.info("HTTP client successfully closed.")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Exception while handling an update: {context.error}", exc_info=context.error)
    if update and update.effective_user:
        try:
            await context.bot.send_message(
                chat_id=update.effective_user.id,
                text="❌ Временная ошибка API Google Sheets. Попробуйте снова через минуту."
            )
        except Exception as e:
            logger.error(f"Error sending error message: {e}")

def main() -> None:
    for directory in [GIFS_DIR, ANIME_DIR, TRIBAL_DIR, OTHER_DIR, MERCH_PHOTOS_DIR]:
        if not os.path.exists(directory):
            os.makedirs(directory)
            logger.info(f"Created directory: {directory}")

    persistence = PicklePersistence(filepath=PERSISTENCE_FILE)

    application = (
        Application.builder()
        .token(TELEGRAM_BOT_TOKEN)
        .persistence(persistence)
        .post_init(post_init)
        .post_shutdown(on_shutdown)
        .build()
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, route_message))
    application.add_handler(MessageHandler(filters.PHOTO | filters.Document.ALL, route_media))
    
    # Rent callback handlers
    application.add_handler(CallbackQueryHandler(handle_calendar_callback, pattern="^(nav_|date_|back_to_menu|ignore)"))
    application.add_handler(CallbackQueryHandler(handle_time_selection, pattern="^(time_|back_to_dates)"))
    application.add_handler(CallbackQueryHandler(handle_rent_type_selection, pattern="^(rent_type_|back_to_times)"))
    application.add_handler(CallbackQueryHandler(handle_hours_selection, pattern="^(hours_|back_to_rent_type)"))
    application.add_handler(CallbackQueryHandler(handle_workplace_setup_selection, pattern="^(workplace_|back_to_rent_type)"))
    application.add_handler(CallbackQueryHandler(handle_after_booking, pattern="^(book_another|back_to_menu)"))
    application.add_handler(CallbackQueryHandler(handle_booking_cancellation, pattern="^(cancel_)"))
    application.add_handler(CallbackQueryHandler(handle_payment_selection, pattern="^(pay_full_|pay_hourly_)"))
    application.add_handler(CallbackQueryHandler(handle_hours_payment_selection, pattern="^(pay_hours_)"))
    application.add_handler(CallbackQueryHandler(handle_payment_confirmation, pattern="^(payment_done)"))
    
    application.add_error_handler(error_handler)

    logger.info("Bot is starting...")
    application.run_polling()

if __name__ == "__main__":
    main()
