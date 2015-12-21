# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _
from yowlayer_store.models.contacts import Contact

TYPE_CONTACT = "contact"
TYPE_GROUP = "group"
TYPE_BROADCAST = "broadcast"


class Conversation(models.Model):
    contact = models.ForeignKey(Contact, null=True)
    created = models.DateTimeField(_("Date created"), auto_now_add=True)

    def __unicode__(self):
        return str(self.contact) + " " + str(self.created)

    def get_type(self):
        if self.contact:
            return TYPE_CONTACT

    def to_dict(self):
        return {
            "contact": self.contact.to_dict() if self.contact else None,
            # TODO:Add group and broadcast field to Conversation
            # "group": self.group.toDict() if self.group else None,
            # "broadcast": self.broadcast.toDict() if self.broadcast else None,
            "type": self.get_type(),
            "created": self.created
        }
