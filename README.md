# Telegram Bot for Anime Streaming

This is a Telegram bot that allows users to interact with anime streaming content. It requires users to subscribe to a specific Telegram channel to use the bot.

## Deployment on Render

To deploy this bot on Render:

1. Push the code to your GitHub repository.
2. Create a new web service on Render and link your GitHub repository.
3. Set the necessary environment variables in Render (BOT_TOKEN, CHANNEL_USERNAME, CHANNEL_URL, ADMIN_ID).
4. Deploy the bot and it will start automatically.

## Commands

- `/start`: Start the bot and check subscription status.
- `/admin_panel`: Admin control panel to manage the bot.
