# chat/views.py
import os
import json
import joblib
import pickle
import numpy as np
import torch
import torch.nn as nn
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Count
from twilio.rest import Client

from safespace_web import settings
from .ai_agent import graph, SYSTEM_PROMPT, parse_response, llm
from .config import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_FROM_NUMBER
from .models import ChatSession, ChatMessage

# ==========================================
# 1. Authentication Views
# ==========================================
def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'chat/register.html', {'form': form})

# ==========================================
# 2. Chat Interface Views
# ==========================================
@login_required
def chat_interface(request, session_id=None):
    sessions = ChatSession.objects.filter(user=request.user).order_by('-created_at')
    active_session = get_object_or_404(ChatSession, id=session_id, user=request.user) if session_id else None
    messages = active_session.messages.all().order_by('timestamp') if active_session else []

    return render(request, 'chat/index.html', {
        'sessions': sessions,
        'active_session': active_session,
        'messages': messages,
    })

@login_required
def new_chat(request):
    session = ChatSession.objects.create(user=request.user, title="New Conversation")
    return redirect('chat_interface_with_id', session_id=session.id)

# ==========================================
# 3. Mood Tracking Helper Function
# ==========================================
def detect_user_mood(message_text):
    try:
        prompt = f"""Analyze the emotional mood of the following text. 
        Return ONLY one word from this list: [Happy, Sad, Anxious, Angry, Neutral].
        Do not include any punctuation or extra text.
        Text: "{message_text}" """
        
        response = llm.invoke(prompt)
        detected_mood = response.content.strip()
        return detected_mood if detected_mood in ['Happy', 'Sad', 'Anxious', 'Angry', 'Neutral'] else 'Neutral'
    except:
        return "Neutral"

# ==========================================
# 4. Message API View
# ==========================================
@login_required
def send_message(request):
    if request.method == "POST":
        data = json.loads(request.body)
        user_message = data.get("message")
        session_id = data.get("session_id")
        
        # সেশন লোড বা তৈরি করা
        if session_id:
            session = get_object_or_404(ChatSession, id=session_id, user=request.user)
        else:
            session = ChatSession.objects.create(user=request.user, title="New Conversation")

        # 🌟 ChatGPT-এর মতো ডাইনামিক টাইটেল লজিক 🌟
        if session.title == "New Conversation" or session.messages.count() == 0:
            try:
                title_prompt = f"Generate a short, engaging title (maximum 4 words) for a therapeutic conversation starting with this message: '{user_message}'. Return ONLY the title text, no quotes or extra text."
                title_response = llm.invoke(title_prompt)
                session.title = title_response.content.strip().replace('"', '')
                session.save()
            except:
                session.title = user_message[:25] + "..."
                session.save()

        # ইউজারের মেসেজ এবং মুড সেভ করা
        user_mood = detect_user_mood(user_message)
        ChatMessage.objects.create(session=session, role="user", content=user_message, mood=user_mood)

        # AI থেকে রেসপন্স জেনারেট করা
        try:
            inputs = {"messages": [("system", SYSTEM_PROMPT), ("user", user_message)]}
            stream = graph.stream(inputs, stream_mode="updates")
            tool_name, ai_response = parse_response(stream)
            if not ai_response:
                ai_response = "I am here to listen. Could you please tell me more?"
        except Exception as e:
            ai_response = f"An error occurred: {str(e)}"
            tool_name = "Error"

        # AI-এর রেসপন্স সেভ করা
        ChatMessage.objects.create(session=session, role="assistant", content=ai_response, tool_called=tool_name, mood="Neutral")
        
        return JsonResponse({
            "status": "success", 
            "session_id": session.id, 
            "response": ai_response, 
            "tool_called": tool_name,
            "detected_mood": user_mood
        })
    return JsonResponse({"status": "error", "message": "Invalid request"})

# ==========================================
# 5. Dashboard View (Mood Swings)
# ==========================================
@login_required
def mood_dashboard(request):
    user_messages = ChatMessage.objects.filter(session__user=request.user, role='user')
    chart_data = {}
    dates = set()
    
    for msg in user_messages:
        date_str = msg.timestamp.strftime('%Y-%m-%d')
        mood = msg.mood
        dates.add(date_str)
        if date_str not in chart_data:
            chart_data[date_str] = {'Happy': 0, 'Sad': 0, 'Anxious': 0, 'Angry': 0, 'Neutral': 0}
        if mood in chart_data[date_str]:
            chart_data[date_str][mood] += 1

    sorted_dates = sorted(list(dates))
    datasets = {
        'Happy': [chart_data[d]['Happy'] for d in sorted_dates],
        'Sad': [chart_data[d]['Sad'] for d in sorted_dates],
        'Anxious': [chart_data[d]['Anxious'] for d in sorted_dates],
        'Angry': [chart_data[d]['Angry'] for d in sorted_dates],
        'Neutral': [chart_data[d]['Neutral'] for d in sorted_dates],
    }

    return render(request, 'chat/dashboard.html', {
        'labels': json.dumps(sorted_dates),
        'datasets': json.dumps(datasets),
    })

