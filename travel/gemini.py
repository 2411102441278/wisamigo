import os
from google import genai

client = genai.Client(
    api_key=os.getenv('GOOGLE_API_KEY', '')
)
if not os.getenv('GOOGLE_API_KEY'):
    print('Warning: GOOGLE_API_KEY is not set. Gemini client may not authenticate.')

while True:

    pesan = input("Kamu: ")

    if pesan.lower() == "exit":
        break

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=pesan
    )

    print("AI:", response.text)