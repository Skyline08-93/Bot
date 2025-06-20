# sol-bot-railway 🤖📈

Автоматический спотовый торговый бот для пары SOL/USDT на бирже Bybit с анализом по MACD и OBV. Подключен к Telegram для уведомлений о сделках и прибыли.

---

## ⚙️ Как запустить на Railway

### 1. Подготовка
- Убедитесь, что у вас есть аккаунт на [Railway](https://railway.app)
- Подключите этот репозиторий к Railway (Deploy from GitHub)

### 2. Установите переменные окружения на Railway

Перейдите в **Deployments → Variables** и добавьте переменные из `.env.example`:

| Название переменной     | Пример значения                  |
|-------------------------|----------------------------------|
| `BYBIT_API_KEY`         | `GenOyt0Rf02LombN6e`             |
| `BYBIT_API_SECRET`      | `vxOegi3zL11hcvWOy2DFUNx...`     |
| `TELEGRAM_TOKEN`        | `7567914583:AA...`              |
| `TELEGRAM_CHAT_ID`      | `937242089`                      |
| `CAPITAL`               | `20`                             |
| `SYMBOL`                | `SOL/USDT`                       |
| `TIMEFRAME`             | `15m`                            |
| `STOP_LOSS_PERCENT`     | `-1`                             |
| `TRAIL_START_PROFIT`    | `2`                              |
| `TRAIL_GAP_PERCENT`     | `1`                              |

---

## 📦 Зависимости

Установлены через `requirements.txt`. Railway автоматически установит зависимости при деплое.
