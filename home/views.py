from pathlib import Path
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
import environ


env = environ.Env()
environ.Env.read_env() 

llm_bot = LLM_Bot()

def index(request):
    
    return render(request, 'index.html')

# SCRAPER_API_URL = env('SCRAPER_API_URL')
SCRAPER_API_URL = os.getenv('SCRAPER_API_URL', 'default_value')

print("SCRAPER_API_URL", SCRAPER_API_URL)

headers = {
    'ngrok-skip-browser-warning': 'true'
}


from django.http import JsonResponse

def scrape(request):
    if request.method == 'POST':
        url = request.POST.get('url')
        if not url.startswith('https'):
            return JsonResponse({'status': 'error', 'message': 'Please enter a valid URL starting with https://'})

        try:
            headers = {
                'ngrok-skip-browser-warning': 'true'
            }

            SCRAPER_API_URL = env('SCRAPER_API_URL')
            SCRAPER_API_URL = os.getenv('SCRAPER_API_URL', 'default_value')

            print("URL: ", SCRAPER_API_URL)

            response = requests.post(f"{SCRAPER_API_URL}/scrape", headers=headers, json={'url': url})
            if response.status_code == 302:
                print("Redirect detected, location:", response.headers.get('Location'))
            print("URL_Response: ", response.json())

            response_data = response.json()
            print("URL_Response: ", response_data)

            if response_data['status'] == 'success':
                data = response_data['data']
                
                # Store scraped data in session
                request.session['scraped_data'] = data

                # Return JSON response for AJAX request
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return JsonResponse({'status': 'success'})

                # For normal form submissions, render the recommendation page
                return render(request, 'recommendation.html', data)
            else:
                return JsonResponse({'status': 'error', 'message': response_data.get('message', 'Unknown error')})

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return JsonResponse({'status': 'error', 'message': 'Invalid request'})



# def scrape(request):
#     if request.method == 'POST':
#         url = request.POST.get('url')
#         if not url.startswith('https'):
#             messages.error(request, 'Please enter a valid URL starting with https://')
#             return redirect('index')

#         try:
#             headers = {
#                 'ngrok-skip-browser-warning': 'true'
#             }

#             SCRAPER_API_URL = env('SCRAPER_API_URL')
#             SCRAPER_API_URL = os.getenv('SCRAPER_API_URL', 'default_value')

#             print("URL: ", SCRAPER_API_URL)

#             response = requests.post(f"{SCRAPER_API_URL}/scrape", headers=headers, json={'url': url})
#             if response.status_code == 302:
#                 print("Redirect detected, location:", response.headers.get('Location'))
#             print("URL_Response: ", response.json())

#             response_data = response.json()
#             print("URL_Response: ", response_data)

#             if response_data['status'] == 'success':
#                 data = response_data['data']
                
#                 # Extract profile details directly
#                 about = data['about']
#                 headline = data['headline']
#                 experience = data['experience']
#                 projects = data['projects']

#                 # Fetch the new recommendations from the LLM bot
#                 newAbout = llm_bot.getNewAbout(about, "")
#                 newHeadline = llm_bot.getNewHeadline(headline, "")
#                 newExperience = llm_bot.getNewExperience(experience)
#                 newProjects = llm_bot.getNewProjects(projects, experience)

#                 # Render the recommendations page
#                 return render(request, 'recommendation.html', {
#                     'newAbout': newAbout,
#                     'about': about,
#                     'newHeadline': newHeadline,
#                     'headline': headline,
#                     'newExperience': newExperience,
#                     'experience': experience,
#                     'newProjects': newProjects,
#                     'projects': projects
#                 })
#             else:
#                 raise Exception(response_data.get('message', 'Unknown error'))

#         except Exception as e:
#             messages.error(request, f'{e}. Please manually fill this form')
#             return redirect('manualUpload')
    
#     return redirect('index')

def getQuestions(request):
    if request.method == 'POST':
        if 'data' not in request.session:
            return JsonResponse({'error': 'Session expired. Please try again.'})

        data = request.session['data']
        about = data['about']
        headline = data['headline']

        questions_about = llm_bot.getAboutQuestions(about)
        questions_headline = llm_bot.getHeadlineQuestions(headline=headline, about=about)

        return JsonResponse({
            'questions': questions_about + questions_headline
        })


