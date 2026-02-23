import google.generativeai as genai
from decouple import config

def list_models():
    api_key = config("GEMINI_API_KEY", default="")
    genai.configure(api_key=api_key)
    print("Listing available Gemini models...")
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f"Model ID: {m.name}")
    except Exception as e:
        print(f"Error listing models: {e}")

if __name__ == "__main__":
    list_models()
