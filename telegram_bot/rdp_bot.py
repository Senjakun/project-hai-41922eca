#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RDP Installer Telegram Bot
Fitur:
- Hanya owner & user yang diizinkan yang bisa akses
- Install RDP dengan pilihan Windows
- Link Owner & Channel bisa diedit
"""

import telebot
from telebot import types
import json
import os
import subprocess
import threading

# ==================== KONFIGURASI ====================
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"  # Ganti di VPS, jangan di sini!
OWNER_ID = 123456789  # Ganti dengan Telegram ID kamu

# File untuk menyimpan data
DATA_FILE = "bot_data.json"

# ==================== LOAD/SAVE DATA ====================
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {
        "allowed_users": [OWNER_ID],
        "owner_link": "https://t.me/username_owner",
        "channel_link": "https://t.me/channel_name"
    }

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

# ==================== INISIALISASI ====================
bot = telebot.TeleBot(BOT_TOKEN)
data = load_data()

# ==================== RDP TYPE OPTIONS ====================
RDP_TYPES = {
    "docker": {
        "name": "🐳 Docker RDP",
        "desc": "• Instalasi cepat (10-15 menit)\n• Berbagai versi Windows tersedia\n• Port 3389 & 8006 (web interface)\n• Cocok untuk testing & development"
    },
    "dedicated": {
        "name": "🖥 Dedicated RDP", 
        "desc": "• Windows langsung di VPS (15-30 menit)\n• Performa optimal\n• Port 22 (custom untuk keamanan)\n• Cocok untuk production use"
    }
}

# ==================== WINDOWS OPTIONS ====================
WINDOWS_OPTIONS = {
    "1": "Windows Server 2012 R2",
    "2": "Windows Server 2016",
    "3": "Windows Server 2019",
    "4": "Windows Server 2022",
    "5": "Windows Server 2025",
    "6": "Windows 10 SuperLite",
    "7": "Windows 11 SuperLite",
    "8": "Windows 10 Atlas",
    "9": "Windows 11 Atlas",
    "10": "Windows 10 Pro",
    "11": "Windows 11 Pro",
    "12": "Tiny10 23H2",
    "13": "Tiny11 23H2"
}

# Simpan pilihan user (OS dan tipe RDP)
USER_SELECTED_OS = {}
USER_SELECTED_TYPE = {}

# ==================== MENU TEXT ====================
RDP_TYPE_MENU_TEXT = """🖥 <b>Pilih Jenis RDP Installation:</b>

🐳 <b>Docker RDP</b> - 1 kuota
• Instalasi cepat (10-15 menit)
• Berbagai versi Windows tersedia
• Port 3389 & 8006 (web interface)
• Cocok untuk testing & development

🖥 <b>Dedicated RDP</b> - 1 kuota
• Windows langsung di VPS (15-30 menit)
• Performa optimal
• Port 22 (custom untuk keamanan)
• Cocok untuk production use"""

WINDOWS_MENU_TEXT = """🖥 <b>Silahkan Pilih Versi Windows Anda</b> 🖥

1 Windows Server 2012 R2
2 Windows Server 2016
3 Windows Server 2019
4 Windows Server 2022
5 Windows Server 2025
6 Windows 10 SuperLite
7 Windows 11 SuperLite
8 Windows 10 Atlas
9 Windows 11 Atlas
10 Windows 10 Pro
11 Windows 11 Pro
12 Tiny10 23H2
13 Tiny11 23H2

Silahkan klik tombol OS di bawah 👇"""


def build_rdp_type_markup():
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🐳 Docker RDP (1 kuota)", callback_data="rdp_type_docker"))
    markup.add(types.InlineKeyboardButton("🖥 Dedicated RDP (1 kuota)", callback_data="rdp_type_dedicated"))
    markup.add(types.InlineKeyboardButton("🏠 Kembali ke Menu", callback_data="back_main"))
    return markup


def build_windows_menu_markup():
    markup = types.InlineKeyboardMarkup(row_width=3)

    row1 = [types.InlineKeyboardButton(str(i), callback_data=f"win_{i}") for i in range(1, 4)]
    row2 = [types.InlineKeyboardButton(str(i), callback_data=f"win_{i}") for i in range(4, 7)]
    row3 = [types.InlineKeyboardButton(str(i), callback_data=f"win_{i}") for i in range(7, 10)]
    row4 = [types.InlineKeyboardButton(str(i), callback_data=f"win_{i}") for i in range(10, 13)]

    markup.row(*row1)
    markup.row(*row2)
    markup.row(*row3)
    markup.row(*row4)
    markup.add(types.InlineKeyboardButton("13", callback_data="win_13"))
    markup.add(types.InlineKeyboardButton("◀️ Kembali", callback_data="install_rdp"))

    return markup

# ==================== CEK AKSES ====================
def is_allowed(user_id):
    return user_id in data["allowed_users"] or user_id == OWNER_ID

def is_owner(user_id):
    return user_id == OWNER_ID

# ==================== HANDLER /start ====================
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id

    if not is_allowed(user_id):
        bot.reply_to(message, "⛔ Akses ditolak!\nHubungi owner untuk mendapatkan akses.")
        return

    user_name = message.from_user.first_name or "User"

    text = f"""🚀 <b>RDP INSTALLER BOT</b>
