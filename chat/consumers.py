import asyncio
import json
import datetime
from django.contrib.auth import get_user
from channels.consumer import AsyncConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model


from .models import Chat, Message

# Создание класса работающего с вебсокетами
class ChatConsumer(AsyncConsumer):

	User = get_user_model()
	# Обработка события соединения
	async def websocket_connect(self, event):
		print(event)
		await self.send({
			'type': 'websocket.accept'
		})
		companion_username = self.scope['url_route']['kwargs']['username']
		self.user = self.scope['user']
		companion = self.User.objects.get(username=companion_username)
		self.chat = await self.get_chat(self.user, companion_username)
		chat_room = f'chat_{self.chat.id}'
		self.chat_room = chat_room
		await self.channel_layer.group_add(
			chat_room, 
			self.channel_name
		)

	# Обработка получения сообщения 
	async def websocket_receive(self, event):
		print(event)
		front_text = event.get('text', None)
		if front_text is not None:
			loaded_dict_data = json.loads(front_text)
			message = loaded_dict_data.get('message')
			author = loaded_dict_data.get('author')
		if message:
			new_message = Message.objects.create(chat=self.chat, author=self.user, content=message)
			current_datetime = datetime.datetime.now().strftime("%H:%M")
		data = {
			'message': message, 
			'author': author, 
			'timestamp': str(current_datetime)
		}
		await self.channel_layer.group_send(
			self.chat_room, 
			{
				'type': 'chat_message', 
				'text': json.dumps(data),		
			}
		)
    # Функция формирования сообщения 
	async def chat_message(self, event):
		await self.send({
			'type': 'websocket.send', 
			'text': event['text']
		})
	# Обработка рассоединения с вебсокетом
	async def websocket_disconnect(self, event):
		print(event)
	# Получение объекта диалога двух пользователей
	@database_sync_to_async	
	def get_chat(self, user, other_username):
		return Chat.objects.get_or_new(user, other_username)
