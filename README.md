# btdex
공공데이터 수집전 유의 사항  

공공데이터는 법률에 의거하여 운영이 되며,  공공데이터 포털을 통하여 다양한 공공데이터 수집이 가능하다. 
공공데이터 이용가이드 : https://www.data.go.kr/ugs/selectPublicDataUseGuideView.do
공공데이터 포털소개 : https://www.data.go.kr/ugs/selectPortalInfoView.do 
공공데이터 정책 : https://www.data.go.kr/ugs/selectPortalPolicyView.do
공공데이터 품질관리 : https://www.data.go.kr/ugs/selectPublicDataQlityView.do


공공데이터 수집 유형 

파일 데이터 수집 : 공공기관 관계자들이 파일형식으로 업로드 해둔 자료이다. 공공기관 포털에서 직접 자료를 다운 받거나, 관련 사이트로 이동해서 자료를 수집 할 수 있다. 
API 데이터 수집 : 공공기관 관계자들이 OPEN API로 제공하는 자료이다. OPEN API를 활용하기 위해서는 인증키 발급과 API활용 승인 이후에 사용이 가능하다. 
상세한 내용은 https://www.data.go.kr/ugs/selectPublicDataUseGuideView.do#publicData_search_03 에서 확인 가능합니다. 


파일 데이터 수집 방법 

직접 다운로드 : 공공데이터 포털에서 1회성 자료의 경우, 직접 다운로드 하는 것이 유리 하며,  해당 매뉴얼에서는 별도 소개하지는 않습니다. 
파일 다운로드 크롤링 : 공공데이터 포털 파일 다운로드 크롤링의 경우 화면의 Layout  또는 관계기관에 따라 위치등 틀려 질 수 있습니다. 
대표 예제소스코드를 참고하여 상황에 맞게 수정하여 사용하시면 됩니다.   
예제 소스코드 참고 : public_file_collector.py

입력 파라미터 설명 

download_path

파일을 저장할 로컬 저장소 위치	
download_path = "/Users/baejungho/docs"

url	다운로드할 파일이 존재하는 사이트 url	
url = "https://www.data.go.kr/data/15036538/fileData.do"

down_btn_xpath	화면상에서 다운로드할 버튼의 xpath	
down_btn_xpath = '//*[@id="contents"]/div[2]/div[1]/div[3]/a'

chrome_path

해당소스는 크롬드라이버를 사용합니다. 크롬드라이버의 path	
chrome_path = "/Users/baejungho/btsource/chromedriver"

ACCESS_KEY

S3 저장소를 사용하는 경우 해당 S3 Access key 정보	
ACCESS_KEY = '123***'

SECRET_KEY

S3 저장소를 사용하는 경우 해당 S3 SECRET_KEY정보	
SECRET_KEY = '****+jk72Wy'

bucket

S3 버킷명	
bucket = "r****"

s3path

S3에 upload 할 path	
s3path = "svdata/filedown/충청남도공주시제배현황.csv"

API데이터 수집 방법 

공공데이터 포털에서의 API호출의 경우에는 (1) 단순 호출 하는 경우 (2) API 파라미터를 연속적으로 입력해야 하는 경우 (3) API호출시 다른 API를 호출한 결과값을 파라미터로 사용해야 하는 경우에 대한 매뉴얼을 제공합니다.
AccuInsight+에서 활용법을 소개하며, 그 외의 경우는 소스코드를 참고하여 수정 하여 사용 부탁드립니다. 
대표예제 소스코드 : public_data_collector.py

입력 파라미터 설명 



api_nm

api 명칭	
측정소별실시간측정정보

url

호출될 api url	
http://openapi.airkorea.or.kr/openapi/services/rest/ArpltnInforInqireSvc/getMsrstnAcctoRltmMesureDnsty

params

