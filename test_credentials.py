#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify credentials.json and base64 encoding
Run this locally to debug before uploading to Railway
"""

import json
import base64
import os
from pathlib import Path

def test_credentials():
    print("=" * 80)
    print("🔍 ТЕСТ CREDENTIALS - ПРОВЕРКА НА ВАЛИДНОСТЬ")
    print("=" * 80)
    
    # Step 1: Read credentials.json
    print("\n📄 Шаг 1: Чтение credentials.json...")
    try:
        with open('credentials.json', 'r', encoding='utf-8') as f:
            creds_content = f.read()
        print(f"✅ Файл прочитан успешно ({len(creds_content)} байт)")
    except FileNotFoundError:
        print("❌ Файл credentials.json не найден!")
        return False
    except Exception as e:
        print(f"❌ Ошибка при чтении файла: {e}")
        return False
    
    # Step 2: Parse JSON
    print("\n🔍 Шаг 2: Парсинг JSON...")
    try:
        creds = json.loads(creds_content)
        print("✅ JSON валиден")
        print(f"  Проект: {creds.get('project_id')}")
        print(f"  Email: {creds.get('client_email')}")
        print(f"  Тип: {creds.get('type')}")
    except json.JSONDecodeError as e:
        print(f"❌ Ошибка парсинга JSON: {e}")
        return False
    
    # Step 3: Validate required fields
    print("\n✓ Шаг 3: Проверка обязательных полей...")
    required_fields = [
        'type', 'project_id', 'private_key_id', 'private_key',
        'client_email', 'client_id', 'auth_uri', 'token_uri'
    ]
    
    missing_fields = [f for f in required_fields if f not in creds]
    if missing_fields:
        print(f"❌ Отсутствуют поля: {missing_fields}")
        return False
    print("✅ Все обязательные поля присутствуют")
    
    # Step 4: Encode to base64
    print("\n📦 Шаг 4: Кодирование в base64...")
    try:
        base64_encoded = base64.b64encode(creds_content.encode('utf-8')).decode('utf-8')
        print(f"✅ Кодирование успешно ({len(base64_encoded)} символов)")
    except Exception as e:
        print(f"❌ Ошибка при кодировании: {e}")
        return False
    
    # Step 5: Verify base64 can be decoded back
    print("\n🔄 Шаг 5: Проверка декодирования base64...")
    try:
        decoded_back = base64.b64decode(base64_encoded).decode('utf-8')
        decoded_json = json.loads(decoded_back)
        
        if decoded_json == creds:
            print("✅ Base64 декодируется корректно")
        else:
            print("❌ Base64 декодируется, но содержимое отличается!")
            return False
    except Exception as e:
        print(f"❌ Ошибка при декодировании base64: {e}")
        return False
    
    # Step 6: Show the base64 string
    print("\n" + "=" * 80)
    print("🔑 BASE64 СТРОКА ДЛЯ RAILWAY:")
    print("=" * 80)
    print(base64_encoded)
    print("=" * 80)
    
    # Save to file for convenience
    with open('credentials_base64.txt', 'w') as f:
        f.write(base64_encoded)
    print("\n💾 Base64 также сохранён в файл: credentials_base64.txt")
    
    print("\n✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
    print("\nСледующие шаги:")
    print("1. Скопируйте base64 строку выше")
    print("2. Перейдите на railway.app → Variables")
    print("3. Создайте переменную: GOOGLE_CREDENTIALS_BASE64 = (вставьте строку)")
    print("4. Нажмите Save/Deploy")
    print("5. Проверьте логи контейнера")
    
    return True

if __name__ == "__main__":
    try:
        success = test_credentials()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ Неожиданная ошибка: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
