from fastapi import FastAPI, Request, Response, Query, HTTPException, APIRouter
from fastapi.responses import PlainTextResponse
import httpx 

import os 

app = FastAPI()

ACCESS_TOKEN = os.environ.get("WHATSAPP_ACCESS_TOKEN")
PHONE_NUMBER_ID = os.environ.get("PHONE_NUMBER_ID")
WHATSAPP_HOOK_TOKEN = os.environ.get("WHATSAPP_HOOK_TOKEN")
WHATSAPP_API_URL = f"https://graph.facebook.com/v18.0/{PHONE_NUMBER_ID}/messages"
# "https://graph.facebook.com/v18.0/739443625915932/messages"

headers = {
    "Authorization": f"Bearer {ACCESS_TOKEN}",
    "Content-Type": "application/json"
}
    
def scripted_response(paciente_text):
    conversation = [
        # SPANISH
        ("Hola, me siento muy mal", "Hola 👋, lamento escuchar eso. Estoy aquí para ayudarte a encontrar un centro médico cercano. ¿Podrías contarme qué síntomas tienes?"),
        ("Tengo un dolor fuerte en el pecho y me cuesta respirar", "Entiendo. Gracias por decírmelo. Estos síntomas pueden ser graves, así que es importante actuar rápido. ¿Me puedes indicar tu ubicación actual o dónde te encuentras en Guatemala?"),
        ("Estoy en la zona 10 de la Ciudad de Guatemala, cerca del hotel Camino Real", "Gracias por la información. Por tus síntomas y tu ubicación, te recomiendo acudir de inmediato al Centro Médico, que cuenta con un área de emergencias equipada para atender problemas cardíacos.\n📍 Dirección: 6a. Avenida 3-47, zona 10, Ciudad de Guatemala.\n📞 Teléfono de emergencias: +502 2319-4600.\n Ubicación: https://share.google/VgSoqYSYNbmhLOUvE"),
        ("UBICACION", "Gracias por la información. Por tus síntomas y tu ubicación, te recomiendo acudir de inmediato al Centro Médico, que cuenta con un área de emergencias equipada para atender problemas cardíacos.\n📍 Dirección: 6a. Avenida 3-47, zona 10, Ciudad de Guatemala.\n📞 Teléfono de emergencias: +502 2319-4600.\n Ubicación: https://share.google/VgSoqYSYNbmhLOUvE"),
        ("Gracias, voy para allá", "De nada, espero que te recuperes pronto 🙏. Si necesitas más ayuda en tu estancia en Guatemala, no dudes en escribirme.")
        # English
        ("Hi, i'm feeling sick", "Hello 👋, I’m sorry to hear that. I’m here to help you find a nearby medical center. Could you tell me what symptoms you’re experiencing?"),
        ("I have severe stomach pain and I’m feeling dizzy", "I understand, thank you for letting me know. Those symptoms can be serious, so it’s important to act quickly. Could you share your current location or where you are in Guatemala?"),
        ("I’m in Guatemala City, near the Hyatt Hotel", "Thanks for the information. Based on your symptoms and location, I recommend you go immediately to Centro Médico, which has a 24/7 emergency department ready to handle urgent cases.\n📍 Address:  6a. Avenida 3-47, zona 10, Ciudad de Guatemala.\n📞 Emergency phone: +502 2319-4600.\n🌐 Map: https://share.google/VgSoqYSYNbmhLOUvE"),
        ("Thank you, I’m heading there now", "You’re welcome, I hope you feel better soon 🙏. If you need more help while you’re in Guatemala, don’t hesitate to message me.")
    ]
    
    for paciente, bot in conversation:
        if paciente_text == paciente:
            return bot
    return "Lo siento, no tengo una respuesta para eso."


@app.get("/")
def home(): 
    return "App is live"

@app.get("/webhook")
async def verify_webhook(request: Request):
    params = dict(request.query_params)
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    if mode and token:
        print(f"Comparing {WHATSAPP_HOOK_TOKEN} with {token}")
        if mode == "subscribe" and token == WHATSAPP_HOOK_TOKEN:
            return PlainTextResponse(content=challenge, status_code=200)
        else:
            raise HTTPException(status_code=403, detail="Verification failed")
    else:
        raise HTTPException(status_code=400, detail="Missing parameters")

@app.post("/webhook")
async def callback(request: Request): 
    # print("callback is beign called")
    data = await request.json()
    # print("Incoming data:", data)

    try:
        entry = data["entry"][0]
        changes = entry["changes"][0]
        value = changes["value"]
        messages = value.get("messages")

        if messages:
            message = messages[0]
            sender_id = message["from"]
            message_type = message.get("type", "text")

            text = ""
            location_data = None

            if message_type == "text":
                # Get the message text
                text = message.get("text", {}).get("body", "")
                response = scripted_response(text)
                
                try:
                    payload = {
                        "messaging_product": "whatsapp",
                        "to": sender_id,
                        "type": "text",
                        "text": {
                            "body": response
                        }
                    }
            
                    async with httpx.AsyncClient() as client:
                        resp = await client.post(WHATSAPP_API_URL, headers=headers, json=payload)
                except:
                    pass
            
            if message_type == "location":
                # Get the message text
                text = message.get("text", {}).get("body", "")
                response = scripted_response("UBICACION")
                
                try:
                    payload = {
                        "messaging_product": "whatsapp",
                        "to": sender_id,
                        "type": "text",
                        "text": {
                            "body": response
                        }
                    }
            
                    async with httpx.AsyncClient() as client:
                        resp = await client.post(WHATSAPP_API_URL, headers=headers, json=payload)
                except:
                    pass

    except Exception as e:
        print("Error:", e)
        

    return {"status": "received"}



