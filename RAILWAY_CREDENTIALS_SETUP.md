# 🚀 Установка на Railway - Инструкция по credentials

## Проблема
```
google.auth.exceptions.RefreshError: ('invalid_grant: Invalid JWT Signature.')
```

**Причина**: Railway не может использовать файлы с учётными данными. Нужно передать credentials через переменные окружения.

---

## ✅ Решение

### Шаг 1️⃣: Преобразуйте credentials.json в base64

#### На Windows (PowerShell):
```powershell
$content = Get-Content "credentials.json" -Raw
$bytes = [System.Text.Encoding]::UTF8.GetBytes($content)
$base64 = [Convert]::ToBase64String($bytes)
Write-Host $base64
```

Скопируйте весь вывод (это будет длинная строка).

#### На Mac/Linux:
```bash
cat credentials.json | base64 | tr -d '\n'
```

---

### Шаг 2️⃣: Добавьте переменную на Railway

1. Откройте [Railway панель](https://railway.app/)
2. Найдите ваш проект
3. Перейдите в **Variables** (слева внизу)
4. Нажмите **+ New Variable**
5. Создайте переменную:
   - **Имя**: `GOOGLE_CREDENTIALS_BASE64`
   - **Значение**: (вставьте base64 строку из Шага 1)
6. Нажмите **Save**

---

### Шаг 3️⃣: Перезагрузите контейнер

1. В Railway панели нажмите кнопку **Redeploy**
2. Дождитесь загрузки контейнера

---

## 🎯 Как это работает

Код автоматически проверит в таком порядке:
1. **Переменная `GOOGLE_CREDENTIALS_BASE64`** (для Railway) ← используем это
2. **Переменная `GOOGLE_CREDENTIALS`** (JSON строка, если понадобится)
3. **Файл `credentials.json`** (для локальной разработки)

---

## ✨ Готово!

После перезагрузки ошибка должна исчезнуть и бот нормально подключится к Google Sheets.

---

## 🆘 Если всё ещё не работает

Проверьте:
1. Base64 строка скопирована **полностью** (без пробелов в начале/конце)?
2. Переменная сохранена в Railway?
3. Контейнер перезагружен после добавления переменной?
4. Проверьте логи Railway на наличие других ошибок

Если ошибка "Invalid JWT Signature" всё ещё появляется - значит credentials.json повреждены и нужно загенерировать новые в Google Cloud Console.
