import os
from fastapi import FastAPI, Request
from fastapi.responses import Response
from fastapi.staticfiles import StaticFiles
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Gather
import requests
from gtts import gTTS
from dotenv import load_dotenv

load_dotenv()

# Twilio credentials
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
TO_PHONE_NUMBER = os.getenv("TO_PHONE_NUMBER") 

# Groq API key
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

twilio_client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

app = FastAPI()

# Serve static files for MP3 playback
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
async def root():
    return {"message": " Your AI Call Assistant is ready!"}

# initiate a call
@app.get("/make-call")
async def make_call():
    call = twilio_client.calls.create(
        to=TO_PHONE_NUMBER,
        from_=TWILIO_PHONE_NUMBER,
        url="https://fd0f-2405-201-4016-9818-203a-c5c7-ae1-7d0b.ngrok-free.app/incoming-call"  # 👈 Replace with your public ngrok URL
    )
    return {"message": f"Call initiated. Call SID: {call.sid}"}

# Twilio when call connects
@app.post("/incoming-call")
async def incoming_call(request: Request):
    response = VoiceResponse()
    gather = Gather(input="speech", action="/gather", method="POST")
    gather.say("Hello! I am your AI assistant. How can I help you today?")
    response.append(gather)
    response.say("Sorry, I didn't hear anything. Goodbye!")
    return Response(content=str(response), media_type="application/xml")

#  caller speech
@app.post("/gather")
async def gather(request: Request):
    form = await request.form()
    speech_result = form.get("SpeechResult", "")
    print(f"📞 Caller said: {speech_result}")

    if not speech_result:
        response = VoiceResponse()
        response.say("Sorry, I didn't catch that. Please try again.")
        gather = Gather(input="speech", action="/gather", method="POST")
        gather.say("Please say something.")
        response.append(gather)
        return Response(content=str(response), media_type="application/xml")

    llama_reply = get_groq_reply(speech_result)

    MAX_CHARS = 400
    if len(llama_reply) > MAX_CHARS:
        llama_reply = llama_reply[:MAX_CHARS] + "..."

    print(f"🤖 Llama3 (truncated if needed): {llama_reply}")

    # Convert to speech
    tts = gTTS(llama_reply)
    audio_path = "static/response.mp3"
    tts.save(audio_path)

    response = VoiceResponse()
    response.play(f"{request.base_url}static/response.mp3")
    gather = Gather(input="speech", action="/gather", method="POST")
    gather.say("Would you like to ask me something else?")
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
                "content": "You are a helpful AI assistant. Keep your answers concise and under 50 words."
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