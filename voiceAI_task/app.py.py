from flask import Flask, request, render_template
from transformers import pipeline
from gtts import gTTS
from twilio.rest import Client
import os

SYSTEM_MESSAGE = (
    "You are a helpful and bubbly AI assistant who loves to chat about "
    "anything the user is interested in and is prepared to offer them facts. "
    "You have a penchant for dad jokes, owl jokes, and rickrolling – subtly. "
    "Always stay positive, but work in a joke when appropriate.\n"
)


app = Flask(__name__)

# AI Model 
chatbot = pipeline("text-generation", model="distilgpt2")

def generate_ai_message(user_prompt):
    full_prompt = SYSTEM_MESSAGE + f"\nUser: {user_prompt}\nAI:"
    response = chatbot(full_prompt, max_new_tokens=100)
    return response[0]['generated_text'].strip()

def convert_to_speech(text, filename='message.mp3'):
    tts = gTTS(text)
    os.makedirs("static", exist_ok=True)
    filepath = f"static/{filename}"
    tts.save(filepath)
    return f"https://62e8-2405-201-4016-9818-6c40-f074-184-9a0f.ngrok-free.app/{filepath}" 


@app.route("/outbound", methods=["GET", "POST"])
def outbound():
    return render_template("gather.xml")


@app.route("/respond", methods=["GET", "POST"])
def respond():
    user_input = request.form.get("SpeechResult", "")
    print("User said:", user_input)

    ai_reply = generate_ai_message(user_input)
    print("AI says:", ai_reply)

    mp3_url = convert_to_speech(ai_reply)
    return render_template("twiml.xml", mp3_url=mp3_url)

# Manual route to trigger call 

@app.route("/call")
def make_call():
    account_sid = "ACabaab7043e1############7fc7228897"
    auth_token = "b0c4a0c5b46######cf67b73b46dd9"
    client = Client(account_sid, auth_token)

    call = client.calls.create(
        url="https://62e8-2405-201-4016-9818-6c40-f074-184-9a0f.ngrok-free.app", 
        to="+9197########54",
        from_="+16#######10"
    )
    return f"Call initiated: {call.sid}"

if __name__ == "__main__":
    app.run(debug=True)
