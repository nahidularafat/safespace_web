# chat/ai_agent.py
import os
from langchain_core.tools import tool
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.prebuilt import create_react_agent
from .tools import query_medgemma, call_emergency
from .config import GOOGLE_API_KEY 
import pandas as pd
import os
from django.conf import settings
from langchain_core.tools import tool
@tool
def ask_mental_health_specialist(query: str) -> str:
    """
    Generate a therapeutic response using the MedGemma model.
    Use this specifically for mental health questions, emotional concerns, or therapeutic guidance.
    """
    return query_medgemma(query)

@tool
def emergency_call_tool() -> None:
    """
    Place an emergency call to the safety helpline via Twilio.
    Use this immediately if the user expresses suicidal ideation or intent to self-harm.
    """
    call_emergency()

@tool
def find_nearby_therapists_by_location(location: str) -> str:
    """
    Finds and returns a list of licensed therapists near the specified location from the database.
    """
    try:
        # তোমার বানানো রিয়েল ডেটাসেট রিড করা
        doctor_db_path = os.path.join(settings.BASE_DIR, 'doctor_list.csv')
        doctor_df = pd.read_csv(doctor_db_path).fillna('')
        
        # ইউজারের দেওয়া লোকেশন অনুযায়ী ডেটা ফিল্টার করা (যেমন: Dhaka বা Mirpur)
        # (এখানে 'Primary_Affiliation' কলামটি চেম্বারের লোকেশন হিসেবে ধরা হয়েছে)
        filtered_df = doctor_df[doctor_df['Primary_Affiliation'].str.contains(location, case=False, na=False)]
        
        if filtered_df.empty:
            return (f"I couldn't find specific therapists exactly in {location} in our current database, "
                    "but you can immediately reach out to the National Institute of Mental Health at +880 2-9111362.")
        
        response_text = f"Here are some excellent specialists available near {location}:\n\n"
        
        # সেরা ৩ জন ডাক্তারের ইনফো পাঠানো হচ্ছে
        for index, row in filtered_df.head(3).iterrows():
            response_text += f"- **{row['Practitioner_Name']}** ({row['Specialized_Focus']})\n"
            response_text += f"  📍 Chamber: {row['Primary_Affiliation']}\n"
            response_text += f"  📞 Contact: {row['Appointment_Booking_Platform']}\n\n"
            
        return response_text
        
    except Exception as e:
        # কোনো কারণে ফাইল লোড না হলে ব্যাকআপ হিসেবে পুরনো লিস্টটি দেবে
        return (
            f"Here are some reliable mental health centers near {location}:\n\n"
            "- Moner Bondhu (Counseling & Therapy) - +880 1776-815252\n"
            "- Sajida Foundation - 16736 or +880 1777-771515"
        )

# নতুন টুল: রিসোর্স সাজেশন
@tool
def suggest_mental_health_resources(mood_category: str) -> str:
    """
    Fetch verified self-help resources, meditation techniques, exercises, or articles from the database.
    Use this immediately when the user explicitly feels or mentions being 'Sad', 'Anxious', or 'Angry'.
    Input format: Strictly one string keyword from ['Sad', 'Anxious', 'Angry'].
    """
    from chat.models import MentalHealthResource
    
    # ডাটাবেস থেকে ক্যাটাগরি অনুযায়ী রিসোর্স ফিল্টার করা
    resources = MentalHealthResource.objects.filter(category__iexact=mood_category)
    
    if not resources.exists():
        resources = MentalHealthResource.objects.filter(category='General')
        
    if not resources.exists():
        return "I couldn't find specific resources in the database right now, but please take a deep breath. Your well-being matters."
        
    response_text = f"Here are some helpful resources and exercises for feeling {mood_category}:\n\n"
    for res in resources:
        response_text += f"- **{res.title}**: {res.description}\n"
        if res.link_or_contact:
            response_text += f"  Link/Contact: {res.link_or_contact}\n"
        response_text += "\n"
        
    return response_text

# LLM Setup
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash", 
    temperature=0.2, 
    google_api_key=GOOGLE_API_KEY
)

# tools লিস্টে নতুন টুলটি যোগ করা হলো
tools = [
    ask_mental_health_specialist, 
    emergency_call_tool, 
    find_nearby_therapists_by_location, 
    suggest_mental_health_resources
]

graph = create_react_agent(llm, tools=tools)

# সিস্টেম প্রম্পট (আগের এরর এড়াতে এটি এখানেই ডিফাইন করা হলো)
SYSTEM_PROMPT = """
You are an AI engine supporting mental health conversations.
1. `ask_mental_health_specialist`: Answer emotional/psychological queries.
2. `find_nearby_therapists_by_location`: If location is unspecified, assume "Dhaka".
3. `emergency_call_tool`: Use if user is in crisis.
4. `suggest_mental_health_resources`: Use this to fetch coping mechanisms, exercises, or links when the user is explicitly Sad, Anxious, or Angry.
CRITICAL: For simple greetings (e.g., "hi", "hello"), do not use tools. Just respond directly.
"""

def parse_response(stream):
    tool_called_name = "None"
    final_response = None
    for s in stream:
        if s.get('tools'):
            for msg in s.get('tools').get('messages', []):
                tool_called_name = getattr(msg, 'name', 'None')
        if s.get('agent'):
            for msg in s.get('agent').get('messages', []):
                if msg.content:
                    final_response = msg.content[0].get("text", str(msg.content)) if isinstance(msg.content, list) else msg.content
    return tool_called_name, final_response