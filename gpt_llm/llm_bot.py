from typing import Any
from openai import RateLimitError
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
from langchain.chains import LLMChain
from langchain_core.prompts import PromptTemplate
from langchain_openai.chat_models import ChatOpenAI


import os

from langchain_core.prompts import ChatPromptTemplate

from langchain_core.messages import SystemMessage
from langchain_core.prompts import HumanMessagePromptTemplate
import os

from dotenv import load_dotenv
load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
print("API_KEY: ", OPENAI_API_KEY)
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
        self.llm = ChatOpenAI(api_key=OPENAI_API_KEY)
        self.chain_first = LLMChain(llm=self.llm , prompt=self.first_prompt)
        self.chain_general_obs = LLMChain(llm =self.llm, prompt=self.general_obs_prompt)
        self.second_chain = LLMChain(llm =self.llm, prompt=self.second_prompt)



    def getQuestions(self, about: str, headline: str) -> Any:
        retry_count = 0
        max_retries = 1

        while retry_count < max_retries:
            try:
                res = self.chain_first.invoke({'about': about, 'headline': headline})
                print("Full response:", res)

                # Directly target the 'text' key and remove the first line with "```Questions```"
                full_text = res['text']
                print("Full text received:", full_text)

                # Split the text into lines and remove the first one
                lines = full_text.split('\n')[1:]
                print("Lines after splitting:", lines)

                # Filter out empty lines and ensure there's meaningful content
                questions_split = [line.strip() for line in lines if len(line.strip()) > 0]
                print("Filtered questions:", questions_split)

                if len(questions_split) > 0:
                    return questions_split
                break  # If questions are found, exit loop
            except RateLimitError:
                print("Rate limit exceeded. Retrying after 60 seconds.")
                time.sleep(60)  # Sleep for 60 seconds before retrying
            except Exception as e:
                print(f"An error occurred: {e}")
                break  # Break out of the loop if there's an unexpected error
            
            retry_count += 1

        return None


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
