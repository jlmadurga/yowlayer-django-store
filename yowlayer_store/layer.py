from yowsup.layers.interface import YowInterfaceLayer, ProtocolEntityCallback
from yowsup.layers.protocol_messages.protocolentities import MessageProtocolEntity, TextMessageProtocolEntity
from yowsup.layers.protocol_contacts.protocolentities import GetSyncIqProtocolEntity
from yowsup.layers.protocol_receipts.protocolentities import OutgoingReceiptProtocolEntity
from yowsup.layers.protocol_media.protocolentities import MediaMessageProtocolEntity
from yowlayer_store.layer_interface import StorageLayerInterface
import datetime
import logging
import time
from django.core.exceptions import ObjectDoesNotExist
from yowlayer_store.models import Message, MessageState, Contact, Conversation, Media


logger = logging.getLogger(__name__)


class YowStorageLayer(YowInterfaceLayer):
    """
    YowLayer to store all data send and received from in Yowsup
    """

    PROP_DB_PATH = "org.openwhatsapp.yowsup.prop.store.db"

    def __init__(self):
        super(YowStorageLayer, self).__init__()
        self.interface = StorageLayerInterface(self)

    def get_contacts(self):
        return Contact.objects.all()

    def get_contact(self, jid_or_number):
        try:
            if '@' in jid_or_number:
                return Contact.objects.get(jid=jid_or_number)

            return Contact.objects.get(number=jid_or_number)
        except ObjectDoesNotExist:
            return None

    def is_contact(self, jid_or_number):
        return self.get_contact(jid_or_number) is not None

    def get_messages(self, jid, offset, limit):
        conversation = self.get_conversation(jid)
        messages = Message.objects.filter(conversation=conversation)
        return messages

    def _get_jid(self, jid_or_number):
        return jid_or_number if '@' in jid_or_number else jid_or_number + "@s.whatsapp.net"

    def get_unread_received_messages(self, jid_or_number):
        jid = self._get_jid(jid_or_number)
        conversation = self.get_conversation(jid)
        messages = Message.get_by_state([MessageState.RECEIVED_REMOTE], conversation)
        return messages

    def get_unacked_received_messages(self, jid_or_number=None):
        if jid_or_number:
            jid = self._get_jid(jid_or_number)
            conversation = self.get_conversation(jid)
        else:
            conversation = None

        return Message.get_by_state([MessageState.RECEIVED], conversation)

    def get_unacked_sent_messages(self, jid_or_number=None):
        if jid_or_number:
            jid = self._get_jid(jid_or_number)
            conversation = self.get_conversation(jid)
        else:
            conversation = None

        return Message.get_by_state([MessageState.SENT_QUEUED], conversation)

    def is_group_jid(self, jid):
        return "-" in jid

    def get_conversation(self, jid):
        # TODO: get conversation from group
        contact = Contact.objects.get_or_create(jid=jid)
        conversation = Conversation.objects.get_or_create(contact=contact[0])[0]
        return conversation

    def send_receipts(self, message_list, read=False):
        receipts = {}
        for m in message_list:
            conversation = m.conversation
            if conversation.contact is not None:
                jid = conversation.contact.jid
            elif conversation.group is not None:
                jid = conversation.group.jid
            else:
                continue

            if jid not in receipts:
                receipts[jid] = []
            receipts[jid].append(m.id_gen)

        for jid, message_ids in receipts.items():
            receipt = OutgoingReceiptProtocolEntity(message_ids, jid, read=read)
            self.send_receipt(receipt)

    def send_receipt(self, outgoing_receipt_protocol_entity):
        for message_id in outgoing_receipt_protocol_entity.getMessageIds():
            try:
                message = Message.objects.get(id_gen=message_id)
                if outgoing_receipt_protocol_entity.read:
                    MessageState.set_received_read_remote(message)
                else:
                    MessageState.set_received_remote(message)

            except ObjectDoesNotExist:
                logger.warning("Sending receipt for non existent message in storage. Id: %s" % message_id)

        self.toLower(outgoing_receipt_protocol_entity)

    def get_message_by_gen_id(self, genId):
        try:
            return Message.objects.get(id_gen=genId)
        except ObjectDoesNotExist:
            logger.warning("Message with id %s does not exist" % genId)
            return None

    def store_message(self, message_protocol_entity):
        if message_protocol_entity.isOutgoing():
            conversation = self.get_conversation(message_protocol_entity.getTo())
        else:
            conversation = self.get_conversation(message_protocol_entity.getFrom())

        if message_protocol_entity.isOutgoing():
            message_gen_id = message_protocol_entity.getId()
            try:
                while True:
                    Message.objects.get(id_gen=message_gen_id)
                    message_id_dis = message_gen_id.split('-')
                    if len(message_gen_id) == 2:
                        message_id_count = int(message_id_dis[1]) + 1
                    else:
                        message_id_count = 1
                    message_gen_id = "%s-%s" % (message_id_dis[0], message_id_count)
            except ObjectDoesNotExist:
                pass

            message_protocol_entity._id = message_gen_id
        message = Message(
            id_gen=message_protocol_entity.getId(),
            conversation=conversation,
            t_sent=datetime.datetime.fromtimestamp(message_protocol_entity.getTimestamp())
        )
        if message_protocol_entity.getType() == MessageProtocolEntity.MESSAGE_TYPE_MEDIA:
            media = self.get_media(message_protocol_entity, message)
            media.save()
            message.media = media
        else:
            message.content = message_protocol_entity.getBody()
        
        if type(message.content) is bytearray:
            message.content = message.content.decode('latin-1')

        message.save()
        return message
    
    def get_media(self, media_message_protocol_entity, message):
        
        media = Media(type=media_message_protocol_entity.getMediaType(),
                      preview=media_message_protocol_entity.getPreview())
        if media_message_protocol_entity.getMediaType() in (
            MediaMessageProtocolEntity.MEDIA_TYPE_IMAGE,
            MediaMessageProtocolEntity.MEDIA_TYPE_AUDIO,
            MediaMessageProtocolEntity.MEDIA_TYPE_VIDEO
        ):
            self.set_downloadable_media_data(media_message_protocol_entity, media)
            if media_message_protocol_entity.getMediaType() != MediaMessageProtocolEntity.MEDIA_TYPE_AUDIO:
                message.content = media_message_protocol_entity.getCaption()

        elif media_message_protocol_entity.getMediaType() == MediaMessageProtocolEntity.MEDIA_TYPE_LOCATION:
            message.content = media_message_protocol_entity.getLocationName()
            self.set_location_media_data(media_message_protocol_entity, media)
        elif media_message_protocol_entity.getMediaType() == MediaMessageProtocolEntity.MEDIA_TYPE_VCARD:
            message.content = media_message_protocol_entity.getName()
            self.set_vcard_media_data(media_message_protocol_entity, media)

        return media
    
    def set_location_media_data(self, location_media_message_protocol_entity, media):
        media.remote_url = location_media_message_protocol_entity.getLocationURL()
        media.data = ";".join((location_media_message_protocol_entity.getLatitude(),
                               location_media_message_protocol_entity.getLongitude()))
        media.encoding = location_media_message_protocol_entity.encoding

    def set_vcard_media_data(self, vcard_media_message_protocol_entity, media):
        media.data = vcard_media_message_protocol_entity.getCardData()

    def set_downloadable_media_data(self, downloadable_media_message_protocol_entity, media):
        media.size = downloadable_media_message_protocol_entity.getMediaSize()
        media.remote_url = downloadable_media_message_protocol_entity.getMediaUrl()
        media.mimetype = downloadable_media_message_protocol_entity.getMimeType()
        media.filehash = downloadable_media_message_protocol_entity.fileHash
        media.filename = downloadable_media_message_protocol_entity.fileName
        media.encoding = downloadable_media_message_protocol_entity.encoding

    def store_contacts_sync_result(self, result_sync_iq_protocol_entity, original_get_sync_protocol_entity):
        for number, jid in result_sync_iq_protocol_entity.inNumbers.items():
            Contact.objects.get_or_create(number=number, jid=jid)

        self.toUpper(result_sync_iq_protocol_entity)

    def send(self, protocol_entity):
        '''
        Store what should be stored from incoming data and then forward to lower layers
        :param protocol_entity: protocol entity to send
        :return:
        '''

        if protocol_entity.__class__ == GetSyncIqProtocolEntity:
            self._sendIq(protocol_entity, self.store_contacts_sync_result)
        elif protocol_entity.__class__ == OutgoingReceiptProtocolEntity:
            if protocol_entity.read:
                for messageId in protocol_entity.getMessageIds():
                    try:
                        message = Message.objects.get(id_gen=messageId)
                        MessageState.set_received_read(message)
                    except ObjectDoesNotExist:
                        continue
            self.send_receipt(protocol_entity)
        # elif protocol_entity.__class__ == ListOutgoingReceiptProtocolEntity:
        #     if protocol_entity.read:
        #         for mId in protocol_entity.getMessageIds():
        #             message = Message.get(id_gen = mId)
        #             MessageState.set_received_read(message)
        #     self.send_receipt(protocol_entity)
        else:
            if isinstance(protocol_entity, MessageProtocolEntity):
                message = self.store_message(protocol_entity)
                MessageState.set_sent_queued(message)
            self.toLower(protocol_entity)

    @ProtocolEntityCallback("message")
    def on_message(self, message_protocol_entity):
        '''
        Store incoming messages with received state. Must afterwards send the entity to upper layers
        :param message_protocol_entity: incoming message protocol entity
        :return:
        '''
        message = self.store_message(message_protocol_entity)
        MessageState.set_received(message)
        self.toUpper(message_protocol_entity)

    @ProtocolEntityCallback("ack")
    def on_ack(self, incoming_ack_protocol_entity):
        """
        Store new state for message associated to ack. Must afterwards send the entity to upper layers
        :param incoming_ack_protocol_entity: ack entity
        :return:
        """
        if incoming_ack_protocol_entity.getClass() == "message":
            message = self.get_message_by_gen_id(incoming_ack_protocol_entity.getId())
            MessageState.set_sent(message)

        self.toUpper(incoming_ack_protocol_entity)

    @ProtocolEntityCallback("success")
    def on_success(self, success_protocol_entity):
        """
        When connected check if there are received or sent message with no ack. Send receipts for received messages
        and re send outgoing messages
        :param success_protocol_entity: entity which represents succesfull authentication/connection
        :return:
        """
        # send pending receipts
        messages = self.get_unacked_received_messages()
        if messages.count():
            self.send_receipts(messages)

        # send offline messages
        messages = self.get_unacked_sent_messages()
        for message in messages:
            # jid = message.group.jid if message.group is not None else message.contact.jid
            jid = message.conversation.contact.jid
            text_message = TextMessageProtocolEntity(message.content, message.id_gen, to=jid,
                                                     timestamp=time.mktime(message.t_sent.timetuple()))
            MessageState.set_sent(message)
            self.toLower(text_message)
        self.toUpper(success_protocol_entity)

    @ProtocolEntityCallback("receipt")
    def on_receipt(self, receipt_protocol_entity):
        '''
        Update message status to delivered or read
        :param receipt_protocol_entity:
        :return:
        '''

        ids = [receipt_protocol_entity.getId()] if receipt_protocol_entity.items is None else \
            receipt_protocol_entity.items

        for id_ in ids:
            message = self.get_message_by_gen_id(id_)
            if message:
                if not receipt_protocol_entity.getType():
                    MessageState.set_sent_delivered(message)
                elif receipt_protocol_entity.getType() == "read":
                    contact = None
                    if receipt_protocol_entity.getParticipant():
                        contact = Contact.objects.get_or_create(jid=receipt_protocol_entity.getParticipant())
                    MessageState.set_sent_read(message, contact)

        self.toUpper(receipt_protocol_entity)
