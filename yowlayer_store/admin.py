from django.contrib import admin
from yowlayer_store.models import Message, MessageState, Contact, Conversation
admin.site.register(Message)
admin.site.register(MessageState)
admin.site.register(Contact)
admin.site.register(Conversation)
