#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Correct way to convert credentials.json to base64 for Railway
Handles line breaks in private key correctly
"""

import json
import base64
import sys

def convert_credentials_to_base64():
    """Convert credentials.json to properly formatted base64"""
    
    print("=" * 80)
    print("КОНВЕРТАЦИЯ CREDENTIALS.JSON В BASE64 (ПРАВИЛЬНЫЙ СПОСОБ)")
    print("=" * 80)
    
    try:
        # Read the file character by character to preserve line breaks
        with open('credentials.json', 'rb') as f:
            content_bytes = f.read()
        
        print(f"\nОригинальный размер файла: {len(content_bytes)} байт")
        
        # Verify it's valid JSON first
        content_str = content_bytes.decode('utf-8')
        creds = json.loads(content_str)
        
        print(f"✓ JSON валиден")
        print(f"  Проект: {creds.get('project_id')}")
        print(f"  Email: {creds.get('client_email')}")
        
        # Check private key
        private_key = creds.get('private_key', '')
        print(f"  Private key:") 
        print(f"    - Начинается с: {private_key[:30]}")
        print(f"    - Длина: {len(private_key)}")
        print(f"    - Переносы строк: {private_key.count(chr(92)+'n')} (\\n)")
        
        # Convert to base64
        base64_encoded = base64.b64encode(content_bytes).decode('ascii')
        
        print(f"\n✓ Base64 кодирование успешно")
        print(f"  Размер base64: {len(base64_encoded)} символов")
        
        # Verify decode works
        decoded_bytes = base64.b64decode(base64_encoded)
        decoded_str = decoded_bytes.decode('utf-8')
        decoded_creds = json.loads(decoded_str)
        
        if decoded_creds == creds:
            print(f"✓ Проверка декодирования: OK")
        else:
            print(f"❌ Проверка декодирования: ОШИБКА - содержимое отличается!")
            return False
        
        # Check private key after decode
        decoded_pk = decoded_creds.get('private_key', '')
        if decoded_pk == private_key:
            print(f"✓ Приватный ключ сохранён идентично")
        else:
            print(f"❌ Приватный ключ повреждён при кодировании!")
            print(f"  Оригинал: {len(private_key)} символов")
            print(f"  После: {len(decoded_pk)} символов")
            return False
        
        # Output the base64
        print("\n" + "=" * 80)
        print("СКОПИРУЙТЕ ВЕСЬ ТЕКСТ НИЖЕ В RAILWAY:")
        print("=" * 80)
        print(base64_encoded)
        print("=" * 80)
        
        # Save to file
        with open('credentials_base64_proper.txt', 'w') as f:
            f.write(base64_encoded)
        print(f"\n✓ Base64 также сохранён в: credentials_base64_proper.txt ({len(base64_encoded)} символов)")
        
        print("\n✅ КОНВЕРТАЦИЯ УСПЕШНА!")
        print("\nИнструкции для Railway:")
        print("1. Откройте railway.app → Variables")
        print("2. Удалите старую переменную GOOGLE_CREDENTIALS_BASE64 если есть")
        print("3. Создайте НОВУЮ переменную:")
        print("   Имя: GOOGLE_CREDENTIALS_BASE64")
        print("   Значение: (вставьте всю строку выше)")
        print("4. Нажмите Save")
        print("5. Дождитесь перезагрузки контейнера")
        
        return True
        
    except FileNotFoundError:
        print("❌ Файл credentials.json не найден!")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ Ошибка парсинга JSON: {e}")
        return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = convert_credentials_to_base64()
    sys.exit(0 if success else 1)
