import os
from fastapi import FastAPI, Request
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Gather
import requests
from dotenv import load_dotenv

load_dotenv()

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
TO_PHONE_NUMBER = os.getenv("TO_PHONE_NUMBER")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

app = FastAPI()

os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
async def root():
    return {"message": "Your Emotional AI Call Assistant is ready!"}


@app.get("/call")
async def call():
    call = twilio_client.calls.create(
        to=TO_PHONE_NUMBER,
        from_=TWILIO_PHONE_NUMBER,
        url="https://87a5-2401-4900-1c64-ab4-ed1b-f4fa-6126-2180.ngrok-free.app/incoming-call"  # Replace with your public URL
    )
    return {"message": f"Call initiated. Call SID: {call.sid}"}


@app.post("/incoming-call")
async def incoming_call(request: Request):
    response = VoiceResponse()
    gather = Gather(input="speech", action="/gather", method="POST", timeout=3, speechTimeout="auto")
    # Use SSML with Polly voice
    gather.say(
        "<speak>Hello there! <break time='300ms'/> "
        "I am your friendly AI assistant, excited to help you today! "
        "What can I do for you?</speak>",
        voice="Polly.Joanna",
        language="en-US"
    )
    response.append(gather)
    response.say(
        "<speak>Sorry, I didn't hear anything. "
        "Please call again. Goodbye!</speak>",
        voice="Polly.Joanna",
        language="en-US"
    )
    return Response(content=str(response), media_type="application/xml")


@app.post("/gather")
async def gather(request: Request):
    form = await request.form()
    speech_result = form.get("SpeechResult", "")
    print(f"Caller said: {speech_result}")

    response = VoiceResponse()

    if not speech_result:
        response.say(
            "<speak>Hmm, I didn't catch that. "
            "Could you please repeat?</speak>",
            voice="Polly.Joanna",
            language="en-US"
        )
        gather = Gather(input="speech", action="/gather", method="POST", timeout=3, speechTimeout="auto")
        gather.say(
            "<speak>Go ahead, I'm listening!</speak>",
            voice="Polly.Joanna",
            language="en-US"
        )
        response.append(gather)
        return Response(content=str(response), media_type="application/xml")

    if any(word in speech_result.lower() for word in ["bye", "goodbye", "hang up", "exit", "stop"]):
        response.say(
            "<speak>Okay, ending the call now. "
            "Have a wonderful day! Goodbye!</speak>",
            voice="Polly.Joanna",
            language="en-US"
        )
        response.hangup()
        return Response(content=str(response), media_type="application/xml")

    llama_reply = get_groq_reply(speech_result)

    MAX_CHARS = 400
    if len(llama_reply) > MAX_CHARS:
        llama_reply = llama_reply[:MAX_CHARS] + "..."

        

    print(f"AI Assistant: {llama_reply}")

    # make reply in SSML
    reply_ssml = f"<speak>{llama_reply} <break time='400ms'/> Do you need anything else?</speak>"

    response.say(reply_ssml, voice="Polly.Joanna", language="en-US")
    gather = Gather(input="speech", action="/gather", method="POST", timeout=3, speechTimeout="auto")
    # gather.say(
    #     "<speak>I'm still here if you need me!</speak>",
    #     voice="Polly.Joanna",
    #     language="en-US"
    # )
    response.append(gather)

    return Response(content=str(response), media_type="application/xml")


def get_groq_reply(prompt):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "llama3-8b-8192",
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are a warm, human-like AI assistant. "
                    "Reply in a friendly, conversational tone with feeling. "
                    "Use natural expressions like wow, great, oh! Keep it under 50 words."
                )
            },
            {"role": "user", "content": prompt}
        ]
    }
    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers=headers,
        json=payload
    )
    data = response.json()
    reply = data["choices"][0]["message"]["content"]
    return reply.strip()