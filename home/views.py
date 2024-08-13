from django.shortcuts import render
from django.shortcuts import redirect
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


# def scrape(request):
#     if request.method == 'POST':
#         url = request.POST.get('url')
#         if not url.startswith('https'):
#             messages.error(request, 'Please enter a valid URL starting with https://')
#             return redirect ('index')
#         print(url)
#         try:
#             data,screenshot = scrapper.scrape(rf"{url}")
#             request.session['data'] = data
#             print(request.session['data'],type(request.session['data']))
#         except Exception as e:
#             print("exception occured")
#             print(e)
#             messages.error(request, 'Could not scrape your profile please manually fill this form')
            
#             return redirect ('manualUpload')


#         return render(request, 'scrape.html',{'url':url,'screenshot':screenshot})
#     return redirect('index')


def scrape(request):
    if request.method == 'POST':
        url = request.POST.get('url')
        if not url.startswith('https'):
            messages.error(request, 'Please enter a valid URL starting with https://')
            return redirect('index')

        scrapper = Scrapper()
        try:
            data, screenshot = scrapper.scrape(url)
            request.session['data'] = data
        except ScrapeException as e:
            logger.info("exception occurred while scraping %s", e)
            messages.error(request, 'Could not scrape your profile. Please manually fill this form')
            return redirect('manualUpload')

        return render(request, 'scrape.html', {'url': url, 'screenshot': screenshot})
    return redirect('index')



def getQuestions(request):
    if request.method == 'POST':
        if 'data' not  in request.session:
            return redirect('index')

        data = request.session['data']
        about = data['about']
        headline = data['headline']

        questions = llm_bot.getQuestions(about,headline)
        # questions = questions[:-1]
        numOfQuestions = len(questions)
        return render(request, 'questions.html',{'questions':questions,
                                                 'numOfQuestions':numOfQuestions,
                                                 "about":about,
                                                 "headline":headline})
    return redirect('index')


def getRecommendation(request):
    if request.method == 'POST':
        if 'data' not  in request.session:
            return redirect('index')
        
        data = request.session['data']
        about = data['about']
        headline = data['headline']
        numOfQuestions = request.POST.get('numOfQuestions')
        qa = ''
        for i in range(1,int(numOfQuestions)+1):
            question = request.POST.get(f'question_{i}')
            answer = request.POST.get(f'answer_{i}')
            qa += f"Question {i}: {question}\n"
            qa += f"Answer {i}: {answer}\n"
                

        suggestions = llm_bot.getNewAbout(about,headline,qa)


        extra_suggestions = llm_bot.get_gen_obs(json.dumps(data))


        return render(request, 'recommendation.html',{'suggestions':suggestions,'extra_suggestions':extra_suggestions})


    return redirect('index')


def manualUpload(request):
    return render(request,'manualUpload.html')