━━━━━━━━━━━━━━━━━━

📊 <b>PROFILE ANDA</b>
<b>ID PROFILE</b> : <code>{user_id}</code>
<b>NAMA</b> : {user_name}

📊 <b>INFORMASI INSTALL</b>
<b>PROVIDER</b> : DigitalOcean / Vultr
<b>RAM/SPEK</b> : Minimal 2GB
<b>OS</b> : Ubuntu 22/20 - Debian 11/12
━━━━━━━━━━━━━━━━━━"""

    markup = types.InlineKeyboardMarkup(row_width=2)

    btn_install = types.InlineKeyboardButton("🖥 Install RDP", callback_data="install_rdp")
    btn_owner = types.InlineKeyboardButton("💬 Owner ↗", url=data["owner_link"])
    btn_channel = types.InlineKeyboardButton("📢 Channel ↗", url=data["channel_link"])

    markup.add(btn_install)
    markup.add(btn_owner, btn_channel)

    # Tombol khusus owner
    if is_owner(user_id):
        btn_settings = types.InlineKeyboardButton("⚙️ Settings Owner", callback_data="owner_settings")
        markup.add(btn_settings)

    bot.send_message(message.chat.id, text, parse_mode="HTML", reply_markup=markup)

# ==================== INSTALL RDP MENU ====================
@bot.callback_query_handler(func=lambda call: call.data == "install_rdp")
def install_rdp_menu(call):
    if not is_allowed(call.from_user.id):
        bot.answer_callback_query(call.id, "⛔ Akses ditolak!")
        return

    text = RDP_TYPE_MENU_TEXT
    markup = build_rdp_type_markup()

    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode="HTML", reply_markup=markup)

# ==================== PILIH TIPE RDP ====================
@bot.callback_query_handler(func=lambda call: call.data.startswith("rdp_type_"))
def select_rdp_type(call):
    if not is_allowed(call.from_user.id):
        bot.answer_callback_query(call.id, "⛔ Akses ditolak!")
        return

    rdp_type = call.data.replace("rdp_type_", "")
    USER_SELECTED_TYPE[call.from_user.id] = rdp_type
    
    type_name = RDP_TYPES[rdp_type]["name"]
    bot.answer_callback_query(call.id, f"✅ Dipilih: {type_name}")
    
    text = WINDOWS_MENU_TEXT
    markup = build_windows_menu_markup()
    
    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode="HTML", reply_markup=markup)

# ==================== PILIH WINDOWS ====================
@bot.callback_query_handler(func=lambda call: call.data.startswith("win_"))
def select_windows(call):
    if not is_allowed(call.from_user.id):
        bot.answer_callback_query(call.id, "⛔ Akses ditolak!")
        return

    win_num = call.data.replace("win_", "")
    win_name = WINDOWS_OPTIONS.get(win_num, "Unknown")
    
    # Ambil tipe RDP yang dipilih
    rdp_type = USER_SELECTED_TYPE.get(call.from_user.id, "docker")
    type_name = RDP_TYPES[rdp_type]["name"]

    # Simpan pilihan OS user untuk dipakai saat /install
    USER_SELECTED_OS[call.from_user.id] = {"code": win_num, "name": win_name}

    text = f"""✅ <b>Pilihan Anda:</b>
    
📦 <b>Tipe:</b> {type_name}
🪟 <b>Windows:</b> {win_name} (<code>{win_num}</code>)

Sekarang kirim IP dan Password VPS dengan format:
<code>/install IP PASSWORD</code>