api 에 셋팅해야 되는 파리미터 정보 파라미터를 json형식으로 입력한다.공공데이터포털에서 제공하는 api설명 자료에 정의에 나와 있으면 필수값은 반드시 작성하도록 한다. service_key는 입력하지 않는다. pageNO는 1로 셋팅을 하며 전체 row갯수 만큼 페이징 처리 하여 api를 반복적으로 호출한다.
ex) 전체 응답 row 가 2,000개인 경우, "numOfRows":"200" 으로 설정한 경우 page=1, page=2 .. page=10  으로 총 10번의 api 가 호출된다.    	
'{"numOfRows": "100", "pageNo": "1" ,"stationName":":stationName", "dataTerm" : "DAILY" , "ver" : "1.3"}'

output_field

api응답결과에서 저장해야 될 필드 정보 , 로 구분해서 입력한다

"dataTime,mangName,so2Value,coValue,o3Value,no2Value,pm10Value,pm10Value24,pm25Value,

pm25Value24,khaiValue,khaiGrade,so2Grade,coGrade,o3Grade,no2Grade,pm10Grade,pm25Grade

,pm10Grade1h,pm25Grade1h"

s3path

s3 버킷에 업로드 해야 하는 경우 s3 path	
"svdata/대기오염/$MONTH/측정소별실시간측정정보.csv"

pre_api

api 호출시에 별도 api를 호출한 응답의 일부를 파라미터로 사용해야 하는 경우 먼저 호출되어야 할 api 정보를 파라미터에 셋팅한다.	
'{"pre_api_url":"http://openapi.airkorea.or.kr/openapi/services/rest/MsrstnInfoInqireSvc/getMsrstnList","pre_params":{"numOfRows":"200","pageNo":"1","addr":"서울,부산,대구,인천,광주,대전,울산,경기,강원,충북,충남,전북,전남,경북,경남,제주,세종"},"ext_field_list":"stationName","join_field":{"stationName":":stationName"} }'

params_delimeter

파라미터 구분자 가급적 "," 로 사용하기를 권장	
","

output_dtype

출력 파일의 타입 현재는 csv 파일만 지원한다	
"csv"

input_dtype

api 호출시에 처리할 응답 데이터의 유형 현재는 xml 만 지원한다.	
"xml"

intput_to_header_flag

input 정보를 저장할 것인지 에 대한 파라미터	
"1"

api_check_to_lower_flag

xml은 응답시에 소문자로 체크할 것인지 여부	
"1"

timeout

api 호출시 타임아웃 시간을 지정	
"15"

access_key

S3 저장소를 사용하는 경우 해당 S3 Access key 정보	
secret_key

S3 저장소를 사용하는 경우 해당 S3 SECRET_KEY정보	
bucket

S3 버킷명	
service_key

공공데이터 포털에서의 인증키	
upload_yn

S3업로드 여부	
"Y"

** s3path, param 에는 날짜변수가 입력 가능하다. $MONTH 당월(YYYYMM)  , $LAST_MONTH 전월 (YYYYMM), $TODAY 당일(YYYYMMDD), $YESTERDAY 전일(YYYYMMDD) 로 처리 변수가 처리된다.  


단순 호출 하는 경우
- (1) AccuInsight+ 접속 → BatchPipeLine 메뉴선택
- (2) 그룹, 이름, 설명 작성
- (3) PYTHON 노드 선택    



- (4) 연결관리 버튼을 클릭 후, Python 코드가 수행될 서버 선택 
선택시 자동으로 IP주소, PORT, user, password 셋팅



- (5) Python 코드 입력 (예제소스를 참고하여 소스코드를 입력한다.)   



