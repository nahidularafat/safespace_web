Markdown
# 🧠 AI Mental Health Agent & Clinical Assessment Tool

A comprehensive, AI-driven mental health support platform built with **Django**. This project integrates a conversational AI agent (using LangGraph and Gemini) with a highly accurate PyTorch Neural Network to provide empathetic support, clinical stress prediction, and automated therapist recommendations.

## ✨ Key Features

* **💬 Intelligent ReAct Agent:** An empathetic conversational agent powered by LangGraph and Gemini 2.5 Flash that listens, supports, and intelligently triggers specific tools based on user context.
* **📊 Clinical Stress Assessment (Explainable AI):** A custom-trained PyTorch Neural Network (`MediumNN`) that predicts user stress levels (Low, Moderate, Critical) with **92.12% accuracy** based on 20 distinct psychological and environmental metrics.
* **👨‍⚕️ Dynamic Therapist Recommendation:** Automatically fetches and recommends nearby specialized psychiatrists from a custom database (`doctor_list.csv`) when moderate or high stress is detected.
* **🚨 Emergency Crisis Intervention:** Integrates with Twilio API to automatically trigger emergency safety phone calls if suicidal ideation or self-harm intent is detected.
* **📈 Mood Tracking Dashboard:** Visualizes the user's emotional state over time using interactive charts.
* **🩺 Therapist Portal:** A dedicated dashboard for professionals to monitor patient progress and trigger proactive SMS check-ins.

## 🛠️ Technology Stack

* **Backend Framework:** Django, Python
* **Machine Learning:** PyTorch, Scikit-learn, Pandas, NumPy
* **AI/LLM:** LangChain, LangGraph, Google Gemini API, Ollama (MedGemma)
* **External APIs:** Twilio (SMS & Voice Calls)
* **Frontend:** HTML, Tailwind CSS, JavaScript
Therapist / Admin Portal Account**
Access the exclusive therapist portal to monitor patient sessions and trigger proactive SMS check-ins.
* **Username:** demo
* **Password:** demo
## 📂 Project Structure



├── chat/
│   ├── ai_agent.py        # LangGraph ReAct Agent setup and tool definitions
│   ├── tools.py           # Custom tools (MedGemma, Twilio Emergency)
│   ├── models.py          # Database models (ChatSession, Message, Resources)
│   ├── views.py           # Core logic, ML inference, and routing
│   └── templates/         # Tailwind-styled HTML templates
├── champion_model.pth     # Trained PyTorch Neural Network (92.12% Accuracy)
├── framework_scaler.pkl   # StandardScaler for input normalization
├── doctor_list.csv        # Custom dataset for therapist recommendations
├── manage.py              # Django project manager
└── requirements.txt       # Python dependencies
🚀 Installation & Setup
Follow these steps to run the project locally:

1. Clone the repository:

Bash
git clone [https://github.com/yourusername/your-repo-name.git](https://github.com/yourusername/your-repo-name.git)
cd your-repo-name
2. Create a virtual environment and activate it:

Bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate
3. Install dependencies:

Bash
pip install -r requirements.txt
4. Configure Environment Variables:
Update the chat/config.py file with your API keys:

GOOGLE_API_KEY

TWILIO_ACCOUNT_SID & TWILIO_AUTH_TOKEN

5. Apply Database Migrations:

Bash
python manage.py makemigrations
python manage.py migrate
6. Run the local server:

Bash
python manage.py runserver
Navigate to http://127.0.0.1:8000/ in your browser.

🧠 Machine Learning Architecture
The Clinical Assessment Tool utilizes a Multi-Layer Perceptron (MLP) architecture named MediumNN. It features:

Input Layer: 20 features (anxiety level, sleep quality, academic performance, etc.)

Hidden Layers: 32 neurons -> 16 neurons with Batch Normalization and ReLU activation functions.

Output Layer: 3 classes (Low, Moderate, Critical Stress).

Training Methodology: Augmented training data with carefully tuned micro-noise injection, achieving robust performance without overfitting.

🤝 Contribution
This project is developed as a Capstone/Thesis project. Feedback, bug reports, and pull requests are welcome!


text<img width="1876" height="940" alt="Screenshot 2026-07-01 181021" src="https://github.com/user-attachments/assets/000f5cf8-8081-4483-a27e-112560bf351f" />
<img width="1903" height="923" alt="Screenshot 2026-07-01 181001" src="https://github.com/user-attachments/assets/ac86c005-bba2-49ac-bf3b-78b80bef4f21" />
<img width="1894" height="924" alt="Screenshot 2026-07-01 180936" src="https://github.com/user-attachments/assets/29c7cc5d-c1e5-45dc-a7bb-a81e14e1267a" />
<img width="1903" height="930" alt="Screenshot 2026-07-01 180924" src="https://github.com/user-attachments/assets/9fce6730-28a1-4630-ad6a-432f48b24cd9" />
<img width="1918" height="932" alt="Screenshot 2026-07-01 180908" src="https://github.com/user-attachments/assets/a8cde961-eed0-40d2-abf0-e9bcab0391c8" />
