from django.contrib import admin
from langchain_core.messages import ChatMessage
from .models import ChatSession, ChatMessage, MentalHealthResource

from chat.models import ChatSession

# Register your models here.
admin.site.register(ChatSession)
admin.site.register(ChatMessage)
admin.site.register(MentalHealthResource)