# ==========================================
# 6. Therapist Portal View
# ==========================================
@login_required
def therapist_portal(request):
    if not request.user.is_staff:
        return redirect('home')
        
    if request.method == "POST" and 'username' in request.POST:
        new_username = request.POST.get('username')
        new_password = request.POST.get('password')
        if new_username and new_password:
            if not User.objects.filter(username=new_username).exists():
                User.objects.create_user(username=new_username, password=new_password)
        return redirect('therapist_portal')

    if request.method == "POST" and 'trigger_sms_session_id' in request.POST:
        session_id = request.POST.get('trigger_sms_session_id')
        session = get_object_or_404(ChatSession, id=session_id)
        
        try:
            client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
            message_content = f"Hello {session.user.username}, yesterday seemed a bit tough..."
            
            client.messages.create(
                 body=message_content,
                 from_=TWILIO_FROM_NUMBER,
                 to='+8801305281907'
            )
            return JsonResponse({"status": "success", "message": "Proactive SMS sent successfully!"})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)})
        
    search_query = request.GET.get('search', '')
    
    if search_query:
        patients = User.objects.filter(username__icontains=search_query, is_staff=False)
    else:
        patients = User.objects.filter(is_staff=False)

    portal_data = []
    
    for patient in patients:
        patient_sessions = ChatSession.objects.filter(user=patient).order_by('-created_at')
        
        if patient_sessions.exists():
            is_critical = ChatMessage.objects.filter(session__user=patient, tool_called='emergency_call_tool').exists()
            msg_count = ChatMessage.objects.filter(session__user=patient, role='user').count()
            
            portal_data.append({
                'patient': patient,
                'sessions': patient_sessions,
                'is_critical': is_critical,
                'msg_count': msg_count,
            })
        
    return render(request, 'chat/therapist_portal.html', {
        'portal_data': portal_data, 
        'search_query': search_query
    })

# ==========================================
# 7. Machine Learning Model for Stress Prediction
# ==========================================
import __main__  # 🌟 PyTorch Pickling-এর জন্য নতুন ইম্পোর্ট

FEATURE_NAMES = [
    'anxiety_level', 'self_esteem', 'mental_health_history', 'depression', 
    'headache', 'blood_pressure', 'sleep_quality', 'breathing_problem', 
    'noise_level', 'living_conditions', 'safety', 'basic_needs', 
    'academic_performance', 'study_load', 'teacher_student_relationship', 
    'future_career_concerns', 'social_support', 'peer_pressure', 
    'extracurricular_activities', 'bullying'
]

class MediumNN(nn.Module):
    def __init__(self):
        super(MediumNN, self).__init__()
        self.fc = nn.Sequential(
            nn.Linear(20, 32), 
            nn.BatchNorm1d(32), 
            nn.ReLU(), 
            nn.Linear(32, 16), 
            nn.BatchNorm1d(16), 
            nn.ReLU(), 
            nn.Linear(16, 3)
        )
    def forward(self, x): 
        return self.fc(x)

# 🌟 PyTorch Pickling Fix: জ্যাঙ্গোর manage.py-এর জন্য ক্লাসটিকে __main__ নেমস্পেসে যুক্ত করা হলো 🌟
setattr(__main__, 'MediumNN', MediumNN)

# গ্লোবাল ভেরিয়েবল
model = MediumNN()
scaler = None
MODEL_PATH = os.path.join(settings.BASE_DIR, 'champion_model.pth')
SCALER_PATH = os.path.join(settings.BASE_DIR, 'framework_scaler.pkl')

# লোডিং লজিক (Updated Fix with weights_only=False)
def load_ml_components():
    global scaler
    global model
    try:
        if os.path.exists(SCALER_PATH):
            scaler = joblib.load(SCALER_PATH)
        if os.path.exists(MODEL_PATH):
            # weights_only=False ব্যবহার করা হয়েছে নেমস্পেস জটিলতা এড়াতে
            state_dict = torch.load(MODEL_PATH, map_location=torch.device('cpu'), weights_only=False)
            
            # মডেলটি state_dict নাকি পুরো অবজেক্ট হিসেবে সেভ করা হয়েছে তা চেক করা হচ্ছে
            if isinstance(state_dict, dict):
                model.load_state_dict(state_dict)
            else:
                model = state_dict
                
            model.eval()
    except Exception as e:
        print(f"Loading Error: {e}")

load_ml_components()

@login_required
def stress_prediction_view(request):
    global scaler
    if scaler is None: load_ml_components()

    formatted_features = [{'raw': f, 'display': f.replace('_', ' ').title()} for f in FEATURE_NAMES]

    if request.method == 'POST':
        if scaler is None:
            return render(request, 'chat/stress_predictor.html', {'error': "Scaler not loaded!", 'features': formatted_features})

        try:
            input_data = [float(request.POST.get(f, 0.0)) for f in FEATURE_NAMES]
            input_array = np.array(input_data).reshape(1, -1)
            
            scaled_data = scaler.transform(input_array)
            tensor_data = torch.FloatTensor(scaled_data)
            
            with torch.no_grad():
                model.eval()
                logits = model(tensor_data)
                probabilities = torch.softmax(logits, dim=1)
                predicted_class = torch.argmax(probabilities, dim=1).item()
                confidence = probabilities[0][predicted_class].item() * 100
                
            status_map = {0: ("Good (Low)", "text-green-600"), 1: ("Moderate", "text-yellow-600"), 2: ("Critical", "text-red-600")}
            status, color = status_map.get(predicted_class, ("Unknown", "text-gray-600"))
                
            return render(request, 'chat/stress_predictor.html', {
                'stress_percentage': round(confidence, 2), 'status': status, 'color': color,
                'features': formatted_features
            })
        except Exception as e:
            return render(request, 'chat/stress_predictor.html', {'error': str(e), 'features': formatted_features})

    return render(request, 'chat/stress_predictor.html', {'features': formatted_features})