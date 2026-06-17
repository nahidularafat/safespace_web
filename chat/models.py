# chat/models.py
from django.db import models
from django.contrib.auth.models import User

class ChatSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sessions')
    title = models.CharField(max_length=255, default="New Conversation")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.title}"

class ChatMessage(models.Model):
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=10) # 'user' or 'assistant'
    content = models.TextField()
    tool_called = models.CharField(max_length=100, default="None")
    mood = models.CharField(max_length=20, default="Neutral") # ড্যাশবোর্ডের জন্য মুড ফিল্ড
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.role}: {self.content[:50]}"

# নতুন: রিসোর্স সাজেশনের জন্য মডেল
class MentalHealthResource(models.Model):
    CATEGORY_CHOICES = [
        ('Sad', 'Sad'),
        ('Anxious', 'Anxious'),
        ('Angry', 'Angry'),
        ('General', 'General'),
    ]
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    title = models.CharField(max_length=255)
    description = models.TextField()
    link_or_contact = models.CharField(max_length=500, blank=True, null=True)

    def __str__(self):
        return f"[{self.category}] {self.title}"