Contoh: <code>/install 167.71.123.45 password123</code>"""

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("◀️ Kembali", callback_data="install_rdp"))

    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode="HTML", reply_markup=markup)

    bot.answer_callback_query(call.id, f"✅ Dipilih: {win_name}")

# ==================== BACK TO MAIN ====================
@bot.callback_query_handler(func=lambda call: call.data == "back_main")
def back_to_main(call):
    try:
        # Recreate start message
        user_id = call.from_user.id
        user_name = call.from_user.first_name or "User"

        text = f"""🚀 <b>RDP INSTALLER BOT</b>
━━━━━━━━━━━━━━━━━━

📊 <b>PROFILE ANDA</b>
<b>ID PROFILE</b> : <code>{user_id}</code>
<b>NAMA</b> : {user_name}

📊 <b>INFORMASI INSTALL</b>
<b>PROVIDER</b> : DigitalOcean / Vultr
<b>RAM/SPEK</b> : Minimal 2GB
<b>OS</b> : Ubuntu 22/20 - Debian 11/12
━━━━━━━━━━━━━━━━━━"""

        markup = types.InlineKeyboardMarkup(row_width=2)

        btn_install = types.InlineKeyboardButton("🖥 Install RDP", callback_data="install_rdp")
        btn_owner = types.InlineKeyboardButton("💬 Owner ↗", url=data["owner_link"])
        btn_channel = types.InlineKeyboardButton("📢 Channel ↗", url=data["channel_link"])

        markup.add(btn_install)
        markup.add(btn_owner, btn_channel)

        if is_owner(user_id):
            btn_settings = types.InlineKeyboardButton("⚙️ Settings Owner", callback_data="owner_settings")
            markup.add(btn_settings)

        bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode="HTML", reply_markup=markup)
    except Exception as e:
        print(f"Error back_to_main: {e}")
        bot.answer_callback_query(call.id, "Silakan ketik /start lagi")

# ==================== OWNER SETTINGS ====================
@bot.callback_query_handler(func=lambda call: call.data == "owner_settings")
def owner_settings(call):
    if not is_owner(call.from_user.id):
        bot.answer_callback_query(call.id, "⛔ Hanya untuk owner!")
        return

    user_count = len(data["allowed_users"])

    text = f"""⚙️ <b>OWNER SETTINGS</b>
━━━━━━━━━━━━━━━━━━

👥 <b>Total User:</b> {user_count}
🔗 <b>Owner Link:</b> {data["owner_link"]}
📢 <b>Channel Link:</b> {data["channel_link"]}

