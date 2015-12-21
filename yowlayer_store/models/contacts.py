# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext_lazy as _


class Contact(models.Model):
    number = models.CharField(_("Number"), unique=False, null=True, max_length=64)
    jid = models.CharField(_("Jid"), null=False, unique=False, max_length=64)
    last_seen_on = models.DateTimeField(_("Last seen"), null=True)
    status = models.CharField(_("Status"), null=True, max_length=128)
    push_name = models.CharField(_("Push name"), null=True, max_length=128)
    name = models.CharField(_("Name"), null=True, max_length=128)

    def to_dict(self):
        return {
            "number": self.number,
            "jid": self.jid,
            "last_seen_on": self.last_seen_on,
            "status": self.status,
            "push_name": self.push_name,
            "name": self.name,
            # TODO:Add picture field to contact
            # "picture": self.picture
        }

    def __unicode__(self):
        return self.jid