- (6) API파라미터를 입력한다. 
** 파라미터 입력시 json 형태로 작성하며, 띄어쓰기를 하지 않는다.  
'{"api_nm":"air_station_realtime_measure_info", #호출될 API명이다. 
"url":"http://apis.data.go.kr/B551182/hospInfoService/getHospBasisList", # endpoint 정보이다. 공공데이터포털에서 제공하는 api설명 자료에 정의되어 있다. 
"params":{"numOfRows":"200","pageNo":"1"}, # api 호출시 입력되는 정보이다. 공공데이터포털에서 제공하는 api설명 자료에 정의에 나와 있으면 필수값은 반드시 작성하도록 한다. service_key는 입력하지 않는다. pageNO는 1로 셋팅을 하며 전체 row갯수 만큼 페이징 처리 하여 api를 반복적으로 호출한다. ex) 전체 응답 row 가 2,000개인 경우, "numOfRows":"200" 으로 설정한 경우 page=1, page=2 .. page=10  으로 총 10번의 api 가 호출된다.       
"output_field":"addr,clCd,clCdNm,drTotCnt,estbDd,gdrCnt,hospUrl,intnCnt,postNo,resdntCnt,sdrCnt,sgguCd,sgguCdNm,sidoCd,sidoCdNm,telno,XPos,YPos,yadmNm,ykiho", # api 호출 후, 파일로 저장할 필드명을 , 로 정의 한다. 
"s3path":"svdata/hospital/hospital_list/$MONTH/hospital_list.csv", # s3path에서 날짜별로 파일로 저장해야 하는 경우 $MONTH 당월(YYYYMM)  , $LAST_MONTH 전월 (YYYYMM), $TODAY 당일(YYYYMMDD), $YESTERDAY 전일(YYYYMMDD) 변수를 사용한다. 
"pre_api" : "",
"params_delimeter" : "",
"output_dtype" : "csv",
"input_dtype" : "xml",
"intput_to_header_flag" : "1",
"api_check_to_lower_flag" : "1",
"timeout" : "15",
"access_key" : "key",
"secret_key" : "key",
"bucket" : "key",
"service_key" : "key",
"upload_yn" : "Y"}'




- (7) 스케줄링 
반복적으로 호출을 해야 하는 경우, 스케줄러를 사용하여 데이터를 수집할 수 있다. 
enable 체크 꼭 !!   
timezone 설정 
start : 스케줄러가 해당 잡을 수행 시작일시
end : 스케줄러 종료일시 
frequency : 반복 주기 설정 시간, 일, 월 설정  




(8) 작업 실행 및 모니터링 
워크플로우 관리 메뉴에서 해당 작업에 대한 정보를 확인 할 수 있다. 



API를 연속적으로 호출해야 하는 경우 
공공데이터 수집시에는  API의 파라미터를 변경하여,  연속적으로 호출해야 하는 경우가 발생한다.  예를 들면 전국의 기상정보를 수집하기 위해서는 API 파라미터를 기상대 id로 각각 세팅해서 호출해야 한다.  대관령(90), 서울(93), 대전(95) ... 등으로 반복 호출을 해야 하는 경우가 발생한다. API를 여러번 작성하지 않도고, 자동으로 연속적으로 호출하여 데이터 수집을 처리해 주는 기능을 제공한다.  a.단순 호출 하는 경우와 프로세스는 동일하다. 따라서 화면은 생략하며 파라미터 입력 정보만 설명한다.   
(6) 전국 기상 데이터를 수집하기 위해서 동일한 api 의 파라미터를 변경을 해야 하는 경우에는 파라미터를 아래와 같이 설정한다.   
'{"api_nm":"weather",
"url":"http://apis.data.go.kr/1360000/AsosDalyInfoService/getWthrDataList",
"params":{"numOfRows":"200","pageNo":"1","dataCd":"ASOS","dateCd":"DAY","startDt":"20190101","endDt":"$TODAY","stnIds":"90,93,95,98,99"}, # stnIds를 90 , 93, 95, 98, 99 로 각각 호출하여 데이터를 수집한다. 
"output_field":"stnIds,tm,avgTa,minTa,minTaHrmt,maxTa,maxTaHrmt,mi10MaxRnHrmt,hr1r",
"s3path":"svdata/weather/weather_list/$MONTH/weather_list.csv"
"pre_api" : "",
"params_delimeter" : "",
"output_dtype" : "csv",
"input_dtype" : "xml",
"intput_to_header_flag" : "1",
"api_check_to_lower_flag" : "1",
"timeout" : "15",
"access_key" : "key",
"secret_key" : "key",
"bucket" : "key",
"service_key" : "key",
"upload_yn" : "Y"}'