<b>Commands:</b>
/adduser [id] - Tambah user
/deluser [id] - Hapus user
/setowner [link] - Set link owner
/setchannel [link] - Set link channel
/listuser - Lihat daftar user"""

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("☁️ Google Drive Manager", callback_data="gdrive_menu"))
    markup.add(types.InlineKeyboardButton("◀️ Kembali", callback_data="back_main"))

    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode="HTML", reply_markup=markup)

# ==================== ADD USER ====================
@bot.message_handler(commands=['adduser'])
def add_user(message):
    if not is_owner(message.from_user.id):
        bot.reply_to(message, "⛔ Hanya owner yang bisa menambah user!")
        return

    try:
        user_id = int(message.text.split()[1])
        if user_id not in data["allowed_users"]:
            data["allowed_users"].append(user_id)
            save_data(data)
            bot.reply_to(message, f"✅ User <code>{user_id}</code> berhasil ditambahkan!", parse_mode="HTML")
        else:
            bot.reply_to(message, "⚠️ User sudah ada dalam daftar!")
    except (IndexError, ValueError):
        bot.reply_to(message, "❌ Format: /adduser [telegram_id]\nContoh: /adduser 123456789")

# ==================== DELETE USER ====================
@bot.message_handler(commands=['deluser'])
def del_user(message):
    if not is_owner(message.from_user.id):
        bot.reply_to(message, "⛔ Hanya owner yang bisa menghapus user!")
        return

    try:
        user_id = int(message.text.split()[1])
        if user_id == OWNER_ID:
            bot.reply_to(message, "⚠️ Tidak bisa menghapus owner!")
            return
        if user_id in data["allowed_users"]:
            data["allowed_users"].remove(user_id)
            save_data(data)
            bot.reply_to(message, f"✅ User <code>{user_id}</code> berhasil dihapus!", parse_mode="HTML")
        else:
            bot.reply_to(message, "⚠️ User tidak ditemukan!")
    except (IndexError, ValueError):
        bot.reply_to(message, "❌ Format: /deluser [telegram_id]")

# ==================== SET OWNER LINK ====================
@bot.message_handler(commands=['setowner'])
def set_owner_link(message):
    if not is_owner(message.from_user.id):
        bot.reply_to(message, "⛔ Hanya owner!")
        return

    try:
        link = message.text.split(maxsplit=1)[1]
        data["owner_link"] = link
        save_data(data)
        bot.reply_to(message, f"✅ Owner link diubah ke:\n{link}")
    except IndexError:
        bot.reply_to(message, "❌ Format: /setowner [link]\nContoh: /setowner https://t.me/username")

# ==================== SET CHANNEL LINK ====================
@bot.message_handler(commands=['setchannel'])
def set_channel_link(message):
    if not is_owner(message.from_user.id):
        bot.reply_to(message, "⛔ Hanya owner!")
        return

    try:
        link = message.text.split(maxsplit=1)[1]
        data["channel_link"] = link
        save_data(data)
        bot.reply_to(message, f"✅ Channel link diubah ke:\n{link}")
    except IndexError:
        bot.reply_to(message, "❌ Format: /setchannel [link]")

# ==================== LIST USER ====================
@bot.message_handler(commands=['listuser'])
def list_users(message):
    if not is_owner(message.from_user.id):
        bot.reply_to(message, "⛔ Hanya owner!")
        return

    user_list = "\n".join([f"• <code>{uid}</code>" for uid in data["allowed_users"]])
    text = f"👥 <b>Daftar User ({len(data['allowed_users'])}):</b>\n\n{user_list}"
    bot.reply_to(message, text, parse_mode="HTML")

# ==================== INSTALL COMMAND /install ====================
@bot.message_handler(commands=['install'])
def install_command(message):
    if not is_allowed(message.from_user.id):
        bot.reply_to(message, "⛔ Akses ditolak!")
        return

    try:
        parts = message.text.split()
        if len(parts) < 3:
            raise ValueError

        ip = parts[1]
        password = parts[2]

        # WIN_CODE bisa diambil dari argumen ke-3 atau dari pilihan terakhir user
        win_code = parts[3] if len(parts) >= 4 else None
        if not win_code:
            saved = USER_SELECTED_OS.get(message.from_user.id)
            win_code = saved.get("code") if saved else None

        if not win_code or win_code not in WINDOWS_OPTIONS:
            bot.reply_to(
                message,
                "❗ Kamu belum memilih OS. Pilih OS dulu di bawah ini, lalu ulangi: <code>/install IP PASSWORD</code>",
                parse_mode="HTML",
            )
            bot.send_message(
                message.chat.id,
                RDP_TYPE_MENU_TEXT,
                parse_mode="HTML",
                reply_markup=build_rdp_type_markup(),
            )
            return

        # Ambil tipe RDP yang dipilih
        rdp_type = USER_SELECTED_TYPE.get(message.from_user.id, "docker")
        type_name = RDP_TYPES[rdp_type]["name"]
        win_name = WINDOWS_OPTIONS[win_code]
        
        # Kirim pesan awal
        bot.reply_to(
            message, 
            f"""🔌 <b>Menghubungkan ke VPS...</b>

📦 <b>Tipe:</b> {type_name}
📍 <b>IP:</b> <code>{ip}</code>
🪟 <b>Windows:</b> {win_name} ({win_code})""", 
            parse_mode="HTML"
        )

        # Jalankan script instalasi berdasarkan tipe
        script_dir = os.path.dirname(os.path.abspath(__file__))
        
        if rdp_type == "docker":
            script_path = os.path.join(script_dir, "rdp_docker.sh")
        else:
            script_path = os.path.join(script_dir, "rdp_dedicated.sh")

        if not os.path.exists(script_path):
            bot.reply_to(message, f"❌ File {os.path.basename(script_path)} tidak ditemukan. Pastikan sudah git pull.")
            return

        subprocess.run(["chmod", "+x", script_path], check=False)
        
        chat_id = str(message.chat.id)
        
        # Fungsi untuk jalankan instalasi di background
        def run_install():
            try:
                log_path = os.path.join(script_dir, "rdp_install.log")
                
                result = subprocess.run(
                    ["bash", script_path, ip, password, win_code, chat_id, BOT_TOKEN],
                    capture_output=True,
                    text=True,
                    timeout=2400  # 40 menit timeout
                )
                
                output = result.stdout + result.stderr
                exit_code = result.returncode
                
                # Simpan log
                with open(log_path, "a") as log:
                    log.write(f"\n{'='*50}\n")
                    log.write(f"User: {message.from_user.id} | IP: {ip} | OS: {win_code} | Type: {rdp_type}\n")
                    log.write(output)
                    log.write(f"\nExit code: {exit_code}\n")
                    
            except subprocess.TimeoutExpired:
                bot.send_message(
                    message.chat.id, 
                    f"""⏰ <b>TIMEOUT!</b>
