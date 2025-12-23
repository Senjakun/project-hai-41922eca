#!/bin/bash

# Dedicated RDP Installer - Install Windows langsung di VPS
# Usage: bash rdp_dedicated.sh [IP] [PASSWORD] [WIN_CODE]

IP=$1
PASSWORD=$2
WIN_CODE=$3
WIN_CODE=$(echo "$WIN_CODE" | tr -cd '0-9')

# Validasi parameter
if [ -z "$IP" ] || [ -z "$PASSWORD" ]; then
    echo "Error: IP dan PASSWORD harus diisi"
    exit 1
fi

echo "================================================"
echo "🖥 Memulai instalasi Dedicated RDP..."
echo "📍 Target IP: $IP"
echo "🪟 Windows Code: $WIN_CODE"
echo "================================================"

# Install sshpass jika belum ada
apt-get install -y sshpass > /dev/null 2>&1

# SSH ke VPS target dan jalankan instalasi
sshpass -p "$PASSWORD" ssh -o StrictHostKeyChecking=no -o ConnectTimeout=30 root@"$IP" "WIN_CODE='$WIN_CODE' bash -s" << 'ENDSSH'
    set -e
    
    echo "📦 Mengupdate sistem..."
    apt update -y
    apt install -y bzip2 wget curl
    
    echo "📥 Mendownload installer RDP..."
    # Menggunakan installer dari Bintang73
    wget -q https://github.com/Bintang73/auto-install-rdp/raw/refs/heads/main/main -O /tmp/rdp_setup
    chmod +x /tmp/rdp_setup
    
    echo "🔧 Menjalankan instalasi RDP..."
    cd /tmp
    if [ -n "$WIN_CODE" ]; then
        printf "%s\n" "$WIN_CODE" | timeout 1200 ./rdp_setup
    else
        timeout 1200 ./rdp_setup
    fi
    
    echo "✅ Instalasi selesai!"
ENDSSH

if [ $? -eq 0 ]; then
    echo "================================================"
    echo "✅ Dedicated RDP berhasil diinstal di $IP"
    echo "🖥 RDP Port: 3389"
    echo "🔑 Password: $PASSWORD"
    echo "================================================"
else
    echo "❌ Gagal menginstal Dedicated RDP."
    exit 1
fi
