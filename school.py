import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta

from abc import ABC, abstractmethod

class School(ABC):
    def __init__(self, school_name, activity_url, recruit_url):
        self.activity_url = activity_url
        self.recruit_url = recruit_url
        self.school_name = school_name
        self.activity_list = []
        self.recruit_list = []

    @abstractmethod
    def scrape_website(self, url):
        pass
        
class NTU(School):
    def __init__(self, activity_url, recruit_url):
        super().__init__("NTU", activity_url, recruit_url)
    def scrape_website(self, url):
        try:
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 找到所有公告
            announcements = soup.find_all('tr')
            
            yesterday = datetime.now().date() - timedelta(days=1)
            results = []
            
            for announcement in announcements:
                date_td = announcement.find('td', class_='i-annc__postdate')
                if date_td:
                    date_str = date_td.text.strip()
                    date_str = date_str.replace("\u200b", "")  # Remove any zero-width spaces if present
                    date = datetime.strptime(date_str, '%Y-%m-%d').date()
                    
                    if yesterday - timedelta(days=1) <= date <= yesterday:
                        content_td = announcement.find('td', class_='i-annc__content')
                        if content_td:
                            link_tag = content_td.find('a', class_='i-annc__title')
                            if link_tag:
                                title = link_tag.text.strip()
                                
                                results.append({
                                    'school': self.school_name,
                                    'title': title,
                                    'date': date_str,
                                    'type': 'activity' if url == self.activity_url else 'recruit'
                                })
            
            print(f"Scraped {len(results)} announcements from {self.school_name}\n")
            return results
        except Exception as e:
            print(f"Error scraping {self.school_name}: {str(e)}")
            return []

class NYCU(School):
    def __init__(self, activity_url, recruit_url):
        super().__init__("NYCU", activity_url, recruit_url)

    def scrape_website(self, url):
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            print("status code: ", response.status_code)
            
            # Find all announcement items
            announcements = soup.find_all('li', class_='announcement-item')
            results = []
            
            # Yesterday's date for filtering
            yesterday = datetime.now().date() - timedelta(days=1)
            
            for announcement in announcements:
                # Extract title
                title_tag = announcement.find('h2').find('a')
                title = title_tag.text.strip() if title_tag else None
                
                # Extract date
                time_tag = announcement.find('time')
                date_str = time_tag['datetime'] if time_tag and 'datetime' in time_tag.attrs else None
                date = datetime.strptime(date_str, '%Y-%m-%d %H:%M').date() if date_str else None
                
                # Filter announcements by date
                if date and yesterday - timedelta(days=1) <= date <= yesterday:
                    # Extract link
                    # link = title_tag['href'] if title_tag and 'href' in title_tag.attrs else None
                    
                    # If the link is relative, convert it to an absolute URL
                    # if link and link.startswith('/'):
                    #     link = f"https://www.cs.nycu.edu.tw{link}"
                    
                    # Append the announcement to results
                    results.append({
                        'school': self.school_name,
                        'title': title,
                        # 'link': link,
                        'date': date_str,
                        'type': 'activity' if url == self.activity_url else 'recruit'
                    })
            
            print(f"Scraped {len(results)} announcements from {self.school_name}\n")
            return results
        except Exception as e:
            print(f"Error scraping {self.school_name}: {str(e)}")
            return []
        
class NCKU(School):
    def __init__(self, activity_url, recruit_url):
        super().__init__("NCKU", activity_url, recruit_url)

    def scrape_website(self, url):
        try:
            response = requests.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find all announcement items
            announcements = soup.find_all('li', class_='li-title')
            results = []
            
            # Yesterday's date for filtering
            yesterday = datetime.now().date() - timedelta(days=1)
            # yesterday = datetime.strptime('2025-03-18', '%Y-%m-%d').date()
            
            for announcement in announcements:
                # Extract title
                title_tag = announcement.find('a')
                title = title_tag.text.strip() if title_tag else None
                
                # Extract date
                date_tag = announcement.find('small', class_='float-right')
                date_str = date_tag.text.strip() if date_tag else None
                date = datetime.strptime(date_str, '%Y.%m.%d').date() if date_str else None
                
                # Filter announcements by date
                if date and yesterday - timedelta(days=1) <= date <= yesterday:
                    # Extract link
                    link = title_tag['href'] if title_tag and 'href' in title_tag.attrs else None
                    
                    # If the link is relative, convert it to an absolute URL
                    if link and link.startswith('/'):
                        link = f"https://www.csie.ncku.edu.tw{link}"
                    
                    # Append the announcement to results
                    results.append({
                        'school': self.school_name,
                        'title': title,
                        'link': link,
                        'date': date_str,
                        'type': 'activity' if url == self.activity_url else 'recruit'
                    })
            
            print(f"Scraped {len(results)} announcements from {self.school_name}\n")
            return results
        except Exception as e:
            print(f"Error scraping {self.school_name}: {str(e)}")
            return []
        

def message_format(all_announcements, schools):
    message = "昨日活動訊息：\n"
    for school in schools:
        message += f"【{school.school_name}】"
        if len([announcement for announcement in all_announcements if (announcement['school'] == school.school_name and announcement['type'] == 'activity')]) == 0:
            message += "無\n"
        else:
            message += '\n'
            for announcement in all_announcements:
                if announcement['school'] == school.school_name and announcement['type'] == 'activity':
                    message += f"⭐{announcement['title']}\n"
        message += "看更多："+ school.activity_url + "\n"
    message += "------------------------\n"
    message += "昨日徵才訊息：\n"
    for school in schools:
        message += f"【{school.school_name}】"
        if len([announcement for announcement in all_announcements if (announcement['school'] == school.school_name and announcement['type'] == 'recruit')]) == 0:
            message += "無\n"
        else:
            message += '\n'
            for announcement in all_announcements:
                if announcement['school'] == school.school_name and announcement['type'] == 'recruit':
                    message += f"⭐{announcement['title']}\n"
        message += "看更多："+ school.recruit_url + "\n"
    return message

if __name__ == "__main__":
    NTU = NTU("https://www.csie.ntu.edu.tw/zh_tw/Announcements/Announcement9", "https://www.csie.ntu.edu.tw/zh_tw/Announcements/Announcement10")
    NYCU = NYCU("https://www.cs.nycu.edu.tw/announcements/activity", "https://www.cs.nycu.edu.tw/announcements/corporation")
    NCKU = NCKU("https://www.csie.ncku.edu.tw/zh-hant/news/speeches", "https://www.csie.ncku.edu.tw/zh-hant/news/jobs")
    
    all_announcements = []
    all_announcements.extend(NTU.scrape_website(NTU.activity_url))
    all_announcements.extend(NYCU.scrape_website(NYCU.activity_url))
    all_announcements.extend(NCKU.scrape_website(NCKU.activity_url))
    all_announcements.extend(NTU.scrape_website(NTU.recruit_url))
    all_announcements.extend(NYCU.scrape_website(NYCU.recruit_url))
    all_announcements.extend(NCKU.scrape_website(NCKU.recruit_url))

    message = message_format(all_announcements, [NTU, NYCU, NCKU])
    print(message)