━━━━━━━━━━━━━━━━━━

📍 <b>IP:</b> <code>{ip}</code>
🪟 <b>Windows:</b> {win_name}

Proses melebihi batas waktu.
Kemungkinan instalasi masih berjalan di VPS.

Coba cek VPS secara manual.""",
                    parse_mode="HTML"
                )
            except Exception as e:
                bot.send_message(
                    message.chat.id,
                    f"""⚠️ <b>ERROR!</b>
━━━━━━━━━━━━━━━━━━

Terjadi error: <code>{str(e)}</code>

Silakan coba lagi.""",
                    parse_mode="HTML"
                )
        
        # Jalankan di background thread
        install_thread = threading.Thread(target=run_install, daemon=True)
        install_thread.start()
        
        # Kirim konfirmasi
        bot.send_message(
            message.chat.id,
            f"""🚀 <b>Proses Instalasi Dimulai!</b>
━━━━━━━━━━━━━━━━━━

📦 <b>Tipe:</b> {type_name}
📍 <b>IP:</b> <code>{ip}</code>
🪟 <b>Windows:</b> {win_name}

⏳ Instalasi berjalan di background.
Kamu akan menerima notifikasi saat selesai.

<b>Estimasi waktu:</b>
• Docker RDP: 10-15 menit
• Dedicated RDP: 15-30 menit

💡 Kamu bisa menutup chat ini, notifikasi akan dikirim otomatis.""",
            parse_mode="HTML"
        )

    except Exception:
        bot.reply_to(message, "❌ Format: /install [IP] [PASSWORD]\nContoh: /install 167.71.123.45 password123")

# ==================== GOOGLE DRIVE MENU ====================
@bot.callback_query_handler(func=lambda call: call.data == "gdrive_menu")
def gdrive_menu(call):
    if not is_owner(call.from_user.id):
        bot.answer_callback_query(call.id, "⛔ Hanya untuk owner!")
        return

    # Cek apakah rclone sudah terinstall
    rclone_status = "✅ Terinstall" if os.path.exists("/usr/bin/rclone") else "❌ Belum terinstall"
    
    # Cek apakah gdrive sudah dikonfigurasi
    gdrive_configured = os.path.exists(os.path.expanduser("~/.config/rclone/rclone.conf"))
    gdrive_status = "✅ Terkonfigurasi" if gdrive_configured else "❌ Belum dikonfigurasi"

    text = f"""☁️ <b>GOOGLE DRIVE MANAGER</b>
━━━━━━━━━━━━━━━━━━

📦 <b>Rclone:</b> {rclone_status}
🔗 <b>GDrive:</b> {gdrive_status}

<b>Pilih aksi:</b>"""

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔧 Setup Rclone + GDrive", callback_data="gdrive_setup"))
    markup.add(types.InlineKeyboardButton("📤 Upload Image", callback_data="gdrive_upload"))
    markup.add(types.InlineKeyboardButton("📥 Download Image", callback_data="gdrive_download"))
    markup.add(types.InlineKeyboardButton("📋 List Images", callback_data="gdrive_list"))
    markup.add(types.InlineKeyboardButton("🗑 Delete Image", callback_data="gdrive_delete"))
    markup.add(types.InlineKeyboardButton("◀️ Kembali", callback_data="owner_settings"))

    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode="HTML", reply_markup=markup)

# ==================== GDRIVE SETUP ====================
@bot.callback_query_handler(func=lambda call: call.data == "gdrive_setup")
def gdrive_setup(call):
    if not is_owner(call.from_user.id):
        bot.answer_callback_query(call.id, "⛔ Hanya untuk owner!")
        return

    text = """🔧 <b>SETUP RCLONE + GOOGLE DRIVE</b>
━━━━━━━━━━━━━━━━━━

<b>Step 1:</b> Install rclone (otomatis)
<b>Step 2:</b> Konfigurasi Google Drive

Gunakan command:
<code>/setuprclone</code> - Install rclone otomatis
<code>/configgdrive [client_id] [client_secret]</code> - Config GDrive

