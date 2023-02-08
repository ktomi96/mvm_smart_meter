import os
import requests
import  json

import dotenv

from requestium import Session, Keys
from selenium import webdriver
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.options import Options
options = Options()
options.add_argument("--headless")
firefox_driver = webdriver.Firefox(executable_path=GeckoDriverManager().install(), options=options)


env_path = ("./env/")
env_file = f"{env_path}config.env"
dotenv.find_dotenv(env_file, raise_error_if_not_found=True)
dotenv.load_dotenv(env_file)

username = os.getenv("USERNAME")
password = os.getenv("PASSWORD")


def main():
    s = Session(driver=firefox_driver)
    s.headers.update({"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/109.0"})
    url = "https://eloszto.mvmemaszhalozat.hu"
    r = s.get(url)
    response_url= r.url
    split_url = response_url.split("(")[1]
    sap_id = split_url.split(")")[0]
    #print(r.url)
    #print(r.status_code)
    main_url = f"{url}({sap_id})"
    

    url = "https://eloszto.mvmemaszhalozat.hu/sap/opu/odata/sap/ZGW_UGYFELSZLG_CMS_NO_AUTH_SRV/Szovegek"
    querystring = {"sap-client":"112","sap-language":"HU","$filter":"Funkcio eq 'AKADALYMEN'"}
    r = s.get(url, params=querystring)
    #print(r.text)

    url = "https://eloszto.mvmemaszhalozat.hu/sap/opu/odata/sap/ZGW_UGYFELSZOLGALAT_LOGIN_SRV/Login"
    querystring = {"sap-client":"112","sap-language":"HU"}
    payload = {
                "Username": username,
                "Password": password}
    headers = {
    "Accept": "application/json",
    "X-Requested-With": "X",
    "Content-Type": "application/json"
    }
    s.cookies.set("cookiePanelAccepted", "1")
    r = s.post(url, json=payload, headers=headers, params=querystring)
    r_dict = r.json()
    authcode = r_dict["d"]["AuthCode"]



    url = "https://eloszto.mvmemaszhalozat.hu/sap/opu/odata/sap/ZGW_OAUTH_SRV/GetToken"
    querystring = {"Code":f'\'{authcode}\'',"sap-client":"112","sap-language":"HU"}
    r = s.get(url, headers=headers, params=querystring)
    token_r_dict = r.json()
    token = token_r_dict["d"]["GetToken"]["TokenCode"]
    #print(r.status_code)

    url = "https://eloszto.mvmemaszhalozat.hu/sap/opu/odata/sap/ZGW_UGYFELSZOLGALAT_SRV/Vevok"
    headers["Authorization"] = f"Bearer {token}"
    querystring = {"Funkcio":"OKOSMERO","sap-client":"112","sap-language":"HU"}
    r = s.get(url, headers=headers, params=querystring)
    custumer_number = r.json()["d"]["results"][0]["Id"]
    #print(r.status_code)

    url = f"https://eloszto.mvmemaszhalozat.hu/sap/opu/odata/sap/ZGW_UGYFELSZOLGALAT_SRV/Vevok(\'{custumer_number}\')/Felhelyek"
    querystring = {"Funkcio":"OKOSMERO","sap-client":"112","sap-language":"HU"}
    r = s.get(url, headers=headers, params=querystring)
    customer_id = r.json()["d"]["results"][0]["Id"]
    #print(r.status_code)

    url = f"https://eloszto.mvmemaszhalozat.hu/sap/opu/odata/sap/ZGW_UGYFELSZOLGALAT_SRV/Felhelyek(Vevo=\'{custumer_number}\',Id=\'{customer_id}\')/Okosmero"
    querystring = {"sap-client":"112","sap-language":"HU"}
    r = s.get(url, headers=headers, params=querystring)
    r_list = r.json()["d"]["results"]
    smart_meter_links = []
    
    for link in r_list :
        if link["URL"].find("guid=&") == -1:
            split_url = link["URL"].split('?')
            query_string = split_url[1]

            query_string_list = query_string.split('&')

            query_dict = {"url":split_url[0]}
            for item in query_string_list:
                key, value = item.split('=')
                query_dict[key] = value
            smart_meter_links.append(query_dict)
    
    smart_meter_url=f"{smart_meter_links[0]['url']}"
    print(f"Smart meter link : {smart_meter_url}")
    sap_client = "100"
    guid = smart_meter_links[0]["guid"]
 
    s.transfer_session_cookies_to_driver(domain=f"{smart_meter_url}?guid={guid}&sap-client={sap_client}")

    print(f"{smart_meter_url}?guid={guid}&sap-client={sap_client}")
    response = s.driver.get(f"{smart_meter_url}?guid={guid}&sap-client={sap_client}")
    #print(response.text)
    
    response_url= s.driver.current_url
    split_url = response_url.split("(")[1]
    sap_id = split_url.split(")")[0]

    s.cookies.pop("sap-usercontext")
    s.cookies.set("sap-usercontext","sap-language=HU&sap-client=100")
    s.transfer_driver_cookies_to_session()
    
    first_page_url = f"{smart_meter_url}({sap_id})/oldal_1.htm"

    r = s.get(first_page_url)
    print(r.status_code)
    print(r.text)
    response = s.get('https://eloszto.mvmemaszhalozat.hu/favicon.ico')
    print(response.status_code)
    

    response = s.get(f"{smart_meter_url}({sap_id})/style.css")
    print(response.status_code)
  
    response = s.get(f"{smart_meter_url}({sap_id})/script/checkbox.js")
    print(response.status_code)


    
    response = s.get(f"{smart_meter_url}({sap_id})/script/checkbox.png")
    print(response.status_code)

    data = {
        'accept': 'on',
        'OnInputProcessing(tovabb)': '',
    }
    
    print(first_page_url)
    s.headers.update({'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8', 
    'Origin': 'https://eloszto.mvmemaszhalozat.hu', 'Upgrade-Insecure-Requests': '1',
     'Referer': f'https://eloszto.mvmemaszhalozat.hu/SMMU({sap_id})/oldal_1.htm'})
    r = s.post(first_page_url, data=data)
    
    print(r.status_code)
    print(r.text)
    print(r.request.headers)
    for resp in r.history:
        print(resp.url)
   
   
    second_page_url = f"{smart_meter_url}({sap_id})/Oldal_2.htm?OnInputProcessing(ToTerhGor1)"
    print(second_page_url)
    r = s.get(second_page_url)
    print(r.status_code)
    print(r.text)
    

    
    
    smart_meter_page2_url = f"{smart_meter_url}({sap_id})/Oldal_2.htm?OnInputProcessing(ToTerhGor1)"
    r = s.get(smart_meter_page2_url)
    print(r.text)
    

    r = s.get(f"{smart_meter_page2_url}?OnInputProcessing(ToTerhGor1)")
    #print(r.history)
    print(r.status_code)
    #print(r.text)
    
  
    smart_meter_page3_url = f"{smart_meter_url}({sap_id})/showPDF.htm?type=1"
    query_string = {"type":"1"}
    r = s.get(smart_meter_page3_url)
    print(r.history)
    print(r.status_code)
    print(r.text)
    

if __name__ == "__main__":
    main()