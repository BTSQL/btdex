# 네이버 오늘의 날씨 크롤링 하여 파일 저장 하기
import requests
from bs4 import BeautifulSoup
from openpyxl import Workbook, load_workbook

def getTemp(url,header, timeout_delay=10) : 
    r = requests.get(url, headers=header,timeout=timeout_delay)
    bs = BeautifulSoup(r.text, "lxml")
    temp = bs.select("div.today_area._mainTabContent > div.main_info > div > p > span.todaytemp")
    print(temp[0].text)
    
header = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36,gzip(gfe)"}
url = "https://search.naver.com/search.naver?sm=top_hty&fbm=1&ie=utf8&query=%EB%82%A0%EC%94%A8"

getTemp(url,header)