import requests
import  json

def main():
    s = requests.Session()
    url = "https://eloszto.mvmemaszhalozat.hu/usz(bD1odSZjPTExMg==)/dso/mvm/index.html#"
    r = s.get(url)
    #print(r.text)

    url = "https://eloszto.mvmemaszhalozat.hu/sap/opu/odata/sap/ZGW_UGYFELSZLG_CMS_NO_AUTH_SRV/Szovegek"
    querystring = {"sap-client":"112","sap-language":"HU","$filter":"Funkcio eq 'AKADALYMEN'"}
    r = s.get(url, params=querystring)
    #print(r.text)

    url = "https://eloszto.mvmemaszhalozat.hu/sap/opu/odata/sap/ZGW_UGYFELSZOLGALAT_LOGIN_SRV/Login"
    querystring = {"sap-client":"112","sap-language":"HU"}
    payload = {
                "Username": "",
                "Password": ""}
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


    url = "https://eloszto.mvmemaszhalozat.hu/sap/opu/odata/sap/ZGW_UGYFELSZOLGALAT_SRV/Vevok"
    headers["Authorization"] = f"Bearer {token}"
    querystring = {"Funkcio":"OKOSMERO","sap-client":"112","sap-language":"HU"}
    r = s.get(url, headers=headers, params=querystring)
    custumer_number = r.json()["d"]["results"][0]["Id"]


    url = f"https://eloszto.mvmemaszhalozat.hu/sap/opu/odata/sap/ZGW_UGYFELSZOLGALAT_SRV/Vevok(\'{custumer_number}\')/Felhelyek"
    querystring = {"Funkcio":"OKOSMERO","sap-client":"112","sap-language":"HU"}
    r = s.get(url, headers=headers, params=querystring)
    customer_id = r.json()["d"]["results"][0]["Id"]
    

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
    
    url=f"{smart_meter_links[0]['url']}"
    sap_client = "100"
    guid = smart_meter_links[0]["guid"]
    query_string = {"guid":guid, "sap-client":sap_client}
    
    
    
    r = s.get(url, headers=headers, params=query_string)
    print(r.status_code)
    print(r.history)
    a = r.url
    a = a.split("(")
    a = a[1].split(")")
    
    sap_id = a[0]
    
    url_1 = f"{url}({sap_id})/oldal_1.htm"
    r = s.get(url_1, headers=headers)
    print(r.status_code)
    print(r.history)
    #print(r.text)

    post_data = {"accept": "on","OnInputProcessing(tovabb)": ""}
    r = s.post(url_1, headers=headers, data=post_data)
    print(r.history)
    print(r.status_code)
    #print(r.text)


    
    
    url_2 = f"{url}({sap_id})/Oldal_2.htm"
    r = s.get(url_2, headers=headers)
    #print(r.text)
    
    #query_string = {"OnInputProcessing(ToTerhGor1)":""}
    r = s.get(f"{url_2}?OnInputProcessing(ToTerhGor1)=")
    print(r.history)
    print(r.status_code)
    #print(r.text)
    '''
    url_3 = f"{url}({sap_id})/Oldal_3.htm"
    r = s.get(url_3, headers=headers)
    print(r.status_code)
    print(r.history)
    print(r.text)
    '''
    
    url_3 = f"{url}({sap_id})/showPDF.htm?type=1"
    query_string = {"type":"1"}
    r = s.get(url_3)
    print(r.history)
    print(r.status_code)
    print(r.text)
    

if __name__ == "__main__":
    main()