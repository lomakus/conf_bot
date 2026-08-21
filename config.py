import os
from dotenv import load_dotenv

load_dotenv()

# VK
VK_BOT_TOKEN = os.getenv("VK_BOT_TOKEN")
if not VK_BOT_TOKEN:
    raise ValueError("❌ VK_BOT_TOKEN не найден в .env!")

# Telegram (пока не используется)
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# # Admin IDs
# ADMIN_TELEGRAM_ID = int(os.getenv("ADMIN_TELEGRAM_ID", "0"))
# ADMIN_VK_ID = int(os.getenv("ADMIN_VK_ID", "0"))

# VK
VK_REVIEW_CHAT_ID = os.getenv("VK_REVIEW_CHAT_ID")
VK_NOTIFICATIONS_CHAT_ID = os.getenv("VK_NOTIFICATIONS_CHAT_ID")
VK_PULS_CHAT_ID = os.getenv("VK_PULS_CHAT_ID")
