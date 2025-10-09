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

WHATSAPP_API_URL="https://graph.facebook.com/v22.0/720254477847692/messages"
WHATSAPP_TOKEN="EAFamCrwshVkBPUSZBfGDgqYsbVLoIZBlLMYaxU2Dnco4l6q4wYnGKfFd19ZBb2wbnR0bXcOaZCh1sbqhKF8HZBUzbvR26E0Tl3g1MmcakOaN8uZCF7r8Rzb1aTuqNDvZAvnqn0AFBo9yVUdJ9RZCbeCyBZCUinCZBpwDPCpGFgZAXTMCw3hboikezY1w2i5jHAk5HZAVrwZDZD"

def llm_api(data,id):
    payload={
        "token": "izDIEr98aBF24jJ6FB2Z4fle",
        "id": id,
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
        logger.info(f"✅ Webhook Raw Data: {data}")
    except json.JSONDecodeError:
        logger.error("❌ Invalid JSON format")
        return JsonResponse({'error': 'Invalid JSON format'}, status=400)

    processed_any = False  # track karega ki koi message process hua ya nahi

    for entry in data.get('entry', []):
        for messaging_event in entry.get('changes', []):
            message = messaging_event.get('value', {}).get('messages', [{}])[0]
            contacts = messaging_event.get('value', {}).get('contacts', [{}])[0]
            name = contacts.get('profile', {}).get('name', '')
            wa_id = contacts.get('wa_id', '')

            if not message:
                logger.warning("⚠️ No message found in change event")
                continue

            message_id = message.get("id")
            if not message_id:
                logger.warning("⚠️ No message_id found")
                continue

            logger.info(f"📩 New incoming message | id={message_id} | from={wa_id} | name={name}")

            cache_key = f"processed_{message_id}"
            if cache.get(cache_key):
                logger.info(f"⏩ Duplicate message skipped | id={message_id}")
                continue
            cache.set(cache_key, True, timeout=300)

            from_number = message.get('from')
            text = message.get('text', {}).get('body', '').strip().lower()
            interactive = message.get('interactive')

            if text:
                logger.info(f"💬 User sent text: {text}")

            if text in ['hi', 'hello', 'hey']:
                logger.info("👉 Greeting detected, sending menu")
                menu_option(from_number)
                processed_any = True

            elif interactive:
                logger.info("👉 Interactive payload detected")
                handle_interactive(from_number, interactive, name)
                processed_any = True

            elif text:
                logger.info("👉 Sending text to LLM API")
                output = llm_api(text, from_number)
                if output:
                    ans = output.get("answer")
                    send_text_message(from_number, f"{ans}")
                    logger.info(f"✅ LLM reply sent: {ans}")
                else:
                    send_text_message(from_number, "No response from LLM API.")
                    logger.warning("⚠️ LLM API returned no output")
                processed_any = True

    if processed_any:
        logger.info("🎯 Webhook processed successfully.")
        return JsonResponse({'status': 'success'}, status=200)
    else:
        logger.info("ℹ️ No valid action taken for this webhook.")
        return JsonResponse({'status': 'no action taken'}, status=200)

def handle_interactive(from_number, interactive,name):
    list_reply = interactive.get('list_reply')
    if list_reply:
        handle_list_message(from_number,list_reply)
        return JsonResponse({'status': 'success'}, status=200)
    button_id = interactive.get('button_reply', {}).get('id')

    logger.info(f"Button clicked: {button_id}")
    return JsonResponse({'status': 'no action taken'}, status=200)

def handle_list_message(from_number,list_reply):
    selected_id = list_reply.get('id')
    title=list_reply.get('title')
    if title:
        logger.info(f"title_____{title}__length--{len(title)}")
    if selected_id == "list_1":
        logger.info(f"title_____{title}__length--{len(title)}")
        output= llm_api(title,from_number)
        if output:
            print(f"output---{output}")
            ans=output.get("answer")
            send_text_message(from_number,f"{ans}")
        else:
            send_text_message(from_number,f"No response from LLM API.")
    
    elif selected_id == "list_2":
        logger.info(f"title_____{title}__length--{len(title)}")
        output= llm_api(title,from_number)
        if output:
            print(f"output---{output}")
            ans=output.get("answer")
            send_text_message(from_number,f"{ans}")
        else:
            send_text_message(from_number,f"No response from LLM API.")
            
    elif selected_id == "list_3":
        logger.info(f"title_____{title}__length--{len(title)}")
        output= llm_api(title,from_number)
        if output:
            print(f"output---{output}")
            ans=output.get("answer")
            send_text_message(from_number,f"{ans}")
        else:
            send_text_message(from_number,f"No response from LLM API.")                
            
        
    return JsonResponse({'status': 'no action taken'}, status=200)

def menu_option(to):
    # if cache.get(f"message_sent_{to}"):
    #     logger.info(f"Message already sent to {to}. Skipping...")
    #     return

    payload = {
        "messaging_product": "whatsapp", 
        "recipient_type": "individual",
        "to":to,
        "type": "interactive",
        "interactive": {
            "type": "list",
            
            "body": {
                "text": f"HI {to}\nPlease select an option from the menu:"
            },
            "action": {
                "button": "Main Menu",
                "sections": [
                    {
                        "title": "Menu",
                        "rows": [
                            {
                                "id": "list_1",
                                "title": "eAuctions",
                            },
                            {
                                "id": "list_2",
                                "title": "Licenses",
                            },
                            {
                                "id": "list_3",
                                "title": "Citizen Services",
                            }
                        ]
                    }
                ]
            }
        }
    }
    send_request_to_whatsapp(payload)


def send_text_message(to, message):
   
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": message}
    }
    send_request_to_whatsapp(payload)


def menu_option(to):
    cache_key = f"message_sent_menu_{to}"
    if cache.get(cache_key):
        logger.info(f"Menu already sent to {to}. Skipping...")
        return

    payload = {
        "messaging_product": "whatsapp", 
        "recipient_type": "individual",
        "to":to,
        "type": "interactive",
        "interactive": {
            "type": "list",
            "body": {
                "text": f"HI {to}\nPlease select an option from the menu:"
            },
            "action": {
                "button": "Main Menu",
                "sections": [
                    {
                        "title": "Menu",
                        "rows": [
                            {"id": "list_1","title": "eAuctions"},
                            {"id": "list_2","title": "Licenses"},
                            {"id": "list_3","title": "Citizen Services"}
                        ]
                    }
                ]
            }
        }
    }
    send_request_to_whatsapp(payload)
    cache.set(cache_key, True, timeout=30)

def send_request_to_whatsapp(payload):
    try:
        response = requests.post(WHATSAPP_API_URL, headers={
            'Authorization': f'Bearer {WHATSAPP_TOKEN}',
            'Content-Type': 'application/json'
        }, json=payload)
        logger.info(f"Message sent: {response.json()}")
    except requests.RequestException as e:
        logger.error(f"Message failed: {e}, Response: {e.response.text if e.response else 'No response'}")

