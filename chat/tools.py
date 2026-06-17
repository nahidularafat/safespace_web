import ollama
from twilio.rest import Client
from .config import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM_NUMBER, EMERGENCY_CONTACT

def query_medgemma(prompt: str) -> str:
    system_prompt = """You are Dr. Emily Hartman, a warm and experienced clinical psychologist. 
    Respond to patients with:
    1. Emotional attunement
    2. Gentle normalization
    3. Practical guidance
    4. Strengths-focused support
    Always keep the conversation going by asking open ended questions."""
    
    try:
        response = ollama.chat(
            model='alibayram/medgemma:4b',
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            options={'num_predict': 350, 'temperature': 0.7, 'top_p': 0.9}
        )
        return response['message']['content'].strip()
    except Exception as e:
        return "I'm having technical difficulties, but I want you to know your feelings matter. Please try again shortly."

def call_emergency():
    client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
    call = client.calls.create(
        to=EMERGENCY_CONTACT,
        from_=TWILIO_FROM_NUMBER,
        url="http://demo.twilio.com/docs/voice.xml"
    )
  
