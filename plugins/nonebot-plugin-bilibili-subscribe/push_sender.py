import os
import requests

class PushSender:
    def __init__(self) -> None:
        self.is_sent = False
    def send_push_notification(self, title, content):
        url = "http://www.pushplus.plus/send"
        token = os.environ.get("TOKEN")
        if not token:
            print("Please set the TOKEN environment variable.")
            return
        template = "markdown"

        payload = {
            "token": token,
            "title": title,
            "content": content,
            "template": template
        }

        response = requests.post(url, data=payload, timeout=5)
        if response.status_code == 200:
            print("Push notification sent successfully.")
            self.is_sent = True
        else:
            print("Failed to send push notification.")
    
    def reset(self):
        self.is_sent = False
