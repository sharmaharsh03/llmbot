import json
from json import loads
import logging
import requests
import time
import re
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from django.core.cache import cache

WHATSAPP_API_URL="https://graph.facebook.com/v22.0/775062742347677/messages"
WHATSAPP_TOKEN="EAAStwtk8iaABPClKNkiXr3AGs5EeoVe23lOfu65ozyysUL7ZA16r2GaZAAkZAf3Aj07W4RSrZAKrZBDnGZB2lJl5osf4S8kpHZBClVRAEZBpxRzcN69Sv644qqBP2xZBt0whB6rsY88IcmN1CMQpeSDhlIzWAwQJGZBeS8tU4oyFGoOtxvZCOV0hQcZCsMPORuRWb1UWlwZDZD"

def llm_api(data):
    payload={
        "token": "izDIEr98aBF24jJ6FB2Z4fle",
        "id": "abc1231",
        "question": data
        }   
    url="https://us-central1-ejournal-7b5df.cloudfunctions.net/askAssistantWithId"

    headers = {
        "Content-Type": "application/json",
    }
    try:
        response = requests.post(url=url, json=payload, headers=headers)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        return {
            "status": False,
            "message": f"An error occurred: {str(e)}",
        }    

def handle_incoming_messages(request):
    try:
        data = json.loads(request.body)
        logger.info(f"Received data: {data}")
    except json.JSONDecodeError:
        logger.error("Invalid JSON format")
        return JsonResponse({'error': 'Invalid JSON format'}, status=400)

    for entry in data.get('entry', []):
        for messaging_event in entry.get('changes', []):
            message = messaging_event.get('value', {}).get('messages', [{}])[0]
            contacts = messaging_event.get('value', {}).get('contacts', [{}])[0]
            name = contacts.get('profile', {}).get('name', '')
            wa_id=contacts.get('wa_id', '')
            from_number = message.get('from')
            text = message.get('text', {}).get('body', '').strip().lower()
            interactive = message.get('interactive')
            if text:
                output= llm_api(text)
                if output:
                    print(f"output---{output}")
                    ans=output.get("answer")
                    send_text_message(from_number,f"{ans}")
                else:
                    send_text_message(from_number,f"please send Hi for starting chat")
                return JsonResponse({'status': 'success'}, status=200)
            
            elif interactive:
                handle_interactive(from_number, interactive,name)
                return JsonResponse({'status': 'success'}, status=200)
            else:
                send_text_message(from_number, "Please select an option from the menu or type 'DEL and AW' to start.")
    logger.info("No valid message found in the request.")
    return JsonResponse({'status': 'no action taken'}, status=200)
def handle_interactive(from_number, interactive,name):
    flow_responses=interactive.get('nfm_reply',{}).get('response_json')
    list_reply = interactive.get('list_reply')
    if list_reply:
        handle_list_message(from_number,list_reply)
        return JsonResponse({'status': 'success'}, status=200)
    button_id = interactive.get('button_reply', {}).get('id')
    logger.info(f"Button clicked: {button_id}")
    return JsonResponse({'status': 'no action taken'}, status=200)
    return JsonResponse({'status': 'no action taken'}, status=200)

def handle_list_message(from_number,list_reply):
    selected_id = list_reply.get('id')
    print(f"selectd_id_____{selected_id}") 
    return JsonResponse({'status': 'no action taken'}, status=200)


def send_text_message(to, message):
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": message}
    }
    send_request_to_whatsapp(payload)

def send_request_to_whatsapp(payload):
    try:
        response = requests.post(WHATSAPP_API_URL, headers={
            'Authorization': f'Bearer {WHATSAPP_TOKEN}',
            'Content-Type': 'application/json'
        }, json=payload)
        logger.info(f"Message sent: {response.json()}")
    except requests.RequestException as e:
        logger.error(f"Message failed: {e}, Response: {e.response.text if e.response else 'No response'}")