<b>Cara dapat Client ID & Secret:</b>
1. Buka https://console.cloud.google.com
2. Buat project baru
3. Enable Google Drive API
4. Buat OAuth credentials
5. Salin Client ID & Secret"""

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("🔧 Auto Install Rclone", callback_data="gdrive_install_rclone"))
    markup.add(types.InlineKeyboardButton("◀️ Kembali", callback_data="gdrive_menu"))

    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode="HTML", reply_markup=markup)

# ==================== AUTO INSTALL RCLONE ====================
@bot.callback_query_handler(func=lambda call: call.data == "gdrive_install_rclone")
def gdrive_install_rclone(call):
    if not is_owner(call.from_user.id):
        bot.answer_callback_query(call.id, "⛔ Hanya untuk owner!")
        return

    bot.answer_callback_query(call.id, "⏳ Menginstall rclone...")
    
    def install_rclone():
        try:
            # Install rclone
            result = subprocess.run(
                ["bash", "-c", "curl https://rclone.org/install.sh | sudo bash"],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if os.path.exists("/usr/bin/rclone"):
                bot.send_message(
                    call.message.chat.id,
                    """✅ <b>Rclone berhasil diinstall!</b>

Sekarang konfigurasi Google Drive:
<code>/configgdrive [client_id] [client_secret]</code>

Atau bisa juga manual:
<code>rclone config</code>""",
                    parse_mode="HTML"
                )
            else:
                bot.send_message(
                    call.message.chat.id,
                    f"❌ Gagal install rclone:\n<code>{result.stderr[:500]}</code>",
                    parse_mode="HTML"
                )
        except Exception as e:
            bot.send_message(call.message.chat.id, f"❌ Error: {str(e)}")
    
    threading.Thread(target=install_rclone, daemon=True).start()

# ==================== CONFIG GDRIVE ====================
@bot.message_handler(commands=['configgdrive'])
def config_gdrive(message):
    if not is_owner(message.from_user.id):
        bot.reply_to(message, "⛔ Hanya owner!")
        return

    try:
        parts = message.text.split()
        if len(parts) < 3:
            bot.reply_to(message, """❌ Format: /configgdrive [client_id] [client_secret]

Contoh:
<code>/configgdrive 123456789.apps.googleusercontent.com GOCSPX-xxxxx</code>""", parse_mode="HTML")
            return

        client_id = parts[1]
        client_secret = parts[2]
        
        # Buat config rclone
        config_dir = os.path.expanduser("~/.config/rclone")
        os.makedirs(config_dir, exist_ok=True)
        
        config_content = f"""[gdrive]
type = drive
client_id = {client_id}
client_secret = {client_secret}
scope = drive
"""
        
        with open(os.path.join(config_dir, "rclone.conf"), "w") as f:
            f.write(config_content)
        
        bot.reply_to(message, """✅ <b>Konfigurasi GDrive disimpan!</b>

Sekarang authorize dengan command di VPS:
<code>rclone config reconnect gdrive:</code>

Ikuti instruksi untuk login ke Google Account.""", parse_mode="HTML")
        
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

# ==================== GDRIVE UPLOAD ====================
@bot.callback_query_handler(func=lambda call: call.data == "gdrive_upload")
def gdrive_upload_menu(call):
    if not is_owner(call.from_user.id):
        bot.answer_callback_query(call.id, "⛔ Hanya untuk owner!")
        return

    text = """📤 <b>UPLOAD KE GOOGLE DRIVE</b>
━━━━━━━━━━━━━━━━━━

Gunakan command:
<code>/upload [path_file] [folder_gdrive]</code>

Contoh:
<code>/upload /tmp/win10.img.gz rdp-images</code>
<code>/upload /home/user/image.img.gz</code>

