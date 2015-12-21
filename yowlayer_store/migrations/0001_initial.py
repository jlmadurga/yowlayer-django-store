# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('number', models.CharField(max_length=64, null=True, verbose_name='Number')),
                ('jid', models.CharField(max_length=64, verbose_name='Jid')),
                ('last_seen_on', models.DateTimeField(null=True, verbose_name='Last seen')),
                ('status', models.CharField(max_length=128, null=True, verbose_name='Status')),
                ('push_name', models.CharField(max_length=128, null=True, verbose_name='Push name')),
                ('name', models.CharField(max_length=128, null=True, verbose_name='Name')),
            ],
        ),
        migrations.CreateModel(
            name='Conversation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Date created')),
                ('contact', models.ForeignKey(to='yowlayer_store.Contact', null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('id_gen', models.CharField(unique=True, max_length=64)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Date created')),
                ('t_sent', models.DateTimeField(auto_now=True, verbose_name='Date sent')),
                ('content', models.TextField(null=True, verbose_name='Content')),
                ('conversation', models.ForeignKey(to='yowlayer_store.Conversation')),
            ],
        ),
        migrations.CreateModel(
            name='MessageState',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('state', models.CharField(max_length=128, verbose_name='state', choices=[(b'received', 'Received'), (b'received_remote', 'Received remote'), (b'received_read', 'Received read'), (b'received_read', 'Received read remote'), (b'sent_queued', 'Send queued'), (b'sent', 'Sent'), (b'sent_delivered', 'Sent delivered'), (b'sent_read', 'Sent Read')])),
                ('contact', models.ForeignKey(related_name='messages_states', to='yowlayer_store.Contact', null=True)),
                ('message', models.ForeignKey(related_name='states', to='yowlayer_store.Message')),
            ],
        ),
    ]
