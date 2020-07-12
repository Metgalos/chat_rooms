from django.contrib.auth.models import AbstractUser
from django.db import models
# Фунция поиска картинки пользователя
def user_directory_path(username, filename):
	return '{0}/{1}'.format(username, filename)

# Переопределение класса пользователя (добавление картинки и списка друзей)
class User(AbstractUser):
	friends = models.ManyToManyField('self')
	picture = models.ImageField(upload_to=user_directory_path, default='default_picture.png')

	def __str__(self):
		return self.username
