# XTRA — xtra.agency.ua

Лендинг веб-студії XTRA. Тёмная тема, жёлтые акценты, интерактивный квиз из 4 шагов.

## Локальный запуск

```bash
python3 -m http.server 8080
```

Открыть: http://localhost:8080

## Live

https://bogdan22807.github.io/xcxc/

## Заявки в Telegram

Заявки из квиза отправляются в Telegram-бота через serverless-функцию
`api/lead.js` (работает на Vercel — не на GitHub Pages).

### Настройка

1. **Создай бота.** Напиши [@BotFather](https://t.me/BotFather) → `/newbot` →
   получи `TELEGRAM_BOT_TOKEN` (вида `123456:ABC...`).
2. **Узнай свой chat id.** Напиши своему боту любое сообщение, затем открой
   `https://api.telegram.org/bot<ТОКЕН>/getUpdates` и найди `"chat":{"id":...}`.
   (Или напиши [@userinfobot](https://t.me/userinfobot).) Это `TELEGRAM_CHAT_ID`.
3. **Разверни на Vercel.** Импортируй репозиторий на [vercel.com](https://vercel.com),
   в **Settings → Environment Variables** добавь:
   - `TELEGRAM_BOT_TOKEN` — токен из BotFather
   - `TELEGRAM_CHAT_ID` — твой chat id
4. **Задеплой.** После деплоя заявки с формы будут приходить боту в Telegram.

> Важно: на GitHub Pages форма работать не будет (там нет сервера) — заявки
> в Telegram приходят только на Vercel-версии сайта.
