# Deploy on bot-hosting.net

1. Create a Discord application at [Discord Developer Portal](https://discord.com/developers/applications).
2. Enable **Bot** intent: **Server Members Intent** and **Message Content Intent** (for hybrid prefix if needed).
3. Copy the bot token and client ID into your hosting panel environment variables (see `.env.example`).
4. Upload the `bot/` folder or connect your Git repo; set **main file** to `main.py`.
5. Install command: `pip install -r requirements.txt`
6. Invite URL (replace CLIENT_ID):

```
https://discord.com/api/oauth2/authorize?client_id=CLIENT_ID&permissions=268443648&scope=bot%20applications.commands
```

Use the same `MONGODB_URI` and `API_SECRET` as the FastAPI dashboard API.
