from django.db import models
from django.conf import settings
from django.db.models import Q


# Класс обрабатывающий модели диалогов
class ChatManager(models.Manager):
	# Функция получения чата по именам двух пользователей
	def get_or_new(self, user, other_username):
		username = user.username
		if username == other_username:
			return None
		qlookup1 = Q(user__username=username) & Q(companion__username=other_username)
		qlookup2 = Q(user__username=other_username) & Q(companion__username=username)
		queryset = self.get_queryset().filter(qlookup1 | qlookup2).distinct()
		if queryset.count() >= 1:
			return queryset.first()
		else:
			Klass = user.__class__
			other_user = Klass.objects.get(username=other_username)
			if user != other_user:
				obj = self.model(user=user, companion=other_user)
				obj.save()
				return obj
		return None

# Модель диалога
class Chat(models.Model):
	user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='current_user', default=0)
	companion = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='companion_user', default=0)

	objects = ChatManager()

	def __str__(self):
		return self.user.username + " " + self.companion.username

# Модель сообщения
class Message(models.Model):
	chat = models.ForeignKey('Chat', on_delete=models.CASCADE, default=0)
	author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
	content = models.TextField()
	timestamp = models.DateTimeField(auto_now_add=True)

#Модель запроса в друзья
class RequestToFriend(models.Model):
    from_request = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='from_request', default=0)
    to_request = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='to_request', default=0)
