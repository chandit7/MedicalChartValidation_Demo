import os
from dotenv import load_dotenv

# Test if .env is loading correctly
print("=" * 50)
print("Testing .env file loading")
print("=" * 50)

# Before loading
print("\n1. Before load_dotenv():")
print(f"   GROQ_API_KEY = {os.getenv('GROQ_API_KEY', 'NOT SET')}")

# Load .env
load_dotenv()

# After loading
print("\n2. After load_dotenv():")
api_key = os.getenv('GROQ_API_KEY', 'NOT SET')
print(f"   GROQ_API_KEY = {api_key}")

if api_key and api_key != 'NOT SET':
    print(f"\n3. API Key Details:")
    print(f"   Length: {len(api_key)}")
    print(f"   First 10 chars: {api_key[:10]}...")
    print(f"   Last 4 chars: ...{api_key[-4:]}")
    
    # Test with Groq
    print("\n4. Testing with Groq API:")
    try:
        from groq import Groq
        client = Groq(api_key=api_key)
        response = client.chat.completions.create(
            model='llama-3.3-70b-versatile',
            messages=[{'role': 'user', 'content': 'test'}],
            max_tokens=5
        )
        print(f"   SUCCESS: {response.choices[0].message.content}")
    except Exception as e:
        print(f"   FAILED: {str(e)}")
else:
    print("\n❌ API Key not loaded from .env file!")

print("\n" + "=" * 50)

# Made with Bob