File akan diupload ke folder 'rdp-images' di GDrive.
Jika folder tidak ada, akan dibuat otomatis."""

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("◀️ Kembali", callback_data="gdrive_menu"))

    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode="HTML", reply_markup=markup)

@bot.message_handler(commands=['upload'])
def upload_to_gdrive(message):
    if not is_owner(message.from_user.id):
        bot.reply_to(message, "⛔ Hanya owner!")
        return

    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "❌ Format: /upload [path_file] [folder_gdrive]")
            return

        file_path = parts[1]
        folder = parts[2] if len(parts) >= 3 else "rdp-images"
        
        if not os.path.exists(file_path):
            bot.reply_to(message, f"❌ File tidak ditemukan: {file_path}")
            return
        
        file_size = os.path.getsize(file_path) / (1024 * 1024 * 1024)  # GB
        bot.reply_to(message, f"⏳ Mengupload {os.path.basename(file_path)} ({file_size:.2f} GB)...")
        
        def do_upload():
            try:
                result = subprocess.run(
                    ["rclone", "copy", file_path, f"gdrive:{folder}/", "-P"],
                    capture_output=True,
                    text=True,
                    timeout=7200  # 2 jam timeout
                )
                
                if result.returncode == 0:
                    bot.send_message(
                        message.chat.id,
                        f"""✅ <b>Upload Berhasil!</b>

📁 <b>File:</b> {os.path.basename(file_path)}
📂 <b>Folder:</b> gdrive:{folder}/
📊 <b>Size:</b> {file_size:.2f} GB""",
                        parse_mode="HTML"
                    )
                else:
                    bot.send_message(message.chat.id, f"❌ Upload gagal:\n<code>{result.stderr[:500]}</code>", parse_mode="HTML")
            except subprocess.TimeoutExpired:
                bot.send_message(message.chat.id, "⏰ Upload timeout (>2 jam)")
            except Exception as e:
                bot.send_message(message.chat.id, f"❌ Error: {str(e)}")
        
        threading.Thread(target=do_upload, daemon=True).start()
        
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

# ==================== GDRIVE DOWNLOAD ====================
@bot.callback_query_handler(func=lambda call: call.data == "gdrive_download")
def gdrive_download_menu(call):
    if not is_owner(call.from_user.id):
        bot.answer_callback_query(call.id, "⛔ Hanya untuk owner!")
        return

    text = """📥 <b>DOWNLOAD DARI GOOGLE DRIVE</b>
━━━━━━━━━━━━━━━━━━

Gunakan command:
<code>/download [gdrive_path] [local_path]</code>

Contoh:
<code>/download rdp-images/win10.img.gz /tmp/</code>
<code>/download rdp-images/win11.img.gz /home/user/</code>

File akan didownload dari GDrive ke VPS."""

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("◀️ Kembali", callback_data="gdrive_menu"))

    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode="HTML", reply_markup=markup)

@bot.message_handler(commands=['download'])
def download_from_gdrive(message):
    if not is_owner(message.from_user.id):
        bot.reply_to(message, "⛔ Hanya owner!")
        return

    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "❌ Format: /download [gdrive_path] [local_path]")
            return

        gdrive_path = parts[1]
        local_path = parts[2] if len(parts) >= 3 else "/tmp/"
        
        bot.reply_to(message, f"⏳ Mengdownload {gdrive_path}...")
        
        def do_download():
            try:
                result = subprocess.run(
                    ["rclone", "copy", f"gdrive:{gdrive_path}", local_path, "-P"],
                    capture_output=True,
                    text=True,
                    timeout=7200
                )
                
                if result.returncode == 0:
                    bot.send_message(
                        message.chat.id,
                        f"""✅ <b>Download Berhasil!</b>

📁 <b>File:</b> {gdrive_path}
📂 <b>Lokasi:</b> {local_path}""",
                        parse_mode="HTML"
                    )
                else:
                    bot.send_message(message.chat.id, f"❌ Download gagal:\n<code>{result.stderr[:500]}</code>", parse_mode="HTML")
            except subprocess.TimeoutExpired:
                bot.send_message(message.chat.id, "⏰ Download timeout (>2 jam)")
            except Exception as e:
                bot.send_message(message.chat.id, f"❌ Error: {str(e)}")
        
        threading.Thread(target=do_download, daemon=True).start()
        
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

# ==================== GDRIVE LIST ====================
@bot.callback_query_handler(func=lambda call: call.data == "gdrive_list")
def gdrive_list_menu(call):
    if not is_owner(call.from_user.id):
        bot.answer_callback_query(call.id, "⛔ Hanya untuk owner!")
        return

    bot.answer_callback_query(call.id, "⏳ Mengambil daftar file...")
    
    def list_files():
        try:
            result = subprocess.run(
                ["rclone", "lsl", "gdrive:rdp-images/"],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0 and result.stdout.strip():
                files = result.stdout.strip().split("\n")
                file_list = []
                for f in files[:20]:  # Max 20 files
                    parts = f.split()
                    if len(parts) >= 4:
                        size = int(parts[0]) / (1024 * 1024 * 1024)  # GB
                        name = parts[-1]
                        file_list.append(f"• {name} ({size:.2f} GB)")
                
                text = f"""📋 <b>DAFTAR IMAGE DI GDRIVE</b>
