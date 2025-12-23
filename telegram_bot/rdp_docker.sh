#!/bin/bash

# Docker RDP Installer - Menggunakan Docker untuk jalankan Windows
# Usage: bash rdp_docker.sh [IP] [PASSWORD] [WIN_CODE]

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
echo "🐳 Memulai instalasi Docker RDP..."
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
    apt install -y curl wget bzip2
    
    echo "🐳 Menginstall Docker..."
    if ! command -v docker &> /dev/null; then
        curl -fsSL https://get.docker.com | sh
        systemctl enable docker
        systemctl start docker
    fi
    
    echo "📥 Mendownload Windows Docker image..."
    # Menggunakan dockur/windows untuk Docker Windows
    docker pull dockurr/windows
    
    echo "🔧 Menjalankan Windows container..."
    docker run -d \
        --name windows \
        --device=/dev/kvm \
        --cap-add NET_ADMIN \
        -p 8006:8006 \
        -p 3389:3389/tcp \
        -p 3389:3389/udp \
        -e RAM_SIZE="2G" \
        -e CPU_CORES="2" \
        -e VERSION="${WIN_CODE:-win10}" \
        -v /windows:/storage \
        --restart unless-stopped \
        dockurr/windows
    
    echo "✅ Docker Windows berhasil dijalankan!"
    echo "🌐 Web Interface: http://$(hostname -I | awk '{print $1}'):8006"
    echo "🖥 RDP Port: 3389"
ENDSSH

if [ $? -eq 0 ]; then
    echo "================================================"
    echo "✅ Docker RDP berhasil diinstal di $IP"
    echo "🌐 Web: http://$IP:8006"
    echo "🖥 RDP Port: 3389"
    echo "================================================"
else
    echo "❌ Gagal menginstal Docker RDP."
    exit 1
fi
