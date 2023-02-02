import os
import time

from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.firefox import GeckoDriverManager
import dotenv
import requests
import  json



driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()))

env_path = ("./env/")
env_file = f"{env_path}config.env"
dotenv.find_dotenv(env_file, raise_error_if_not_found=True)
dotenv.load_dotenv(env_file)
user_agent = os.getenv("USER_AGENT")
headers = {"User-Agent":user_agent}
username = os.getenv("USERNAME")
password = os.getenv("PASSWORD")

def main():
        driver.get("https://eloszto.mvmemaszhalozat.hu")
        driver.maximize_window()
        time.sleep(10)
        cookie_accept = driver.find_element(By.XPATH, "/html/body/div[2]/div/div[1]/div/div/div/div[2]/button[1]")
        cookie_accept.click()
        time.sleep(4)
        login_button = driver.find_element(By.CSS_SELECTOR, value=".login-button")
        login_button.click()
        user_name_login = driver.find_element(By.CSS_SELECTOR, value="div.Input-wrapper:nth-child(1) > input:nth-child(2)").send_keys(username)
        time.sleep(4)
        user_password_login = driver.find_element(By.CSS_SELECTOR, value="div.Input-wrapper:nth-child(2) > input:nth-child(2)").send_keys(password)
        time.sleep(4)
        log_user_in_button = driver.find_element(By.CSS_SELECTOR, value="button.Button:nth-child(3)")
        log_user_in_button.click()
        time.sleep(2)
        menu_bar = driver.find_element(By.CSS_SELECTOR, value="li.dropdown:nth-child(6)")
        ActionChains(driver).move_to_element(menu_bar).click().perform()
        time.sleep(1)
        smart_meter_menu_bar = driver.find_element(By.CSS_SELECTOR, value="div.show > a:nth-child(5)")
        ActionChains(driver).move_to_element(smart_meter_menu_bar).click().perform()
        time.sleep(4)
        smart_meter_external_link = driver.find_element(By.CSS_SELECTOR, value=".-even > div:nth-child(2) > a:nth-child(1)")
        smart_meter_external_link.click()
        time.sleep(2)
        driver.switch_to.window(driver.window_handles[1])
        time.sleep(2)
        driver.switch_to.frame(0)
        smart_meter_site_cookie = driver.find_element(By.CSS_SELECTOR, value=".checkbox")
        smart_meter_site_cookie.click()
        time.sleep(1)
        smart_meter_site_cookie_click = driver.find_element(By.ID, value="tovabb_button")
        smart_meter_site_cookie_click.click()
        time.sleep(1)
        driver.find_element(By.CSS_SELECTOR, value=".terhelesi_button").click()
        


if __name__ == "__main__":
        main()
       
        

        