━━━━━━━━━━━━━━━━━━

{chr(10).join(file_list) if file_list else "Tidak ada file"}

Total: {len(files)} file"""
            else:
                text = """📋 <b>DAFTAR IMAGE DI GDRIVE</b>
━━━━━━━━━━━━━━━━━━

Folder kosong atau belum dikonfigurasi.

Pastikan sudah setup GDrive dengan benar."""
            
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("🔄 Refresh", callback_data="gdrive_list"))
            markup.add(types.InlineKeyboardButton("◀️ Kembali", callback_data="gdrive_menu"))
            
            bot.send_message(call.message.chat.id, text, parse_mode="HTML", reply_markup=markup)
            
        except Exception as e:
            bot.send_message(call.message.chat.id, f"❌ Error: {str(e)}")
    
    threading.Thread(target=list_files, daemon=True).start()

# ==================== GDRIVE DELETE ====================
@bot.callback_query_handler(func=lambda call: call.data == "gdrive_delete")
def gdrive_delete_menu(call):
    if not is_owner(call.from_user.id):
        bot.answer_callback_query(call.id, "⛔ Hanya untuk owner!")
        return

    text = """🗑 <b>DELETE FILE DI GOOGLE DRIVE</b>
━━━━━━━━━━━━━━━━━━

Gunakan command:
<code>/deletegdrive [nama_file]</code>

Contoh:
<code>/deletegdrive rdp-images/win10.img.gz</code>
<code>/deletegdrive rdp-images/win11-old.img.gz</code>

⚠️ <b>HATI-HATI!</b> File yang dihapus tidak bisa dikembalikan."""

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("◀️ Kembali", callback_data="gdrive_menu"))

    bot.edit_message_text(text, call.message.chat.id, call.message.message_id, parse_mode="HTML", reply_markup=markup)

@bot.message_handler(commands=['deletegdrive'])
def delete_from_gdrive(message):
    if not is_owner(message.from_user.id):
        bot.reply_to(message, "⛔ Hanya owner!")
        return

    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "❌ Format: /deletegdrive [path_file]")
            return

        file_path = parts[1]
        
        bot.reply_to(message, f"⏳ Menghapus {file_path}...")
        
        def do_delete():
            try:
                result = subprocess.run(
                    ["rclone", "delete", f"gdrive:{file_path}"],
                    capture_output=True,
                    text=True,
                    timeout=60
                )
                
                if result.returncode == 0:
                    bot.send_message(
                        message.chat.id,
                        f"✅ <b>File berhasil dihapus:</b>\n{file_path}",
                        parse_mode="HTML"
                    )
                else:
                    bot.send_message(message.chat.id, f"❌ Gagal menghapus:\n<code>{result.stderr[:500]}</code>", parse_mode="HTML")
            except Exception as e:
                bot.send_message(message.chat.id, f"❌ Error: {str(e)}")
        
        threading.Thread(target=do_delete, daemon=True).start()
        
    except Exception as e:
        bot.reply_to(message, f"❌ Error: {str(e)}")

# ==================== SETUP RCLONE COMMAND ====================
@bot.message_handler(commands=['setuprclone'])
def setup_rclone_cmd(message):
    if not is_owner(message.from_user.id):
        bot.reply_to(message, "⛔ Hanya owner!")
        return

    bot.reply_to(message, "⏳ Menginstall rclone...")
    
    def install():
        try:
            result = subprocess.run(
                ["bash", "-c", "curl https://rclone.org/install.sh | sudo bash"],
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if os.path.exists("/usr/bin/rclone"):
                bot.send_message(
                    message.chat.id,
                    """✅ <b>Rclone berhasil diinstall!</b>

Sekarang konfigurasi Google Drive:
<code>/configgdrive [client_id] [client_secret]</code>""",
                    parse_mode="HTML"
                )
            else:
                bot.send_message(message.chat.id, f"❌ Gagal install:\n<code>{result.stderr[:500]}</code>", parse_mode="HTML")
        except Exception as e:
            bot.send_message(message.chat.id, f"❌ Error: {str(e)}")
    
    threading.Thread(target=install, daemon=True).start()

# ==================== RUN BOT ====================
if __name__ == "__main__":
    print("🤖 Bot sedang berjalan...")
    bot.infinity_polling()
