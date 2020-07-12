from django.conf.urls import url

from .views import Chat

app_name = 'chat'
# Соединение функции отображения с адресом
urlpatterns = [
	url(r'^chat/(?P<username>\w+)/$', chat_views.Chat.as_view(), name='chat'),
]