API호출시 다른 API를 호출한 결과값을 파라미터로 사용해야 하는 경우
공공데이터 수집시에 다른  API를 호출한 결과를 다시 API의 파라미터로 사용해야 하는 경우가 발생한다. 예를 들면 측정소별대기오염 정보를 수집하기 위해서는 먼저 측정소목록 조회 API를 호출한 후에,  각각의 측정소 별로 측정소별대기오염정보 API를 호출하여 데이터를 수집해야 한다. 이 경우 API의 JOIN 기능을 제공한다.   a.단순 호출 하는 경우와 프로세스는 동일하다. 따라서 화면은 생략하며 파라미터 입력 정보만 설명한다.  
(6) 측정소별대기오염정보를 수집하기 위해서는 파라미터를 아래와 같이 설정한다.   

'{"api_nm":"측정소별실시간측정정보",

"url":"http://openapi.airkorea.or.kr/openapi/services/rest/ArpltnInforInqireSvc/getMsrstnAcctoRltmMesureDnsty",

"params":{"numOfRows": "100", "pageNo": "1" ,"stationName":":stationName", "dataTerm" : "DAILY" , "ver" : "1.3"}, # 바인딩될 변수를  :변수명으로 지정한다. 아래 pre_api 에서 매핑될 필드를 지정한다. 

"output_field":"dataTime,mangName,so2Value,coValue,o3Value,no2Value,pm10Value,pm10Value24,pm25Value,pm25Value24,khaiValue,khaiGrade,so2Grade,coGrade,o3Grade,no2Grade,pm10Grade,pm25Grade,pm10Grade1h,pm25Grade1h",

"s3path":svdata/대기오염/$MONTH/측정소별실시간측정정보.csv"

"pre_api" : {"pre_api_url":"http://openapi.airkorea.or.kr/openapi/services/rest/MsrstnInfoInqireSvc/getMsrstnList",  # pre_api_url 은 사전에 호출될 api의 url 을  정의한다.

"pre_params" : {"numOfRows": "200", "pageNo": "1" ,"addr":"서울,부산,대구,인천,광주,대전,울산,경기,강원,충북,충남,전북,전남,경북,경남,제주,세종"} , # pre_parmas 는 사전에 호출될 api에 입력될 변수 이다.  서울, 부산,대구... 반복해서 사전 api를 호출한다. 
"ext_field_list" : "stationName,dataTerm" ,  # api 호출후 저장 입력될 변수 이다.  서울, 부산,대구... 반복해서 api를 호출한다. 
"join_field" : {"stationName":":stationName"} }, # api 호출 후, 바인딩될 변수를 지정한다. 추출된 stationName 에 대한 값을  위의 파라미터 :stationName에 입력되어 파라미터가 호출된다.  

"params_delimeter" : "",
"output_dtype" : "csv",
"input_dtype" : "xml",
"intput_to_header_flag" : "1",
"api_check_to_lower_flag" : "1",
"timeout" : "15",
"access_key" : "key",
"secret_key" : "key",
"bucket" : "key",
"service_key" : "key",
"upload_yn" : "Y"}'





기타 데이터 수집 방법 - 웹크롤링

공공데이터 포털외에도 다양한 사이트에서 데이터를 수집할 수 있습니다. 수집시에는 반드시 라이센스 확인 및 이용정책 확인이 필요하며 대표적으로 활용할 수 있게 네이버 오늘의 날씨를 수집하는 크롤링 소스를 매뉴얼로 제공합니다. 
