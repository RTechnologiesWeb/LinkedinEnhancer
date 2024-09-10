from django.shortcuts import render
from django.shortcuts import redirect
import markdown
import requests
from gpt_llm.llm_bot import LLM_Bot
from django.contrib import messages
from django.http import JsonResponse
from django.http import request
import json
import logging
logger = logging.getLogger(__name__)
import os
from dotenv import load_dotenv
load_dotenv()

llm_bot = LLM_Bot()

def index(request):
    
    return render(request, 'index.html')

SCRAPER_API_URL = os.getenv('SCRAPER_API_URL')
print("SCRAPER_API_URL", SCRAPER_API_URL)



def scrape(request):
    if request.method == 'POST':
        url = request.POST.get('url')
        if not url.startswith('https'):
            messages.error(request, 'Please enter a valid URL starting with https://')
            return redirect('index')

        try:
            headers = {
                    'ngrok-skip-browser-warning': 'true'
                }
            # Make a POST request to the Flask API
            print(url)
            response = requests.post(f"{SCRAPER_API_URL}", headers=headers, json={'url': url})
            print(response)
            response_data = response.json()
            print(response_data)
            if response_data['status'] == 'success':
                request.session['data'] = response_data['data']
                print("Data",response_data['data'])
            else:
                raise Exception(response_data.get('message', 'Unknown error'))

        except Exception as e:
            logger.info("Exception occurred while scraping: %s", e)
            messages.error(request, f'{e}. Please manually fill this form')
            return redirect('manualUpload')

        # Pass the screenshot URL directly to the template
        print("HERE")
        return render(request, 'scrape.html', {'url': url, 'screenshot': response_data['data']['screenshot_url']})
    
    return redirect('index')

def getQuestions(request):
    logger.info("getQuestions view called")
    if request.method == 'POST':
        if 'data' not in request.session:
            messages.error(request, "Session expired. Please try again.")
            return redirect('index')

        data = request.session['data']
        about = data['about']
        headline = data['headline']

        questions_about = llm_bot.getAboutQuestions(about)
        questions_headline = llm_bot.getHeadlineQuestions(headline=headline,about=about)
        
        print("Questions agaye")
        print("Questions ye hain",questions_about,questions_headline)

        if questions_about is None or  questions_headline is None:
            logger.error("Failed to retrieve questions from LLM_Bot.")
            messages.error(request, "Failed to retrieve questions. Please try again later.")
            return redirect('index')

        numOfAboutQuestions = len(questions_about)
        numOfHeadlineQuestions = len(questions_headline)
        logger.info(f"Retrieved {numOfAboutQuestions} about questions successfully and {numOfHeadlineQuestions} headline questions successfully.")

        return render(request, 'questions.html', {
            'questions_about': questions_about,
            'questions_headline': questions_headline,
            'numOfAboutQuestions': numOfAboutQuestions,
            'numOfHeadlineQuestions': numOfHeadlineQuestions,
            'about': about,
            'headline': headline
        })
    
    return redirect('index')

def preprocess_text(text):
    # Replace **text** with <strong>text</strong>
    return markdown.markdown(text)

def getRecommendation(request):
    if request.method == 'POST':
        if 'data' not in request.session:
            return redirect('index')
        
        data = request.session['data']
        about = data['about']
        headline = data['headline']
        experience  = data['experience']
        projects = data['projects']
        numOfAboutQuestions = request.POST.get('numOfAboutQuestions')
        numOfHeadlineQuestions = request.POST.get('numOfHeadlineQuestions')
        about_qa = ''
        for i in range(1, int(numOfAboutQuestions) + 1):
            question = request.POST.get(f'question_about_{i}')
            answer = request.POST.get(f'answer_about_{i}')
            about_qa += f"Question {i}: {question}\n"
            about_qa += f"Answer {i}: {answer}\n"

        newAbout = llm_bot.getNewAbout(about,  about_qa)
        headline_qa = ''
        for i in range(1, int(numOfHeadlineQuestions) + 1):
            question = request.POST.get(f'question_headline_{i}')
            answer = request.POST.get(f'answer_headline_{i}')
            headline_qa += f"Question {i}: {question}\n"
            headline_qa += f"Answer {i}: {answer}\n"

        newHeadline = llm_bot.getNewHeadline(headline, headline_qa)


        newExperience = llm_bot.getNewExperience(experience)
        newProjects = llm_bot.getNewProjects(projects,experience)





        return render(request, 'recommendation.html', {
            'newAbout': newAbout,
            'about': about,
            'newHeadline': newHeadline,
            'headline': headline,
            "newExperience":newExperience,
            'experience':experience,
            "newProjects":newProjects,
            'projects':projects

        })
    
    return redirect('index')




def manualUpload(request):
    return render(request,'manualUpload.html')


def regenerate(request):
    types = {
        "about": llm_bot.regenAbout,
        "headline": llm_bot.regenHeadline,
        "experience": llm_bot.regenExperience,
        "projects": llm_bot.regenProjects
    }
    if request.method == 'POST':
        data = json.loads(request.body)
        print(data)
        
        function = types[data['section']]
        res = function(data['text'])
        res = types[data['section']](data['text'])
        
        return  JsonResponse({"res":res})