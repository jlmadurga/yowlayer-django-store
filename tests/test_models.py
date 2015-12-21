#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_yowlayer-django-store
------------

Tests for `yowlayer-django-store` models module.
"""

from django.test import TestCase
from yowlayer_store.layer import YowStorageLayer
from yowsup.stacks.yowstack import YowStack
from yowsup.layers import YowLayer
from yowsup.layers.protocol_messages.protocolentities import TextMessageProtocolEntity
from yowsup.layers.protocol_acks.protocolentities import IncomingAckProtocolEntity
from yowsup.layers.protocol_receipts.protocolentities import IncomingReceiptProtocolEntity, \
    OutgoingReceiptProtocolEntity
from yowsup.layers.protocol_contacts.protocolentities import ResultSyncIqProtocolEntity, GetSyncIqProtocolEntity
from yowsup.layers.auth.protocolentities import SuccessProtocolEntity
import time
import six
from yowlayer_store.models.messages import MessageState


class DummySenderLayer(YowLayer):

    def __init__(self):
        super(DummySenderLayer, self).__init__()
        self.lower_sink = []
        self.toLower = self.send_overrider

    def send_overrider(self, data):
        self.lower_sink.append(data)


class DummyReceiverLayer(YowLayer):

    def __init__(self):
        super(DummyReceiverLayer, self).__init__()
        self.upper_sink = []
        self.toUpper = self.receiver_overrider

    def receiver_overrider(self, data):
        self.upper_sink.append(data)


class TestStorageLayer(TestCase):

    def setUp(self):
        self.stack = YowStack((DummyReceiverLayer, YowStorageLayer, DummySenderLayer))
        self.storage_layer = self.stack.getLayerInterface(YowStorageLayer)
        self.dummy_top_layer = self.stack.getLayer(2)
        self.dummy_bottom_layer = self.stack.getLayer(0)

    def assertEqualUpper(self, data):
        self.assertEqual(data, self.dummy_top_layer.upper_sink.pop())

    def assertEqualLower(self, data):
        self.assertEqual(data, self.dummy_bottom_layer.lower_sink.pop())

    def send_message(self, content="Hello World"):
        msg_content = content
        msg_jid = "aaa@s.whatsapp.net"
        msg = TextMessageProtocolEntity(msg_content, to=msg_jid)
        self.stack.send(msg)
        self.assertEqualLower(msg)
        return msg

    def send_receipt(self, message, read=False, participant=None):
        receipt = OutgoingReceiptProtocolEntity(message.getId(), message.getTo(), read)
        self.stack.send(receipt)
        self.assertEqualLower(receipt)
        return receipt

    def receive_message(self, content="Received message"):
        msg_content = "Received message"
        msg_jid = "bbb@s.whatsapp.net"
        msg = TextMessageProtocolEntity(msg_content, _from=msg_jid)
        self.stack.receive(msg)
        self.assertEqualUpper(msg)
        return msg

    def receive_ack(self, message):
        ack = IncomingAckProtocolEntity(message.getId(), "message", message.getTo(), str(int(time.time())))
        self.stack.receive(ack)
        self.assertEqualUpper(ack)
        return ack

    def receive_receipt(self, message, read=False, items=None):
        receipt = IncomingReceiptProtocolEntity(message.getId(), message.getTo(), str(int(time.time())), items=items)
        if read:
            receipt.type = "read"
        self.stack.receive(receipt)
        self.assertEqualUpper(receipt)
        return receipt

    def connection_success(self):
        attributes = {
            "status": "active",
            "kind": "free",
            "creation": "1234",
            "expiration": "1446578937",
            "props": "2",
            "t": "1415470561"
        }
        success_protocol_entity = SuccessProtocolEntity(**attributes)
        self.stack.receive(success_protocol_entity)

    def get_message_state(self, message_gen_id):
        from yowlayer_store.models.messages import MessageState
        message = self.storage_layer.get_message_by_gen_id(message_gen_id)
        state = MessageState.objects.get(message=message).state
        return state

    def test_incoming_ack(self):
        message = self.send_message()
        self.receive_ack(message)
        self.assertEqual(self.get_message_state(message.getId()), MessageState.SENT)

    def test_incoming_receipt(self):
        message = self.send_message()
        self.receive_ack(message)
        self.receive_receipt(message)
        self.assertEqual(self.get_message_state(message.getId()), MessageState.SENT_DELIVERED)
        self.receive_receipt(message, read=True)
        self.assertEqual(self.get_message_state(message.getId()), MessageState.SENT_READ)

    def test_incoming_receipt_multi(self):
        messages = [self.send_message(), self.send_message(), self.send_message()]
        # get acks
        for message in messages:
            self.receive_ack(message)

        # get receipt
        receipt = self.receive_receipt(message, items=[message.getId() for message in messages])
        self.assertEqual(receipt.items, [message.getId() for message in messages])
        # check
        for message in messages:
            state = self.get_message_state(message.getId())
            self.assertEqual(state, MessageState.SENT_DELIVERED)

        self.receive_receipt(message, read=True, items=[message.getId() for message in messages])
        self.assertEqual(receipt.items, [message.getId() for message in messages])
        for message in messages:
            state = self.get_message_state(message.getId())
            self.assertEqual(state, MessageState.SENT_READ)

    def test_outgoing_text_messages(self):
        from yowlayer_store.models.messages import MessageState
        msg = self.send_message()
        message = self.storage_layer.get_messages(msg.getTo(), limit=1)[0]
        self.assertEqual(message.content, msg.getBody())
        self.assertEqual(message.conversation.contact.jid, msg.getTo())
        self.assertEqual(MessageState.objects.get(message=message).state, MessageState.SENT_QUEUED)

    def test_incoming_message_receipts(self):
        from yowlayer_store.models.messages import MessageState
        message = self.receive_message()
        self.assertEqual(self.get_message_state(message.getId()), MessageState.RECEIVED)
        self.send_receipt(message)
        self.assertEqual(self.get_message_state(message.getId()), MessageState.RECEIVED_REMOTE)
        self.send_receipt(message, read=True)
        self.assertEqual(self.get_message_state(message.getId()), MessageState.RECEIVED_READ_REMOTE)

    def test_incoming_text_message(self):
        from yowlayer_store.models.messages import Message, MessageState
        msg = self.receive_message()
        self.send_receipt(msg)
        message = Message.objects.get(id_gen=msg.getId())
        self.assertEqual(message.content, msg.getBody())
        self.assertEqual(message.conversation.contact.jid, msg.getFrom())
        self.assertEqual(MessageState.objects.get(message=message).state, MessageState.RECEIVED_REMOTE)
        self.send_receipt(msg, read=True)
        state = MessageState.objects.get(message=message).state
        self.assertEqual(state, MessageState.RECEIVED_READ_REMOTE)

    def test_contacts_sync(self):
        from yowlayer_store.models.contacts import Contact
        in_numbers = {
            "492743103668": "492743103668@s.whatsapp.net",
            "4915225256022": "4915225256022@s.whatsapp.net"
        }
        get_sync_protocol_entity = GetSyncIqProtocolEntity([in_numbers.keys()])
        self.stack.send(get_sync_protocol_entity)
        self.assertEqualLower(get_sync_protocol_entity)
        out_numbers = {}
        invalid_numbers = []
        result_sync = ResultSyncIqProtocolEntity(get_sync_protocol_entity.getId(), "1.2341", "0",
        True, "12345", in_numbers, out_numbers, invalid_numbers)
        self.stack.receive(result_sync)
        self.assertEqualUpper(result_sync)
        for number, jid in in_numbers.items():
            Contact.objects.get(jid=jid, number=number)
        # get by number
        first_contact_jid = six.next(six.itervalues(in_numbers))
        first_contact_number = first_contact_jid.split('@')[0]
        contact = self.storage_layer.get_contact(first_contact_number)
        self.assertTrue(contact is not None)
        self.assertEqual(contact["jid"], first_contact_jid)
        contact = self.storage_layer.get_contact(first_contact_jid)
        self.assertTrue(contact is not None)
        self.assertEqual(contact["number"], first_contact_number)

    def test_get_unread_messages(self):
        message1 = self.receive_message()
        message2 = self.receive_message()
        self.send_receipt(message1)
        self.send_receipt(message2)
        unread_ids = [m["id"] for m in self.storage_layer.get_unread_received_messages(message1.getFrom())]
        self.assertEqual(len(unread_ids), 2)
        self.assertTrue(message1.getId() in unread_ids)
        self.assertTrue(message2.getId() in unread_ids)
        self.send_receipt(message1, True)
        self.send_receipt(message2, True)

    def test_unacked_sent_messages(self):
        message1 = self.send_message("Message 1")
        message2 = self.send_message("Message 2")
        self.assertEqual(MessageState.SENT_QUEUED, self.get_message_state(message1.getId()))
        self.assertEqual(MessageState.SENT_QUEUED, self.get_message_state(message2.getId()))
        self.connection_success()
        self.assertEqual(message2.getId(), self.dummy_bottom_layer.lower_sink.pop().getId())
        self.assertEqual(message1.getId(), self.dummy_bottom_layer.lower_sink.pop().getId())
        self.assertEqual(MessageState.SENT, self.get_message_state(message1.getId()))
        self.assertEqual(MessageState.SENT, self.get_message_state(message2.getId()))

    def test_unacked_received_messages(self):
        message1 = self.receive_message("Message 1")
        message2 = self.receive_message("Message 2")
        self.assertEqual(MessageState.RECEIVED, self.get_message_state(message1.getId()))
        self.assertEqual(MessageState.RECEIVED, self.get_message_state(message2.getId()))
        self.connection_success()
        self.assertEqual(MessageState.RECEIVED_REMOTE, self.get_message_state(message1.getId()))
        self.assertEqual(MessageState.RECEIVED_REMOTE, self.get_message_state(message2.getId()))
        self.assertEqual([message1.getId(), message2.getId()],
                         self.dummy_bottom_layer.lower_sink.pop().getMessageIds())
