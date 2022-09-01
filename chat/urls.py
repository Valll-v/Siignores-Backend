from django.urls import path
from . import views

urlpatterns = [
    path('<int:chat_id>/', views.ChatView.as_view({'get': 'get'})),
    path('all/', views.ChatView.as_view({'get': 'get_user_chats'})),
    path('', views.ChatView.as_view({'post': 'create_chat'})),
    path('user/', views.ChatView.as_view({'post': 'add_user', 'delete': 'delete_user'})),
]
