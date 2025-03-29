# Telegram Notification & Calendar Bot

## Project Structure

```
tg_bot_notificator/
│── public/
│── src/
│   ├── assets/
│   ├── components/
│   ├── hooks/
│   ├── pages/
│   ├── styles/
│   ├── utils/
│   ├── App.tsx
│   ├── main.tsx
│── .env
│── index.html
│── package.json
│── tsconfig.json
│── vite.config.ts
│── README.md
```


## Example Usage
Go to @BotFather bot and get your Bot Token. Then create and fill `.env` file:
```bash
nano .env
```
Example of `.env`:
```.env
BOT_TOKEN="YOUR_TOKEN_FROM_BOT_FATHER"
```

```bash
npm install @fullcalendar/react @fullcalendar/daygrid @fullcalendar/interaction axios
```