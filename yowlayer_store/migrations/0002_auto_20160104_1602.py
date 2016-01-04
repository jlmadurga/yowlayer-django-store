# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('yowlayer_store', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Media',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.CharField(max_length=128, verbose_name='Type', choices=[(b'image', 'Type Image'), (b'audio', 'Type Audio'), (b'video', 'Type Video'), (b'vcard', 'Type VCard'), (b'location', 'Type Location')])),
                ('preview', models.BinaryField(verbose_name='Preview', null=True)),
                ('transfer_status', models.IntegerField(default=0, verbose_name='Transfer Status')),
                ('remote_url', models.URLField(null=True, verbose_name='Remote Url')),
                ('size', models.IntegerField(null=True, verbose_name='Size')),
                ('mimetype', models.CharField(max_length=128, null=True, verbose_name='Mime Type')),
                ('filehash', models.CharField(unique=True, max_length=128, verbose_name='File Hash')),
                ('filename', models.CharField(max_length=128, null=True, verbose_name='File Name')),
                ('encoding', models.CharField(max_length=128, null=True, verbose_name='Encoding')),
                ('data', models.TextField(unique=True, verbose_name='Data')),
            ],
        ),
        migrations.AlterField(
            model_name='message',
            name='conversation',
            field=models.ForeignKey(verbose_name='Conversation', to='yowlayer_store.Conversation'),
        ),
        migrations.AddField(
            model_name='message',
            name='media',
            field=models.ForeignKey(verbose_name='Media', to='yowlayer_store.Media', null=True),
        ),
    ]
