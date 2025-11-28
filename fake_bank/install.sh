#!/bin/bash

echo "Установка Bank Service API..."

# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка Python и pip
sudo apt install -y python3 python3-pip python3-venv

# Создание виртуального окружения
python3 -m venv venv
source venv/bin/activate

# Установка зависимостей
pip install -r requirements.txt

# Создание директории для данных
mkdir -p data

echo "Установка завершена!"
echo "Для запуска выполните:"
echo "source venv/bin/activate && uvicorn main:app --host 0.0.0.0 --port 8000"