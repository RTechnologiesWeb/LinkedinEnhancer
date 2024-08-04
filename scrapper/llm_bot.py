from typing import Any
from openai import RateLimitError
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
from langchain.chains import LLMChain
from langchain_core.prompts import PromptTemplate
from langchain_openai.chat_models import ChatOpenAI
from selenium.webdriver.chrome.options import Options
import os

from langchain_core.prompts import ChatPromptTemplate

from langchain_core.messages import SystemMessage
from langchain_core.prompts import HumanMessagePromptTemplate
import os

from dotenv import load_dotenv
load_dotenv()

# API_KEY = os.environ.get('OPENAI_API_KEY')
API_KEY = os.getenv('OPENAI_API_KEY')

class LLM_Bot:
    def __init__(self) -> None:

    


        self.first_prompt = ChatPromptTemplate.from_messages(
            [
                SystemMessage(
                    content=(
                        "You are Linkedin profile optimizer. "
                         "The user will provide about and headline of their profile. "
                          "your job is to generate target questions to improve it. "
                          "Place all the questions together enclosed in triple backticks ```Questions``` Like this. "
                    )
                ),
                HumanMessagePromptTemplate.from_template("Headline: {headline} \n About: {about}"),
            ]
        )
        
        self.general_obs_prompt = ChatPromptTemplate.from_messages(
                        [
                SystemMessage(
                    content=(
                          "You are Linkedin profile optimizer. "
                         "Using the following linkedin profile guide the use how to optimize it. "
                    )
                ),
                HumanMessagePromptTemplate.from_template("Profile: {profile} "),
            ]
        )
        self.second_prompt = ChatPromptTemplate.from_messages(
            [
                SystemMessage(
                    content=(
                        "You are Linkedin profile optimizer. "
                         "You asked the user a bunch of questions to optimize their headline and about section. "
                         "The user is going to provide answers to those questions along with the about and headline. "
                        "Your job is to generate a new about and headline section based on the answers provided. "
                    )
                ),
                HumanMessagePromptTemplate.from_template("Headline: {headline} \n About: {about} \n Questions and answers: {qa}"),

            ]
        )
        self.llm = ChatOpenAI(api_key=API_KEY)
        self.chain_first = LLMChain(llm=self.llm , prompt=self.first_prompt)
        self.chain_general_obs = LLMChain(llm =self.llm, prompt=self.general_obs_prompt)
        self.second_chain = LLMChain(llm =self.llm, prompt=self.second_prompt)

    # def getQuestions(self,about:str,headline:str) -> Any:
    #     while 1:
    #         res = self.chain_first.invoke({'about': about,'headline': headline})
    #         print(res['text'])
    #         try:     
    #             question_raw = (res['text'].split('```') [1] )

    #             questions_split = question_raw.split('\n')

    #             questions_split = [q for q in questions_split if len(q.split(' ')) > 3 ]
    #             if len(questions_split) <1:
    #                 continue
    #             return questions_split    
    #         except:
    #             continue

    def getQuestions(self, about: str, headline: str) -> Any:
        while True:
            try:
                res = self.chain_first.invoke({'about': about, 'headline': headline})
                print(res['text'])
                question_raw = (res['text'].split('```')[1])
                questions_split = question_raw.split('\n')
                questions_split = [q for q in questions_split if len(q.split(' ')) > 3]
                if len(questions_split) < 1:
                    continue
                return questions_split
            except RateLimitError as e:
                print("Rate limit exceeded. Please try again later.")
                # Implement logic to handle the rate limit, e.g., retry after some time
                time.sleep(60)  # Sleep for 60 seconds before retrying
            except Exception as e:
                print(f"An error occurred: {e}")
                continue

    # def get_gen_obs(self,data:str) -> str:

    #     res = self.chain_general_obs.invoke({'profile': data})
    #     return res['text']

    def get_gen_obs(self, data: str) -> str:
        try:
            res = self.chain_general_obs.invoke({'profile': data})
            return res['text']
        except RateLimitError as e:
            print("Rate limit exceeded. Please try again later.")
            # Implement logic to handle the rate limit
            time.sleep(60)  # Sleep for 60 seconds before retrying
        except Exception as e:
            print(f"An error occurred: {e}")
            return ""
        
    
    def getNewAbout(self, about: str, headline: str, qa: str) -> str:
        try:
            res = self.second_chain.invoke({'about': about, 'headline': headline, 'qa': qa})
            return res['text']
        except RateLimitError as e:
            print("Rate limit exceeded. Please try again later.")
            # Implement logic to handle the rate limit
            time.sleep(60)  # Sleep for 60 seconds before retrying
        except Exception as e:
            print(f"An error occurred: {e}")
            return ""
