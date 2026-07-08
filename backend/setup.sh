#!/bin/bash

# ============================================
# SaglikCebim Backend Setup - Linux/Mac
# ============================================
# This script automates the initial setup process
# for the SaglikCebim backend on Linux/Mac.
#
# Usage: ./setup.sh
#
# What it does:
# 1. Creates Python virtual environment
# 2. Activates venv and installs dependencies
# 3. Creates .env configuration file
# 4. Runs database migrations
# 5. Creates necessary directories
#
# Prerequisites:
# - Python 3.11+ installed and in PATH
# - PostgreSQL Docker container running (optional)
# ============================================

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
GRAY='\033[0;37m'
NC='\033[0m'  # No Color

echo -e "${CYAN}==================================${NC}"
echo -e "${CYAN}  🏥 SaglikCebim Backend Setup${NC}"
echo -e "${CYAN}==================================${NC}"
echo ""

# ============================================
# ADIM 1/6: Virtual Environment
# ============================================
echo -e "${YELLOW}📦 ADIM 1/6: Virtual Environment${NC}"
if [ ! -d "venv" ]; then
    echo -e "${GRAY}   Oluşturuluyor...${NC}"
    python3 -m venv venv
    if [ $? -eq 0 ]; then
        echo -e "   ${GREEN}✓ Oluşturuldu${NC}"
    else
        echo -e "   ${RED}✗ Hata! Python 3.11+ yüklü mü kontrol et.${NC}"
        exit 1
    fi
else
    echo -e "   ${GREEN}✓ Zaten var${NC}"
fi

# ============================================
# ADIM 2/6: Activate Virtual Environment
# ============================================
echo ""
echo -e "${YELLOW}🔌 ADIM 2/6: venv Aktifleştir${NC}"
source venv/bin/activate
echo -e "   ${GREEN}✓ Aktif${NC}"

# ============================================
# ADIM 3/6: Install Dependencies
# ============================================
echo ""
echo -e "${YELLOW}📥 ADIM 3/6: Bağımlılıklar Kuruluyor${NC}"
echo -e "${GRAY}   Bu biraz zaman alabilir...${NC}"
pip install -q -r requirements.txt
if [ $? -eq 0 ]; then
    echo -e "   ${GREEN}✓ Kuruldu (20+ packages)${NC}"
else
    echo -e "   ${RED}✗ Pip kurulumu başarısız!${NC}"
    echo -e "   ${GRAY}📌 Komutu manuel çalıştır: pip install -r requirements.txt${NC}"
    exit 1
fi

# ============================================
# ADIM 4/6: Environment Configuration
# ============================================
echo ""
echo -e "${YELLOW}⚙️  ADIM 4/6: Environment Konfigürasyonu${NC}"
if [ ! -f ".env" ]; then
    echo -e "${GRAY}   .env şablondan oluşturuluyor...${NC}"
    cp .env.example .env
    echo -e "   ${GREEN}✓ .env oluşturuldu${NC}"
    echo ""
    echo -e "   ${RED}⚠️  IMPORTANT: .env dosyasını düzenleyin!${NC}"
    echo -e "   ${GRAY}📌 Adres: $(pwd)/.env${NC}"
    echo -e "   ${GRAY}📋 Gerekli ayarlar:${NC}"
    echo -e "   ${GRAY}      - DATABASE_URL (PostgreSQL bağlantısı)${NC}"
    echo -e "   ${GRAY}      - SECRET_KEY (random string olmalı)${NC}"
    echo -e "   ${GRAY}      - VAPID keys (push notifications için)${NC}"
else
    echo -e "   ${GREEN}✓ .env zaten var${NC}"
fi

# ============================================
# ADIM 5/6: Database Migrations
# ============================================
echo ""
echo -e "${YELLOW}🗄️  ADIM 5/6: Database Migrasyonları${NC}"
echo -e "${GRAY}   Çalıştırıluyor...${NC}"
if alembic upgrade head > /dev/null 2>&1; then
    echo -e "   ${GREEN}✓ Migrasyonlar tamamlandı${NC}"
else
    echo -e "   ${RED}⚠️  Migration başarısız${NC}"
    echo -e "   ${GRAY}📌 Manual çalıştır: alembic upgrade head${NC}"
    echo -e "   ${GRAY}💡 Sorun giderim adımları:${NC}"
    echo -e "   ${GRAY}      1. PostgreSQL container running? (docker ps)${NC}"
    echo -e "   ${GRAY}      2. DATABASE_URL doğru .env'de? (kontrol et)${NC}"
    echo -e "   ${GRAY}      3. venv aktif mi?${NC}"
fi

# ============================================
# ADIM 6/6: Create Necessary Directories
# ============================================
echo ""
echo -e "${YELLOW}📁 ADIM 6/6: Dizinler Kontrol Ediliyor${NC}"
if [ ! -d "uploads" ]; then
    mkdir -p uploads
    echo -e "   ${GREEN}✓ uploads/ klasörü oluşturuldu${NC}"
else
    echo -e "   ${GREEN}✓ uploads/ klasörü var${NC}"
fi

# ============================================
# SUCCESS SUMMARY
# ============================================
echo ""
echo -e "${CYAN}==================================${NC}"
echo -e "  ${GREEN}✅ Setup Tamamlandı!${NC}"
echo -e "${CYAN}==================================${NC}"
echo ""

echo -e "${CYAN}📝 SONRAKI ADIMLAR:${NC}"
echo ""
echo -e "  ${CYAN}1️⃣  Backend'i başlat:${NC}"
echo -e "      ${YELLOW}uvicorn app.main:app --reload${NC}"
echo ""
echo -e "  ${CYAN}2️⃣  Test et:${NC}"
echo -e "      ${YELLOW}• Browser: http://localhost:8000/docs (Swagger)${NC}"
echo -e "      ${YELLOW}• curl: curl http://localhost:8000/health${NC}"
echo ""
echo -e "  ${CYAN}3️⃣  Frontend başlat (yeni terminal):${NC}"
echo -e "      ${YELLOW}cd ../frontend && npm install && npm run dev${NC}"
echo ""

echo -e "${YELLOW}💡 İPUÇLARı:${NC}"
echo -e "  ${GRAY}• Hata alırsan: CTRL+C ve setup'i yeniden çalıştır${NC}"
echo -e "  ${GRAY}• venv'i deaktif etmek için: deactivate${NC}"
echo -e "  ${GRAY}• venv'i tekrar aktif etmek için: source venv/bin/activate${NC}"
echo ""

echo -e "${CYAN}🔗 Kaynaklar:${NC}"
echo -e "  ${YELLOW}• README: ../README.md${NC}"
echo -e "  ${YELLOW}• API Docs: http://localhost:8000/redoc${NC}"
echo ""
