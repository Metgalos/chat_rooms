"""project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Import the include() function: from django.conf.urls import url, include
    3. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

from chat import views as chat_views

settingpatterns = [
    url(r'delete-user/$', chat_views.DeleteUser.as_view(), name='delete-user'),
    url(r'$', chat_views.SettingsView.as_view(), name='settings'),
]

# Соединение адресов с их контроллерами
urlpatterns = [
	url(r'^login/', auth_views.LoginView.as_view()),
    url(r'^logout/$', chat_views.UserLogout.as_view()),
    url(r'^register/$', chat_views.UserRegister.as_view()),


    url(r'^$', chat_views.HomePage.as_view(), name='home'),
    url(r'^admin/', admin.site.urls),
    url(r'^friends/$', chat_views.Friends.as_view(), name='friends'),
    url(r'^chats/$', chat_views.ChatList.as_view(), name='chat_list'),
    url(r'^add-to-friends/(?P<username>\w+)/$', chat_views.AddToFriends.as_view(), name='add_to_friends'),
    url(r'^detail/(?P<username>\w+)/$', chat_views.DetailPage.as_view(), name='detail'),
    url(r'^delete-from-friends/(?P<username>\w+)/$', chat_views.DeleteFromFriends.as_view(), name='delete_from_friends'),
    url(r'^chat/(?P<username>\w+)/$', chat_views.Chating.as_view(), name='chat'),
    url(r'^requests/$', chat_views.ListRequestsToFriend.as_view(), name='requests'),
    url(r'^request/(?P<username>\w+)/(?P<request_response>\w+)/$', chat_views.RequestHandler.as_view(), name='request_handler'),
    url(r'^settings/', include(settingpatterns)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)