def preprocess_text(text):
    # Replace **text** with <strong>text</strong>
    return markdown.markdown(text)

# def getRecommendation(request):
#     if request.method == 'POST':
#         if 'data' not in request.session:
#             return redirect('index')
        
#         data = request.session['data']
#         about = data['about']
#         headline = data['headline']
#         experience  = data['experience']
#         projects = data['projects']
#         numOfAboutQuestions = request.POST.get('numOfAboutQuestions')
#         numOfHeadlineQuestions = request.POST.get('numOfHeadlineQuestions')
#         about_qa = ''
#         for i in range(1, int(numOfAboutQuestions) + 1):
#             question = request.POST.get(f'question_about_{i}')
#             answer = request.POST.get(f'answer_about_{i}')
#             about_qa += f"Question {i}: {question}\n"
#             about_qa += f"Answer {i}: {answer}\n"

#         newAbout = llm_bot.getNewAbout(about,  about_qa)
#         headline_qa = ''
#         for i in range(1, int(numOfHeadlineQuestions) + 1):
#             question = request.POST.get(f'question_headline_{i}')
#             answer = request.POST.get(f'answer_headline_{i}')
#             headline_qa += f"Question {i}: {question}\n"
#             headline_qa += f"Answer {i}: {answer}\n"

#         newHeadline = llm_bot.getNewHeadline(headline, headline_qa)


#         newExperience = llm_bot.getNewExperience(experience)
#         newProjects = llm_bot.getNewProjects(projects,experience)





#         return render(request, 'recommendation.html', {
#             'newAbout': newAbout,
#             'about': about,
#             'newHeadline': newHeadline,
#             'headline': headline,
#             "newExperience":newExperience,
#             'experience':experience,
#             "newProjects":newProjects,
#             'projects':projects

#         })
    
#     return redirect('index')


# def getRecommendation(request):
#     # Check if data is available in the session
#     scraped_data = request.session.get('scraped_data')
#     print("Scrapped data is available in the session: "+ scraped_data.get('about'))
#     if not scraped_data:
#         return redirect('index')  # Redirect back to the index if no data is available in the session

#     # Extract the relevant data from the session
#     about = scraped_data.get('about')
#     headline = scraped_data.get('headline')
#     experience = scraped_data.get('experience')
#     projects = scraped_data.get('projects')

#     # Generate recommendations (or use as is)
#     newAbout = llm_bot.getNewAbout(about, "")
#     newHeadline = llm_bot.getNewHeadline(headline, "")
#     newExperience = llm_bot.getNewExperience(experience)
#     newProjects = llm_bot.getNewProjects(projects, experience)

#     # Render the recommendations page with the data
#     return render(request, 'recommendation.html', {
#         'newAbout': newAbout,
#         'about': about,
#         'newHeadline': newHeadline,
#         'headline': headline,
#         'newExperience': newExperience,
#         'experience': experience,
#         'newProjects': newProjects,
#         'projects': projects
#     })

def getRecommendation(request):
    # Check if data is available in the session
    scraped_data = request.session.get('scraped_data')
    
    if not scraped_data:
        return redirect('index')  # Redirect back to the index if no data is available in the session
    
    # Safe print statement, check if about exists
    about = scraped_data.get('about', '')
    print(f"Scraped data is available in the session: {about}")
    
    # Extract the relevant data from the session
    headline = scraped_data.get('headline', '')
    experience = scraped_data.get('experience', '')
    projects = scraped_data.get('projects', '')

    # Generate recommendations (or use as is)
    newAbout = llm_bot.getNewAbout(about, "")
    newHeadline = llm_bot.getNewHeadline(headline, "")
    newExperience = llm_bot.getNewExperience(experience)
    newProjects = llm_bot.getNewProjects(projects, experience)

    # Render the recommendations page with the data
    return render(request, 'recommendation.html', {
        'newAbout': newAbout,
        'about': about,
        'newHeadline': newHeadline,
        'headline': headline,
        'newExperience': newExperience,
        'experience': experience,
        'newProjects': newProjects,
        'projects': projects
    })


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
