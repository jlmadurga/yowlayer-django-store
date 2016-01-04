from yowsup.layers.protocol_media.protocolentities.message_media_downloadable_image import \
    ImageDownloadableMediaMessageProtocolEntity
from yowsup.layers.protocol_media.protocolentities.message_media_downloadable_audio import \
    AudioDownloadableMediaMessageProtocolEntity
from yowsup.layers.protocol_media.protocolentities.message_media_downloadable_video import \
    VideoDownloadableMediaMessageProtocolEntity
from yowsup.layers.protocol_media.protocolentities import VCardMediaMessageProtocolEntity
from yowsup.layers.protocol_media.protocolentities import LocationMediaMessageProtocolEntity

def image_downloadable_media_message_protocol_entity(to="t@s.whatsapp.net"):
    attributes = {
        "mimeType": "image/jpeg",
        "fileHash": "fhash",
        "url": "http:/google.com",
        "ip": "ip",
        "size": 1234,
        "fileName": "filename",
        "encoding": "raw",
        "height": 123,
        "width": 321,
        "caption": "CAPTN",
        "to": to               
    }
    return ImageDownloadableMediaMessageProtocolEntity(**attributes)


def audio_downloadable_media_message_protocol_entity(to="t@s.whatsapp.net"):
    attributes = {
        "mimeType": "image/jpeg",
        "fileHash": "fhash",
        "url": "http:/google.com",
        "ip": "ip",
        "size": 1234,
        "fileName": "filename",
        "encoding": "raw",
        "abitrate": "bitrate",
        "acodec": "code",
        "asampfreq": "asampfreq",
        "duration": "duration",
        "origin": "origin",
        "seconds": "seconds",
        "to": to            
    }
    return AudioDownloadableMediaMessageProtocolEntity(**attributes)

def video_downloadable_media_message_protocol_entity(to="t@s.whatsapp.net"):
    attributes = {
        "mimeType": "image/jpeg",
        "fileHash": "fhash",
        "url": "http:/google.com",
        "ip": "ip",
        "size": 1234,
        "fileName": "filename",
        "encoding": "raw",
        "abitrate": "bitrate",
        "acodec": "code",
        "caption": "CAPT",
        "asampfmt": "asampfmt",
        "asampfreq": "asampfreq",
        "duration": "duration",
        "fps": "fps",
        "width": "width",
        "height": "height",
        "seconds": "seconds",
        "vbitrate": "vbitrate",
        "vcodec": "vcodec",
        "to": to                 
    }
    return VideoDownloadableMediaMessageProtocolEntity(**attributes)


def vcard_media_message_protocol_entity(to="t@s.whatsapp.net"):
    attributes = {
        "name": "NAME",
        "card_data": "VCARD_DATA",
        "to": to
    }
    return VCardMediaMessageProtocolEntity(**attributes)

def location_media_message_protocol_entity(to="t@s.whatsapp.net"):
    attributes = {
        "to": to,
        "latitude": "LAT",
        "longitude": "LONG",
        "name": "name",
        "url": "URL",
        "encoding": "raw"
    }
    return LocationMediaMessageProtocolEntity(**attributes)
