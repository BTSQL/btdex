#-*- coding:utf-8 -*-
"""
메타 데이터를 읽어서 
api 정보를 호출하고 정보를 S3버킷에 업로드 한다. 
"""
import requests
import json, os
from bs4 import BeautifulSoup
from openpyxl import Workbook, load_workbook
from datetime import datetime, timedelta
import boto3
from botocore.exceptions import NoCredentialsError
import time
import argparse
from itertools import product
import pandas as pd

class ApiCaller() :
    def __init__ (self, access_key, secret_key, bucket, service_key) :
        """
        config파일을 읽어 DB와 service 키를 셋팅
        db 연결 
        """
        self.sev_key = service_key
        self.HEADER = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36,gzip(gfe)"}
        self.bucket = bucket
        self.s3 = boto3.client('s3', aws_access_key_id=access_key, aws_secret_access_key=secret_key)

    def replaceBindDate(self,bind_var) :
        if isinstance(bind_var,str) : 
            n_var = bind_var.replace("$TODAY",self.getDate("$TODAY")).replace("$YESTERDAY",self.getDate("$YESTERDAY")).replace("$MONTH",self.getDate("$MONTH")).replace("$LASTMONTH",self.getDate("$LASTMONTH"))
            return n_var

        return bind_var

    # 옵션에 따른 날짜를 구한다 
    # 당일날짜 $TODAY
    # 어제날짜 $YESDERDAY
    def getDate(self, option_var):
        ndate = datetime.now()

        if option_var == "$TODAY" :
            return ndate.strftime("%Y%m%d")

        elif option_var== "$YESTERDAY" : 
            ydate =  ndate - timedelta(days=1)
            return ydate.strftime("%Y%m%d")

        elif option_var=="$MONTH" :
            return ndate.strftime("%Y%m")
        
        elif option_var=="$LASTMONTH" :
            lastmonth = ndate - timedelta(days=30)
            return lastmonth.strftime("%Y%m")


    def getApiEndPointList(self, url, json_args, deli, timeout_delay) :
        param_list = []
        api_list = []
        rowcnt = 0
        param = url + "?serviceKey=" + self.sev_key
        rowcnt = int(json_args["numOfRows"])

        for key, value in json_args.items() :
            value = value.split(deli)
            p_list = []
            for p in value :
                p_list.append("&" + key + "=" + p)
            
            param_list.append(p_list)
            
        param_list = list(product(*param_list))

        for pp in param_list :
            endpoint = param+"".join(pp)
            print("endpoint is {0}".format(endpoint))
            time.sleep(1)
            r = requests.get(endpoint, headers=self.HEADER,timeout=timeout_delay)
            bs = BeautifulSoup(r.text, "lxml")
            cnt = bs.select("totalcount")
            if len(cnt) > 0 :
                cnt = int(cnt[0].text)
                print("totcout : {0}".format(cnt))
                ## 페이지 갯수 만큼 호출 api를 만든다
                totpage = int(cnt / rowcnt )+ 1
                for i in range(1,totpage+1) :
                    page_param = "pageNo="+str(i)
                    print(page_param)
                    api_list.append(endpoint.replace("pageNo=1",page_param))

        return api_list
    
    
    def callNApi(self, endpoint,s3path,wirte_mode,output_field,params,file_header,sudo_output,intput_to_header_flag,timeout_delay) : 
        """
        API를 호출한다 
        """
        dt_string = datetime.now().strftime("%Y-%m-%d:%H%M%S")
        try :
            dir_path = s3path.split("/")
            file_name = dir_path.pop()
            dir_path = ("/").join(dir_path)
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)

            print(dir_path)
            print(file_name)
            
            # 로컬에 파일이 있으면 덮어쓰고 없으면 신규로 만든다. 
            is_exists = os.path.exists(s3path)

            f = open(s3path,wirte_mode,encoding="utf-8")
            

            # 파일이 없는 경우에 헤더를 쓴다 
            if is_exists : 
                pass
            else : 
                header = ",".join(file_header) + "," + ",".join(output_field)
                print(header)

                f.writelines(",".join(file_header)+ "," + ",".join(output_field))

            r = requests.get(endpoint, headers=self.HEADER, timeout=timeout_delay)
            bs = BeautifulSoup(r.text, "lxml")
            items = bs.select("items > item")
            if len(items) > 0 :
                for item in items :
                    try :
                        fileinfo = []
                        fileinfo.append(dt_string)
                        if intput_to_header_flag == "1" : 
                            [fileinfo.append(sudo.split("=")[1]) for sudo in sudo_output]
                        
                        for field in output_field :
                            test = item.select(field)
                            if len(test) > 0 : 
                                fileinfo.append(item.select(field)[0].text.replace(",","/"))
                        f.write('\n')
                        print(fileinfo)
                        f.writelines(",".join(fileinfo))
                    except Exception as e :
                        print(e)    
            f.close()

        except requests.Timeout :
            print(" Time Out " )
            f.close() 
        except Exception as e : 
            print (e)
            f.close()

    def getTotCnt(self, url) : 
        r = requests.get(url, headers=self.HEADER)
        bs = BeautifulSoup(r.text, "lxml")
        cnt = bs.select("totalcount")

        if len(cnt) > 0 :
            return int(cnt[0].text) 
        return 0
    
    def upload_to_aws(self, local_file, s3_file):
        try:
            self.s3.upload_file(local_file, self.bucket, s3_file)
            print("Upload Successful")
            return True
        except FileNotFoundError:
            print("The file was not found")
            return False
        except NoCredentialsError:
            print("Credentials not available")
            return False

    def start(self, api_nm,url,params,output_field,s3path,pre_api,params_delimeter,output_dtype,input_dtype,intput_to_header_flag,timeout_delay) : 

        # 파라미터 치환
        params = self.replaceBindDate(params)
        url = self.replaceBindDate(url)
        s3path = self.replaceBindDate(s3path)

        # 파라미터 검증
        # api url 조합 (pre_api 등)
        if len(pre_api) > 0 :
            j_param = json.loads(pre_api)
            print("pre api")             
            # 파라미터 로드 
            #j_param = json.loads(pre_api)
            # 매핑 컬럼 및 파일 조정 
            pre_api_url = j_param["pre_api_url"]
            ext_field_list = j_param["ext_field_list"]
            # 대소문자시 파싱 오류로 소문자로 변환하여 처리 
            ext_field_list = ext_field_list.lower()
            pre_params = json.dumps(j_param["pre_params"],ensure_ascii=False)
            join_field = json.dumps(j_param["join_field"],ensure_ascii=False)

            join_field = json.loads(join_field)

            print(pre_api_url, pre_params, ext_field_list, join_field)

            # pre_api 부터 호출해서 파일에 저장한다. 
            # append 모드로 저장하며 작업 후에는 삭제 하도록 한다. 
            local_path = "./tmp/"+api_nm+".csv"

            self.start(api_nm,pre_api_url,pre_params,ext_field_list,local_path,"",params_delimeter,output_dtype,input_dtype,"0",timeout_delay)
            print("done")
            pre_data = pd.read_csv(local_path)
            #필드 저장은 소문자로 되기 때문에 value에 대문자가 포함된 경우는 소문자로 key를 변경
            for index, row in pre_data.iterrows():
                #udefine 핃르 
                gubun = []
                for key, value in join_field.items():
                    sub_params = params.replace(value,row[key.lower()])
                    gubun.append(row[key.lower()])
                print(sub_params)
                print(gubun)
                self.start(api_nm,url,sub_params,output_field,s3path,"",params_delimeter,output_dtype,input_dtype,"1",timeout_delay)
            
            # 로컬의 임시 파일은 작업 후 삭제 한다. 
            os.remove(local_path)

        else : 
            # 소문자로 체크하기 원래 xml 대소문자 체크안하나, 대문자 포함된 경우 accu에서 호출시 인식 못함
            if api_check_to_lower_flag == "1" : 
                output_field = output_field.lower()
                output_field = output_field.split(",")

            if len(timeout_delay) > 0 : 
                timeout_delay = int(timeout_delay)
            else : 
                timeout_delay = 10
                
            params = json.loads(params)
            file_header = ["api호출일시"]
            wirte_mode = "a+t"

            print("file_header : {0}".format(file_header))
            #print(file_header)
            print("apinm : {0}".format(api_nm))
            print("url : {0}".format(url))
            print("params : {0}".format(params))  
            print("output_field : {0}".format(output_field))
            print("s3path : {0}".format(s3path))
            print("pre_api : {0}".format(pre_api))
            print("params_delimeter : {0}".format(params_delimeter))
            print("output_dtype : {0}".format(output_dtype))
            print("input_dtype : {0}".format(input_dtype))
            print("intput_to_header_flag : {0}".format(intput_to_header_flag))

            if intput_to_header_flag == "1" :
                for key, value in params.items():
                    file_header.append(key)

            api_list = self.getApiEndPointList(url,params,params_delimeter,timeout_delay)
            for endpoint in api_list :
                print(endpoint)
                sudo_output = endpoint.split("&")[1:]
                print(sudo_output)
                time.sleep(1)
                self.callNApi(endpoint,s3path,wirte_mode,output_field,params,file_header,sudo_output,intput_to_header_flag,timeout_delay)


