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
    NTU_inst = school.NTU("https://www.csie.ntu.edu.tw/zh_tw/Announcements/Announcement9", "https://www.csie.ntu.edu.tw/zh_tw/Announcements/Announcement10")
    NYCU_inst = school.NYCU("https://www.cs.nycu.edu.tw/announcements/activity", "https://www.cs.nycu.edu.tw/announcements/corporation")
    NCKU_inst = school.NCKU("https://www.csie.ncku.edu.tw/zh-hant/news/speeches", "https://www.csie.ncku.edu.tw/zh-hant/news/jobs")
    
    all_announcements = []
    all_announcements.extend(NTU_inst.scrape_website(NTU_inst.activity_url))
    all_announcements.extend(NYCU_inst.scrape_website(NYCU_inst.activity_url))
    all_announcements.extend(NCKU_inst.scrape_website(NCKU_inst.activity_url))
    all_announcements.extend(NTU_inst.scrape_website(NTU_inst.recruit_url))
    all_announcements.extend(NYCU_inst.scrape_website(NYCU_inst.recruit_url))
    all_announcements.extend(NCKU_inst.scrape_website(NCKU_inst.recruit_url))

    message = school.message_format(all_announcements, [NTU_inst, NYCU_inst, NCKU_inst])
    send_line_message(message)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--daily-task", action="store_true", help="Run the daily task")
    args = parser.parse_args()

    if args.daily_task:
        daily_task()
    