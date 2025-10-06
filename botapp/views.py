from django.shortcuts import render
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .handle_incoming import handle_incoming_messages
VERIFY_TOKEN = 'HAPPYBOY'

def home(request):
    return HttpResponse("Hello, this is the home page of the bot application.")

@csrf_exempt
def webhook(request):
    if request.method == 'GET':
        return handle_verification(request)  
    elif request.method == 'POST':
        return handle_incoming_messages(request) 

    return JsonResponse({'error': 'Method not allowed'}, status=405)

def handle_verification(request): 
    mode = request.GET.get('hub.mode')
    token = request.GET.get('hub.verify_token')
    challenge = request.GET.get('hub.challenge')

    if mode == 'subscribe' and token == VERIFY_TOKEN:
        return HttpResponse(challenge, status=200)
 
    return JsonResponse({'error': 'Verification failed'}, status=403)


