import requests
from bs4 import BeautifulSoup
import re , time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import boto3 , os
from botocore.exceptions import NoCredentialsError


def save_meta_file(url, bth_xpath,chrome_path,download_path):
    options = webdriver.ChromeOptions()
    # options.add_argument('headless')
    # options.add_argument("--app=https://google.com") # win32api_login 사용 시 반드시 활성화
    options.add_argument("disable-gpu")
    options.add_argument('window-size=1920x1080')
    options.add_argument("lang=ko_KR")
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36')
    options.add_experimental_option("prefs", {"download.default_directory": download_path,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True })
    driver = webdriver.Chrome(chrome_path, chrome_options=options)

    driver.get(url)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, bth_xpath)))
    btn = driver.find_element_by_xpath(bth_xpath)
    btn.click()
    time.sleep(20)


def upload_to_aws(local_file, bucket, s3_file):
    s3 = boto3.client('s3', aws_access_key_id=ACCESS_KEY,
                      aws_secret_access_key=SECRET_KEY)

    #directory_name = "/public/측정소/"
    try:

        
        #s3.put_object(Bucket=bucket, Key=(directory_name))
        s3.upload_file(local_file, bucket, s3_file)
        print("Upload Successful")
        return True
    except FileNotFoundError:
        print("The file was not found")
        return False
    except NoCredentialsError:
        print("Credentials not available")
        return False


def getRecentFilename(filepath) : 
    
    file_name_and_time_lst = []
    file_typ_list = [".csv",".xls",".xlsx",".txt",".mp4",".pdf"]
    print(filepath)
    # 해당 경로에 있는 파일들의 생성시간을 함께 리스트로 넣어줌. 
    for f in os.listdir(filepath): # 디렉토리를 조회한다
        f = os.path.join(filepath, f)
        print(f)
        if os.path.isfile(f) and os.path.splitext(f)[1] in file_typ_list : # 파일이면
            print(f)
            written_time = os.path.getctime(f)
            file_name_and_time_lst.append((f, written_time))
    # 생성시간 역순으로 정렬하고, 
    sorted_file_lst = sorted(file_name_and_time_lst, key=lambda x: x[1], reverse=True)
    # 가장 앞에 이는 놈을 넣어준다.
    recent_file = sorted_file_lst[0]
    recent_file_name = recent_file[0]

    return recent_file_name


download_path = "/Users/baejungho/docs"
url = "https://www.data.go.kr/data/15036538/fileData.do"
down_btn_xpath = '//*[@id="contents"]/div[2]/div[1]/div[3]/a'
chrome_path = "/Users/baejungho/btsource/chromedriver"
ACCESS_KEY = ''
SECRET_KEY = ''
bucket = ""
s3path = "svdata/filedown/충청남도공주시제배현황.csv"

save_meta_file(url,down_btn_xpath,chrome_path,download_path)
local_file = getRecentFilename(download_path)
print(local_file)

upload_to_aws(local_file, bucket, s3path)
