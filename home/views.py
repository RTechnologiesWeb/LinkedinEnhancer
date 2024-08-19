from django.shortcuts import render
from django.shortcuts import redirect
import requests
from scrapper.llm_bot import LLM_Bot
from django.contrib import messages
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
headers = {
    'ngrok-skip-browser-warning': 'true'
}


def scrape(request):
    if request.method == 'POST':
        url = request.POST.get('url')
        if not url.startswith('https'):
            messages.error(request, 'Please enter a valid URL starting with https://')
            return redirect('index')

        try:
            # Make a POST request to the Flask API
            response = requests.post(f"{SCRAPER_API_URL}/scrape", headers=headers, json={'url': url})
            response_data = response.json()

            if response_data['status'] == 'success':
                request.session['data'] = response_data['data']
            else:
                raise Exception(response_data.get('message', 'Unknown error'))

        except Exception as e:
            logger.info("Exception occurred while scraping: %s", e)
            messages.error(request, 'Could not scrape your profile. Please manually fill this form')
            return redirect('manualUpload')

        # Pass the screenshot URL directly to the template
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

        questions = llm_bot.getQuestions(about, headline)
        print("Questions agaye")
        print("Questions ye hain",questions)

        if questions is None:
            logger.error("Failed to retrieve questions from LLM_Bot.")
            messages.error(request, "Failed to retrieve questions. Please try again later.")
            return redirect('index')

        numOfQuestions = len(questions)
        logger.info(f"Retrieved {numOfQuestions} questions successfully.")

        return render(request, 'questions.html', {
            'questions': questions,
            'numOfQuestions': numOfQuestions,
            'about': about,
            'headline': headline
        })
    
    return redirect('index')

def preprocess_text(text):
    # Replace **text** with <strong>text</strong>
    return text.replace("**", "<strong>").replace("**", "</strong>", 1)

def getRecommendation(request):
    if request.method == 'POST':
        if 'data' not in request.session:
            return redirect('index')
        
        data = request.session['data']
        about = data['about']
        headline = data['headline']
        numOfQuestions = request.POST.get('numOfQuestions')
        qa = ''
        for i in range(1, int(numOfQuestions) + 1):
            question = request.POST.get(f'question_{i}')
            answer = request.POST.get(f'answer_{i}')
            qa += f"Question {i}: {question}\n"
            qa += f"Answer {i}: {answer}\n"

        suggestions = llm_bot.getNewAbout(about, headline, qa)
        extra_suggestions = llm_bot.get_gen_obs(json.dumps(data))

        suggestions = preprocess_text(suggestions)
        extra_suggestions = preprocess_text(extra_suggestions)
        return render(request, 'recommendation.html', {
            'suggestions': suggestions,
            'extra_suggestions': extra_suggestions
        })
    
    return redirect('index')

def manualUpload(request):
    return render(request,'manualUpload.html')
