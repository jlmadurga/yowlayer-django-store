from yowsup.layers import YowLayerInterface


class StorageLayerInterface(YowLayerInterface):

    def get_contact(self, jid_or_number):
        contact = self._layer.get_contact(jid_or_number)
        if contact:
            return contact.to_dict()

    def get_contacts(self):
        return [contact.to_dict() for contact in self._layer.get_contacts()]

    def is_contact(self, jid_or_number):
        return self.get_contact(jid_or_number) is not None

    def add_contact(self, jid_or_number):
        return self._layer.add_contact(jid_or_number).to_dict()

    def get_unread_received_messages(self, jid_or_number):
        return [message.to_dict() for message in self._layer.get_unread_received_messages(jid_or_number)]

    def get_unacked_received_messages(self, jid_or_number=None):
        return [message.to_dict() for message in self._layer.get_unacked_received_messages(jid_or_number)]

    def get_messages(self, jid, offset=0, limit=30):
        return self._layer.get_messages(jid, offset, limit)

    def get_message_by_gen_id(self, id_gen):
        return self._layer.get_message_by_gen_id(id_gen)

    def get_conversation(self, jid):
        return self._layer.get_conversation(jid)

    def reset(self):
        self._layer.reset()