"""
parser = argparse.ArgumentParser()
parser.add_argument("param", type=str) # json양식으로 작성된 input 파라미터를 받아온다.   
args = parser.parse_args()

json_param = json.loads(args.param)

api_nm = json_param["api_nm"]
url = json_param["url"]
params = json.dumps(json_param["params"],ensure_ascii=False)
output_field = json_param["output_field"]
s3path = json_param["s3path"]
pre_api = json_param["pre_api"]

## pre_api 가 있을 때만 
if len(pre_api) > 0 :
    pre_api = json.dumps(json_param["pre_api"],ensure_ascii=False)
    
params_delimeter = json_param["params_delimeter"]
output_dtype = json_param["output_dtype"] 
input_dtype =  json_param["input_dtype"]
intput_to_header_flag = json_param["intput_to_header_flag"]
api_check_to_lower_flag = json_param["api_check_to_lower_flag"]
timeout = json_param["timeout"]
access_key = json_param["access_key"]
secret_key = json_param["secret_key"]
bucket = json_param["bucket"]
upload_yn = json_param["upload_yn"]
service_key = json_param["service_key"]

"""

api_nm = "측정소별실시간측정정보"
url = "http://openapi.airkorea.or.kr/openapi/services/rest/ArpltnInforInqireSvc/getMsrstnAcctoRltmMesureDnsty"
params ='{"numOfRows": "100", "pageNo": "1" ,"stationName":":stationName", "dataTerm" : "DAILY" , "ver" : "1.3"}'
output_field = "dataTime,mangName,so2Value,coValue,o3Value,no2Value,pm10Value,pm10Value24,pm25Value,pm25Value24,khaiValue,khaiGrade,so2Grade,coGrade,o3Grade,no2Grade,pm10Grade,pm25Grade,pm10Grade1h,pm25Grade1h"
s3path = "svdata/대기오염/$MONTH/측정소별실시간측정정보.csv"
pre_api = '{"pre_api_url":"http://openapi.airkorea.or.kr/openapi/services/rest/MsrstnInfoInqireSvc/getMsrstnList","pre_params":{"numOfRows":"200","pageNo":"1","addr":"서울,부산,대구,인천,광주,대전,울산,경기,강원,충북,충남,전북,전남,경북,경남,제주,세종"},"ext_field_list":"stationName","join_field":{"stationName":":stationName"} }'
params_delimeter =","
output_dtype = "csv"  
input_dtype =  "xml" 
intput_to_header_flag = "1" 
api_check_to_lower_flag = "1"
timeout = "15"
access_key = ""
secret_key = ""
bucket = ""
service_key = ""
upload_yn = "N"


# 객체 생성 
myapi = ApiCaller(access_key,secret_key,bucket,service_key)

# 수집함수 호출 
myapi.start(api_nm,url,params,output_field,s3path,pre_api,params_delimeter,output_dtype,input_dtype,intput_to_header_flag,timeout)

#s3 upload
if len(upload_yn) > 0 and upload_yn == "Y" : 
    myapi.upload_to_aws(s3path, s3path)