from django.urls import path
from . import views

urlpatterns = [
    path('', views.chat_rag, name='chat_rag'),
    path('starters/', views.chat_starters, name='chat_starters'),
    path('chatbot/', views.chatbot_page, name='chatbot_page'),
] 