from django.contrib import admin
from yowlayer_store.models import Message, MessageState, Contact, Conversation, \
    State
admin.site.register(Message)
admin.site.register(MessageState)
admin.site.register(Contact)
admin.site.register(Conversation)
admin.site.register(State)
