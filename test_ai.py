from google import genai
from decouple import config

api_key = config("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

try:
    print("Testing gemini-1.5-flash...")
    response = client.models.generate_content(
        model='gemini-1.5-flash',
        contents='Hello'
    )
    print("Success with gemini-1.5-flash")
except Exception as e:
    print(f"Error with gemini-1.5-flash: {e}")

try:
    print("\nTesting gemini-2.0-flash...")
    response = client.models.generate_content(
        model='gemini-2.0-flash',
        contents='Hello'
    )
    print("Success with gemini-2.0-flash")
except Exception as e:
    print(f"Error with gemini-2.0-flash: {e}")
