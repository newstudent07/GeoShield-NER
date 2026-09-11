import os
import httpx

def send_telegram_alert(message: str):
    """
    Sends a message via the Telegram Bot HTTP API.
    """
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    if not token or not chat_id or token == "your_token_here":
        print(f"Telegram Notification Skipped (No valid token): {message}")
        return
        
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message
    }
    
    try:
        with httpx.Client(timeout=5.0) as client:
            res = client.post(url, json=payload)
            res.raise_for_status()
            print("Telegram alert dispatched successfully.")
    except Exception as e:
        print(f"Failed to send Telegram alert: {e}")
