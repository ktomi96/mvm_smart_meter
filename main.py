import os
import requests
import json


from requestium import Session, Keys
from selenium import webdriver
from webdriver_manager.firefox import GeckoDriverManager
from selenium.webdriver.firefox.options import Options
import pandas
import io


class Smart_meter():
    def __init__(self, username, password):
        self.options = Options()
        self.options.add_argument("--headless")
        self.firefox_driver = webdriver.Firefox(
            executable_path=GeckoDriverManager().install(), options=self.options
        )
        self.s = Session(driver=self.firefox_driver)
        self.s.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/109.0"
            }
        )
        self.base_url = "https://eloszto.mvmemaszhalozat.hu"
        self.username = username
        self.password = password

    def get_base_cookies(self):
        r = self.s.get(self.base_url)
        response_url = r.url
        split_url = response_url.split("(")[1]
        self.sap_id = split_url.split(")")[0]
        # print(r.url)

    def get_login_cookies(self):
        url = "https://eloszto.mvmemaszhalozat.hu/sap/opu/odata/sap/ZGW_UGYFELSZLG_CMS_NO_AUTH_SRV/Szovegek"
        querystring = {
            "sap-client": "112",
            "sap-language": "HU",
            "$filter": "Funkcio eq 'AKADALYMEN'",
        }
        r = self.s.get(url, params=querystring)

        login_url = "https://eloszto.mvmemaszhalozat.hu/sap/opu/odata/sap/ZGW_UGYFELSZOLGALAT_LOGIN_SRV/Login"
        querystring = {"sap-client": "112", "sap-language": "HU"}

        payload = {"Username": self.username, "Password": self.password}
        headers = {
            "Accept": "application/json",
            "X-Requested-With": "X",
            "Content-Type": "application/json",
        }
        self.s.cookies.set("cookiePanelAccepted", "1")

        r = self.s.post(login_url, json=payload, headers=headers, params=querystring)
        r_dict = r.json()
        #print(r.text)
        self.authcode = r_dict["d"]["AuthCode"]

    def get_token(self):
        token_url = "https://eloszto.mvmemaszhalozat.hu/sap/opu/odata/sap/ZGW_OAUTH_SRV/GetToken"
        querystring = {
            "Code": f"'{self.authcode}'",
            "sap-client": "112",
            "sap-language": "HU",
        }
        self.headers = {
            "Accept": "application/json",
            "X-Requested-With": "X",
            "Content-Type": "application/json",
        }
        r = self.s.get(token_url, headers=self.headers, params=querystring)
        token_r_dict = r.json()
        self.token = token_r_dict["d"]["GetToken"]["TokenCode"]

        # print(r.status_code)

    def get_custumer_data(self):
        custumer_number_url = "https://eloszto.mvmemaszhalozat.hu/sap/opu/odata/sap/ZGW_UGYFELSZOLGALAT_SRV/Vevok"

        self.headers["Authorization"] = f"Bearer {self.token}"
        querystring = {"Funkcio": "OKOSMERO", "sap-client": "112", "sap-language": "HU"}
        r = self.s.get(custumer_number_url, headers=self.headers, params=querystring)
        self.custumer_number = r.json()["d"]["results"][0]["Id"]
        # print(r.status_code)

        custumer_id_url = f"https://eloszto.mvmemaszhalozat.hu/sap/opu/odata/sap/ZGW_UGYFELSZOLGALAT_SRV/Vevok('{self.custumer_number}')/Felhelyek"
        querystring = {"Funkcio": "OKOSMERO", "sap-client": "112", "sap-language": "HU"}
        r = self.s.get(custumer_id_url, headers=self.headers, params=querystring)
        self.customer_id = r.json()["d"]["results"][0]["Id"]
        # print(r.status_code)

    def get_smart_meter_data(self):
        custumer_meters_url = f"https://eloszto.mvmemaszhalozat.hu/sap/opu/odata/sap/ZGW_UGYFELSZOLGALAT_SRV/Felhelyek(Vevo='{self.custumer_number}',Id='{self.customer_id}')/Okosmero"
        querystring = {"sap-client": "112", "sap-language": "HU"}
        r = self.s.get(custumer_meters_url, headers=self.headers, params=querystring)
        r_list = r.json()["d"]["results"]
        self.meter_ids = r.json()["d"]["results"]
        self.smart_meter_links = []

        for link in r_list:
            if link["URL"].find("guid=&") == -1:
                split_url = link["URL"].split("?")
                query_string = split_url[1]

                query_string_list = query_string.split("&")

                query_dict = {"url": split_url[0], "meter_id": link["FogyMeroAzon"]}
                for item in query_string_list:
                    key, value = item.split("=")
                    query_dict[key] = value
                self.smart_meter_links.append(query_dict)

    def get_cookies_smart_meter_site(self):
        # TODO get around without using selenium

        self.smart_meter_url = f"{self.smart_meter_links[0]['url']}"
        # print(f"Smart meter link : {smart_meter_url}")
        self.sap_client = "100"
        self.guid = self.smart_meter_links[0]["guid"]

        self.s.transfer_session_cookies_to_driver(
            domain=f"{self.smart_meter_url}?guid={self.guid}&sap-client={self.sap_client}"
        )

        # print(f"{smart_meter_url}?guid={guid}&sap-client={sap_client}")
        response = self.s.driver.get(
            f"{self.smart_meter_url}?guid={self.guid}&sap-client={self.sap_client}"
        )
        # print(response.text)

        smart_meter_site_data_url = self.s.driver.current_url
        split_url = smart_meter_site_data_url.split("(")[1]
        self.sap_id = split_url.split(")")[0]

        self.s.transfer_driver_cookies_to_session()
        self.firefox_driver.quit()

    def smart_site_accept_cookes(self):
        first_page_url = f"{self.smart_meter_url}({self.sap_id})/oldal_1.htm"

        data = {
            "accept": "on",
            "OnInputProcessing(tovabb)": "",
        }

        #print(first_page_url)
        self.s.headers.update(
            {
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
                "Origin": "https://eloszto.mvmemaszhalozat.hu",
                "Upgrade-Insecure-Requests": "1",
                "Referer": f"https://eloszto.mvmemaszhalozat.hu/SMMU({self.sap_id})/oldal_1.htm",
            }
        )
        r = self.s.post(first_page_url, data=data)

    def get_ldc(self):
        second_page_url = f"{self.smart_meter_url}({self.sap_id})/Oldal_2.htm?OnInputProcessing(ToTerhGor1)"
        # print(second_page_url)
        r = self.s.get(second_page_url)
        # print(r.status_code)
        # print(r.text)

    def set_date_for_ldc(self, date_from, date_to):
        data = {
            "azonosito": self.smart_meter_links[0]["meter_id"],
            "tipus": "Fogyasztás",
            "idoszak_tol_mero": date_from,
            "idoszak_ig_mero": date_to,
            "mertekegyseg": "kWh",
            "profil": "KIS_LAKOSSAG",
            "OnInputProcessing(elkuld)": "Adatok frissítése",
        }
        r = self.s.post(f"{self.smart_meter_url}({self.sap_id})/Oldal_3.htm", data=data)
        # print(r.status_code)

    def download_ldc_data(self):
        smart_meter_page3_url = (
            f"{self.smart_meter_url}({self.sap_id})/showPDF.htm?type=1"
        )
        query_string = {"type": "1"}
        r = self.s.get(smart_meter_page3_url)
        # print(r.history)
        # print(r.status_code)
        r.encoding = "ISO-8859-1"
        data = r.text
        columns = [
            "serial_number",
            "id",
            "date",
            "time",
            "imported",
            "import_amount",
            "import_state",
            "import_state_desc",
            "exported",
            "exported_amount",
            "export_state",
            "export_state_desc",
            "saldo",
            "saldo_amount",
            "saldo_state",
            "saldo_state_desc",
        ]
        return pandas.read_csv(
            io.StringIO(data),
            sep=";",
            header=None,
            skiprows=1,
            names=columns,
        )

