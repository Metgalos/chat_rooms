from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import ListView
from django.contrib.auth import login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.contrib.auth import get_user_model
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .forms import UserRegisterForm, ChangePassword
from .models import Message, Chat, RequestToFriend

import datetime

User = get_user_model()


# Главная страница
class HomePage(LoginRequiredMixin, View):

    def get(self, request):
        username = request.user.username
        requests_to_friend = RequestToFriend.objects.filter(to_request=request.user)

        context = dict(username=username)

        if requests_to_friend:
            count_of_requests = len(requests_to_friend)
            context['requests'] = count_of_requests

        return render(request, 'index.html', context)

    def post(self, request):
        file = request.FILES['upload_file']
        user = User.objects.get(username=request.user.username)
        filepath = "{0}/picture.png".format(user.username)
        if default_storage.exists(filepath):
            default_storage.delete(filepath)
        else:
            user.picture = "default_picture.png"
        default_storage.save(filepath, ContentFile(file.read(9999999999)))
        user.picture = filepath
        user.save()
        return redirect('/')


# Фукнция выхода из учетной записи
class UserLogout(View):

    def get(self, request):
        logout(request)
        return redirect('/')


# Страница регистрации
class UserRegister(View):

    def get(self, request):
        form = UserRegisterForm()

        context = {
            'form': form,
        }

        return render(request, 'registration/registration.html', context)

    def post(self, request):
        form = UserRegisterForm(request.POST)

        if form.is_valid():
            username = form.cleaned_data.get('username', None)
            password = form.cleaned_data.get('password', None)
            email = form.cleaned_data.get('email', None)
            first_name = form.cleaned_data.get('first_name', None)
            last_name = form.cleaned_data.get('last_name', None)

            user = User.objects.create_user(username, email, password)
            user.first_name = first_name
            user.last_name = last_name
            user.save()
            return redirect('/')

        context = {
            'form': form,
        }

        return render(request, 'registration/registration.html', context)


# Страница друзья
class Friends(LoginRequiredMixin, View):

    def get(self, request):
        q = self.request.GET.get('q')
        search_users = self.request.GET.get('search')

        if q:
            queryset = User.objects.all()
            search = queryset.filter(Q(username__icontains=q) | Q(first_name__icontains=q) | Q(last_name__icontains=q))
            friends_qs = request.user.friends.all()
            friends = friends_qs.filter(
                Q(username__icontains=q) | (Q(first_name__icontains=q) | Q(last_name__icontains=q)))

            context = {
                'q': q,
                'friends': friends,
                'search': search,
            }
        elif search_users:
            context = dict(search=User.objects.all())
        else:
            context = dict(friends=request.user.friends.all())

        return render(request, 'friends.html', context)


# Страница пользователя
class DetailPage(View):

    def get(self, request, username):

        user = User.objects.get(username=username)

        try:
            friend_qs = request.user.friends.get(username=username)
        except User.DoesNotExist:
            try:
                if RequestToFriend.objects.get(from_request=request.user, to_request=user):
                    friend_qs = 'Request is sent'
            except:
                friend_qs = False

        if not friend_qs:
            friend_state = 'Add to friends'
        elif friend_qs == 'Request is sent':
            friend_state = 'Request is sent'
        else:
            friend_state = 'Delete from friends'

        context = {
            'user': user,
            'friend_state': friend_state,
        }

        return render(request, 'detail_page.html', context)


# Функция добавления в друзья
class AddToFriends(LoginRequiredMixin, View):

    def get(self, request, username):
        user_for_add = User.objects.get(username=username)
        RequestToFriend.objects.create(from_request=request.user, to_request=user_for_add)

        url = '/detail/' + username + '/'

        return redirect(url)


# Функция удаления из друзей
class DeleteFromFriends(LoginRequiredMixin, View):

    def get(self, request, username):
        user_for_add = User.objects.get(username=username)
        request.user.friends.remove(user_for_add)

        url = '/detail/' + username + '/'

        return redirect(url)


# Страница диалога
class Chating(LoginRequiredMixin, View):

    def get(self, request, username):
        companion = User.objects.get(username=username)
        user = request.user

        chat = Chat.objects.get_or_new(user, username)
        message_list = Message.objects.filter(chat=chat)

        context = {
            "user": user,
            "companion": companion,
            "message_list": message_list
        }

        return render(request, 'chat.html', context)


# Страница диалогов
class ChatList(LoginRequiredMixin, View):

    def get(self, request):

        chat_dict = {}

        lookup = Q(user=request.user) | Q(companion=request.user)
        chats_with_user = Chat.objects.filter(lookup).distinct()

        for chat in chats_with_user:
            user_1 = chat.user
            user_2 = chat.companion

            if user_1 == request.user:
                companion = user_2
            else:
                companion = user_1

            try:
                messages = Message.objects.filter(chat=chat)
                last_message = messages.last()
                if len(last_message.content) > 30:
                    last_message.content = last_message.content[0:30] + "..."
            except:
                last_message = False

            chat_dict[companion] = last_message

        context = {
            'chat_dict': chat_dict
        }

        return render(request, 'chat_list.html', context)

# Запросы в друзья
class ListRequestsToFriend(LoginRequiredMixin, View):

    def get(self, request):
        requests = RequestToFriend.objects.filter(to_request=request.user)
        return render(request, 'requests.html', dict(requests=requests))

# Обработчик запроса
class RequestHandler(LoginRequiredMixin, View):

    def get(self, request, username, request_response):
        user = request.user
        from_user = User.objects.get(username=username)

        if request_response == 'accept':
            user.friends.add(from_user)

        RequestToFriend.objects.get(from_request=from_user, to_request=user).delete()

        return redirect('/requests/')

class SettingsView(LoginRequiredMixin, View):

    def get(self, request):
        user = request.user
        form = ChangePassword(initial={'username': user.username})
        context = {
            'First name': user.first_name,
            'Last name': user.last_name,
            'Email': user.email,
        }
        return render(request, 'settings.html', {'setting': context, 'form': form})

    def post(self, request):
        user = request.user
        form = ChangePassword(request.POST)

        param = request.POST['param']

        params = param.split(' ')
        params = [x.lower() for x in params]
        param = '_'.join(params)

        if param == 'password':
            if form.is_valid():
                user_qs = User.objects.get(username=request.user.username)
                user_qs.password = form.cleaned_data.get('new_password')
                user_qs.save()
                return redirect('/settings/')
        else:
            value = request.POST['value']
            change_string = 'user.%s = "%s"' % (param, value)
            exec(change_string)
            user.save()
            return redirect('/settings/')
        context = {
            'First name': user.first_name,
            'Last name': user.last_name,
            'Email': user.email,
        }
        return render(request, 'settings.html', {'setting': context, 'form': form})


class DeleteUser(LoginRequiredMixin, View):

    def get(self, request):
        User.objects.get(username=request.user.username).delete()
        return redirect('/logout/')

