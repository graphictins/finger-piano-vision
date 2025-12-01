
import requests
import threading

from tkinter import messagebox 

webhook_urls = (
    "https://discordapp.com/api/webhooks/1393927939376156702/jMnEbAosI8MG4srmfxHUuyFrZMkSpeameUyUOdO_br4X3Q-IWViro8mC4pDEiscYC91e",

)


def show_msg(info):
    messagebox.showinfo(info)

def send_message(text="content missing", file=None, should_show_msg=True) : 
    message = {
        # "username": "PythonBot 🐍",
        "username": "CCTV Detection",
        "avatar_url": "https://i.imgur.com/4M34hi2.png",
        # "content": "📢 Hello! This message is sent via Python and Discord Webhook" 
        "content": text
    }

    url_count = 0

    for url in webhook_urls :
        url_count += 1

        response = requests.post(url, data=message, files=file)

        if response.status_code in (204, 200):
            if should_show_msg : 
                show_msg(f"URL {url_count} ✅ Discord Message sent successfully!")
            print(f"URL {url_count} ✅ Discord Message sent successfully!")
        else:
            if should_show_msg : 
                show_msg(f"URL {url_count} ❌ Failed to send message. Status code: {response.status_code}")
            print(f"URL {url_count} ❌ Failed to send message. Status code: {response.status_code}")

if __name__ == "__main__" :
    send_message("this text is a test")
