# ✅ Чек-лист для Railway - Решение ошибки InvalidJWTSignature

## 🔍 Что может быть не так?

Ошибка `Invalid JWT Signature` обычно означает одно из:

1. **Переменная окружения не добавлена**
2. **Base64 строка повреждена или неполная**
3. **Credentials.json невалидны или истекли**
4. **Контейнер не перезагружен после добавления переменной**

---

## ✅ Пошаговая проверка

### Шаг 1: Проверьте на Railway
- [ ] Откройте ваш проект на railway.app
- [ ] Перейдите в **Variables**
- [ ] Проверьте есть ли переменная `GOOGLE_CREDENTIALS_BASE64`
- [ ] Если не видите - значит она не была добавлена!

### Шаг 2: Проверьте логи контейнера

После перезагрузки посмотрите в **Logs**. Вы должны увидеть:

✅ **ХОРОШО:** 
```
Found GOOGLE_CREDENTIALS_BASE64 env var (length: 3172)
Decoded credentials for project: massive-glyph-465201-a5
Client email: ikona-81@massive-glyph-465201-a5.iam.gserviceaccount.com
✅ Successfully connected to Google Sheets using env credentials (base64).
✅ Spreadsheet opened successfully.
```

❌ **ПЛОХО:**
```
⚠️ GOOGLE_CREDENTIALS_BASE64 environment variable not found!
Attempting to use credentials from file: credentials.json
❌ Credentials file not found: credentials.json
```

---

### Шаг 3: Если переменная не видна на Railroad

**Возможные причины:**
1. Вы добавили переменную, но контейнер ещё не перефdeployed
2. Вы добавили в неправильный сервис (есть несколько?)
3. Переменная была добавлена, но потом случайно удалена

**Решение:**
1. Откройте **Variables** в Railway
2. Удалите старую переменную если есть
3. Создайте НОВУЮ с именем: `GOOGLE_CREDENTIALS_BASE64`
4. Вставьте ВЕСЬ base64 текст (3172 символа)
5. Нажмите **Save**
6. Дождитесь что контейнер перезагружен (должен быть прогресс бар)

---

### Шаг 4: Если переменная есть, но всё ещё ошибка JWT

**Проверьте base64 строку:**

Скопируйте и запустите локально:
```powershell
# Проверка что base64 можно декодировать
$base64 = "ewogICJ0eXBlIjog..." # вставьте вашу строку
$bytes = [Convert]::FromBase64String($base64)
$json = [System.Text.Encoding]::UTF8.GetString($bytes)
Write-Host $json | ConvertFrom-Json
```

Если это не работает - base64 повреждена!

---

### Шаг 5: Если credentials.json невалидны

**Признаки:**
- Base64 декодируется OK
- JSON парсится OK
- Но ошибка JWT остаётся...

**Решение:**
1. Зайдите в [Google Cloud Console](https://console.cloud.google.com/)
2. Перейдите в **APIs & Services** → **Credentials**
3. Найдите service account `ikona-81@...`
4. Нажмите на неё
5. Перейдите в **Keys**
6. Удалите старый ключ
7. Создайте НОВЫЙ JSON ключ
8. Скопируйте его содержимое
9. Заново конвертируйте в base64
10. Обновите переменную на Railway

---

## 🆘 Если ничего не помогает

Попробуйте вариант для разработки - добавьте на Railway переменную:

```
GOOGLE_CREDENTIALS_DEBUG=true
```

Это выведет лишню информацию в логи, которая поможет найти проблему.

---

## 📋 Что должно быть после успешного подключения

Если всё работает, в логах будет:
1. ✅ Base64 var found
2. ✅ Credentials decoded
3. ✅ Google Sheets connected
4. ✅ Spreadsheet opened
5. ✅ Bot started

После этого ошибка исчезнет и бот начнёт работать нормально.
