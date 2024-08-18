from django.shortcuts import render
from django.shortcuts import redirect
import requests
from scrapper.scrapper import ScrapeException, Scrapper
from scrapper.llm_bot import LLM_Bot
from django.contrib import messages
import json
import logging
logger = logging.getLogger(__name__)


scrapper = Scrapper()
llm_bot = LLM_Bot()

def index(request):
    
    return render(request, 'index.html')

SCRAPER_API_URL = 'https://9e57-124-29-227-46.ngrok-free.app/scrape'
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
            # Make a request to the Flask API
            response = requests.post(SCRAPER_API_URL, headers=headers, json={'url': url})
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
    if request.method == 'POST':
        if 'data' not in request.session:
            return redirect('index')

        data = request.session['data']
        about = data['about']
        headline = data['headline']

        questions = llm_bot.getQuestions(about, headline)
        numOfQuestions = len(questions)
        
        return render(request, 'questions.html', {
            'questions': questions,
            'numOfQuestions': numOfQuestions,
            'about': about,
            'headline': headline
        })
    
    return redirect('index')

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

        return render(request, 'recommendation.html', {
            'suggestions': suggestions,
            'extra_suggestions': extra_suggestions
        })
    
    return redirect('index')

def manualUpload(request):
    return render(request,'manualUpload.html')