def clean_df(df):
    for col in df.columns:
        df[col] = df[col].map(lambda x: x.lstrip('="').rstrip('"'))

    df["datetime"] = df["date"] + " " + df["time"]
    df["datetime"] = pandas.to_datetime(df["datetime"])
    df = df.drop(columns=["date", "time"])
    df_colums = list(df.columns)
    items_to_keep = ["datetime", "imported", "saldo", "exported"]
    for col in items_to_keep:
        df_colums.remove(col)
    
    df = df.drop(columns=df_colums)

    for col in ["imported", "saldo", "exported"]:
        df[col] = df[col].str.replace(",", ".").str.replace(" ", "").astype(float)
    return df

def main():
    import dotenv

    env_path = "./env/"
    env_file = f"{env_path}config.env"
    dotenv.find_dotenv(env_file, raise_error_if_not_found=True)
    dotenv.load_dotenv(env_file)

    username = os.getenv("USERNAME")
    password = os.getenv("PASSWORD")

    smart_meter = Smart_meter(username, password)
    smart_meter.get_base_cookies()
    smart_meter.get_login_cookies()
    smart_meter.get_token()
    smart_meter.get_custumer_data()
    smart_meter.get_smart_meter_data()
    smart_meter.get_cookies_smart_meter_site()
    smart_meter.smart_site_accept_cookes()
    smart_meter.get_ldc()
    smart_meter.set_date_for_ldc("2023.02.08", "2023.02.08")
    df = smart_meter.download_ldc_data()
    
    print(clean_df(df))

if __name__ == "__main__":
    main()
