import google.generativeai as genai
from groq import Groq
from decouple import config
import requests
import base64
import PIL.Image
import io
import wikipedia
import pywhatkit as kit
from email.message import EmailMessage
import smtplib

# AI Configuration
def configure_genai():
    api_key = config("GEMINI_API_KEY", default="")
    if api_key:
        genai.configure(api_key=api_key)

configure_genai()

def get_ai_response(query, chat_history=None):
    api_key = config("GEMINI_API_KEY", default="")
    if not api_key: return "Sir, the primary neural brain is offline."
    
    # Rotation for Text AI
    models_to_try = ['gemini-2.0-flash', 'gemini-1.5-flash']
    
    for model_id in models_to_try:
        try:
            model = genai.GenerativeModel(model_id)
            persona = "You are JARVIS, a highly advanced AI created by Dilpreet Singh. Respond concisely and professionally."
            full_context = f"Instruction: {persona}\n"
            if chat_history:
                for msg in chat_history:
                    role = "User" if msg['role'] == 'user' else "JARVIS"
                    full_context += f"{role}: {msg['content']}\n"
            full_context += f"User: {query}"
            response = model.generate_content(full_context)
            if response.text: return response.text
        except Exception as e:
            if "429" in str(e):
                print(f"MODEL {model_id} SATURATED. SHIFTING TO BACKUP...")
                continue
            print(f"AI ERROR ({model_id}): {e}")
            break
            
    # Ultimate Fallback: Groq Text
    return get_groq_response(query, chat_history)

def get_groq_response(query, chat_history=None):
    api_key = config("GROQ_API_KEY", default="")
    if not api_key: return "Sir, all neural cores are saturated."
    try:
        client = Groq(api_key=api_key)
        persona = "You are JARVIS, Dilpreet Singh's assistant."
        messages = [{"role": "system", "content": persona}]
        if chat_history:
            for msg in chat_history: messages.append(msg)
        messages.append({"role": "user", "content": query})
        
        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            max_tokens=512
        )
        return completion.choices[0].message.content
    except: return "I apologize sir, but I'm unable to connect to any neural hub at the moment."

def get_vision_response(image_data, query="Analyze this visual input, sir."):
    if isinstance(image_data, bytes):
        image_bytes = image_data
    else:
        img = PIL.Image.open(image_data)
        byte_arr = io.BytesIO()
        img.save(byte_arr, format='JPEG')
        image_bytes = byte_arr.getvalue()

    # Model Rotation for Vision to bypass 429s
    # Using 'flash-lite' as primary because it has higher free quotas
    vision_models = ['gemini-2.0-flash-lite', 'gemini-2.0-flash', 'gemini-1.5-flash']
    
    for model_id in vision_models:
        try:
            model = genai.GenerativeModel(model_id)
            img = PIL.Image.open(io.BytesIO(image_bytes))
            persona = "You are JARVIS. Describe this accurately for Dilpreet Singh."
            response = model.generate_content([persona, query, img])
            if response.text: return response.text
        except Exception as e:
            if "429" in str(e):
                print(f"VISION HUB {model_id} SATURATED. ROTATING SENSORS...")
                continue
            print(f"VISION ERROR ({model_id}): {e}")
            
    return "Sir, every available vision hub is currently saturated. I recommend a 60-second cooldown."

# --- Support ---
def search_on_wikipidia(query):
    try: return wikipedia.summary(query, sentences=2)
    except: return "No data found."

def search_on_google(query): kit.search(query)
def youtube(video): kit.playonyt(video)

def weather_forecast(city):
    WEATHER_API_KEY = config("WEATHER_API_KEY", default="")
    try:
        res = requests.get(f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric").json()
        return res["weather"][0]["main"], f"{res['main']['temp']}°C", f"{res['main']['feels_like']}°C"
    except: return "Unknown", "N/A", "N/A"

def find_my_ip():
    try: return requests.get("https://api.ipify.org?format=json").json()["ip"]
    except: return "Unknown"

def get_random_fact():
    try:
        res = requests.get("https://uselessfacts.jsph.pl/api/v2/facts/random").json()
        return res["text"]
    except: return "I'm having trouble accessing my knowledge base, sir."

def get_dictionary_meaning(word):
    try:
        res = requests.get(f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}").json()
        return res[0]['meanings'][0]['definitions'][0]['definition']
    except: return None

def send_email(receiver_add, subject, message):
    try:
        EMAIL = config("EMAIL", default="")
        PASSWORD = config("PASSWORD", default="")
        email = EmailMessage()
        email['To'], email['Subject'], email['From'] = receiver_add, subject, EMAIL
        email.set_content(message)
        s = smtplib.SMTP("smtp.gmail.com", 587)
        s.starttls()
        s.login(EMAIL, PASSWORD)
        s.send_message(email)
        s.close()
        return True
    except: return False

def get_latest_news():
    try:
        NEWS_API_KEY = config("NEWS_API_KEY", default="")
        if not NEWS_API_KEY: return "Sir, the news uplink is not configured."
        url = f"https://newsapi.org/v2/top-headlines?country=in&apiKey={NEWS_API_KEY}"
        res = requests.get(url).json()
        articles = res["articles"]
        results = []
        for ar in articles[:3]:
            results.append(ar["title"])
        return results
    except: return ["I'm unable to reach the news satellite at the moment, sir."]

def get_joke():
    try:
        res = requests.get("https://v2.jokeapi.dev/joke/Any?blacklistFlags=nsfw,religious,political,racist,sexist,explicit&type=single").json()
        if res["type"] == "single": return res["joke"]
        else: return f"{res['setup']} ... {res['delivery']}"
    except: return "I'm not in a funny mood right now, sir."

def get_advice():
    try:
        res = requests.get("https://api.adviceslip.com/advice").json()
        return res['slip']['advice']
    except: return "Focus on the task at hand, sir. That is my best advice."
