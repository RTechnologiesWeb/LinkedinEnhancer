from typing import Any
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
from langchain.chains import LLMChain
from langchain_core.prompts import PromptTemplate
from langchain_mistralai.chat_models import ChatMistralAI
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import os
from io import BytesIO
import base64


MISTRAL_API_KEY = 'c2pXa02xhfTrY6nZfjmOdzHjj4wKv7Mv'
class ScrapeException(Exception):
    """Custom exception for scrape errors"""
    pass


class Scrapper:
    def __init__(self):
        self.chrome_options = Options()
        self.chrome_options.add_argument("--start-maximized")
        # chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
        self.chrome_options.add_argument('--log-level 3') 
        self.chrome_options.add_argument("--headless")
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        self.chrome_options.add_argument("--disable-gpu")

    def scrape(self,url) -> str:
        """Tries to scrape linkedin profile and returns about and headline throws if unsuccessful"""
        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(options=self.chrome_options) 

        print("here")
        print(url)
        driver.get(url)
        print("sleeping")
        time.sleep(2)
        print("sleep over")
        tries = 0
        while driver.current_url != url:
            if tries > 10:
                raise ScrapeException("Could not Scrape page")
            
            print("redirected to signup page")
            print(driver.current_url)
            driver.get(url)
            time.sleep(1)
            tries += 1
            
        time.sleep(1)
        try:
            driver.find_element(by=By.CSS_SELECTOR,value='#base-contextual-sign-in-modal > div > section > button').click()
            print("clicked")
        except:
            print("could not find button ")
            try:
                driver.find_element(by=By.CSS_SELECTOR,value='#public_profile_contextual-sign-in > div > section > button').click()
                print("clicked button 2")

            except:
                print("could not find button")

        time.sleep(1)
        # with open('test.html', 'w', encoding='utf-8') as file:
        #     file.write(driver.page_source)
        print("writting page source for inspection")
        about = driver.find_element(by=By.CSS_SELECTOR,value='section.core-section-container:nth-child(2) > div:nth-child(2) > p:nth-child(1)').text


        headline = driver.find_element(by=By.CSS_SELECTOR,value ='.top-card-layout__headline').text



        projectDetailsLi = driver.find_elements(by=By.CSS_SELECTOR,value ='.personal-project')



        projDetails = ''
        for project in projectDetailsLi:
            projDetails += project.text.strip() + '\n'




        experienceLi = driver.find_elements(by=By.CSS_SELECTOR,value ='.experience-item')
        experience = ''
        for exp in experienceLi:
            experience += exp.text.strip() + '\n'



        certificationLi = driver.find_elements(by=By.CSS_SELECTOR,value ='.experience-item')
        certificationDetails = ''
        for cert in certificationLi:
            certificationDetails += cert.text.strip() + '\n'

        


    


        educationDetailsLis = driver.find_elements(by=By.CSS_SELECTOR,value ='.education__list-item')
        eduDetails = ''
        for edu in educationDetailsLis:
            eduDetails += edu.text.strip() + '\n'




        screenshot = driver.get_screenshot_as_png()
        screenshot = base64.b64encode(screenshot).decode('utf-8')
        driver.quit()  
        return{
            'about':about,
            'headline':headline,
            'projects':projDetails,
            'experience':experience,
            'certifications':certificationDetails,
            'education':eduDetails
        } , screenshot
        