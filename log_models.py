import google.generativeai as genai
from decouple import config

def list_models():
    api_key = config("GEMINI_API_KEY", default="")
    genai.configure(api_key=api_key)
    with open("models.txt", "w") as f:
        try:
            for m in genai.list_models():
                f.write(f"{m.name}\n")
        except Exception as e:
            f.write(f"Error: {e}\n")

if __name__ == "__main__":
    list_models()
