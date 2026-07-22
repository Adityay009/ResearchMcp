from dotenv import load_dotenv
import os

load_dotenv()
key = os.getenv("GOOGLE_API_KEY")

if key:
    print("Key loaded, starts with:", key[:8] + "...")
else:
    print("Key NOT found — check your .env file")