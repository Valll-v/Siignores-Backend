from django.urls import path
from . import views

urlpatterns = [
    path('<int:chat_id>/', views.ChatView.as_view({'get': 'get'})),
    path('all/', views.ChatView.as_view({'get': 'get_user_chats'}))
]
