import logging
import argparse
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *
import school
import os

line_bot_api = LineBotApi(os.environ['CHANNEL_ACCESS_TOKEN'])

# 設置日誌
logging.basicConfig(level=logging.INFO, format='%(asctime)s:%(levelname)s:%(message)s')

def send_line_message(message):
    try:
        line_bot_api.broadcast(TextSendMessage(text=message))
        logging.info("Line message sent successfully")
    except Exception as e:
        logging.error(f"Error sending Line message: {str(e)}")

def daily_task():
    logging.info("Starting daily scraping task")
    NTU = school.NTU("https://www.csie.ntu.edu.tw/zh_tw/Announcements/Announcement9", "https://www.csie.ntu.edu.tw/zh_tw/Announcements/Announcement10")
    NYCU = school.NYCU("https://www.cs.nycu.edu.tw/announcements/activity", "https://www.cs.nycu.edu.tw/announcements/corporation")
    NCKU = school.NCKU("https://www.csie.ncku.edu.tw/zh-hant/news/speeches", "https://www.csie.ncku.edu.tw/zh-hant/news/jobs")
    
    all_announcements = []
    all_announcements.extend(NTU.scrape_website(NTU.activity_url))
    all_announcements.extend(NYCU.scrape_website(NYCU.activity_url))
    all_announcements.extend(NCKU.scrape_website(NCKU.activity_url))
    all_announcements.extend(NTU.scrape_website(NTU.recruit_url))
    all_announcements.extend(NYCU.scrape_website(NYCU.recruit_url))
    all_announcements.extend(NCKU.scrape_website(NCKU.recruit_url))

    message = school.message_format(all_announcements, [NTU, NYCU, NCKU])
    send_line_message(message)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--daily-task", action="store_true", help="Run the daily task")
    args = parser.parse_args()

    if args.daily_task:
        daily_task()