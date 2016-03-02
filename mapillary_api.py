from config import config
from tornado import gen
from tornado.gen import Return
from tornado.httpclient import AsyncHTTPClient
DEFAULT_IMAGE_VERSION = "thumb-2048.jpg"


class MapillaryApi(object):
    MAPIllARY_URL_V1 = 'http://api.mapillary.com/v1/'
    MAPIllARY_URL_V2 = 'https://a.mapillary.com/v2/'
    IMAGE_BANK_URL = "https://d1cuyjsrcm0gby.cloudfront.net/"
    SEQUENCE_PATH = 's/'
    IMAGE_PATH = 'im/'
    CLIENT_PARAM = "client_id"
    OBJECTS_ON_IM_PARAM = '/or'

    def __init__(self):
        pass

    @staticmethod
    @gen.coroutine
    def get_sequence(sequence_id):
        url = MapillaryApi.MAPIllARY_URL_V1 + MapillaryApi.SEQUENCE_PATH + sequence_id
        req = AsyncHTTPClient()
        out = yield req.fetch(url)
        raise Return(out)

    @staticmethod
    @gen.coroutine
    def get_image_info(image_id):
        url = MapillaryApi.MAPIllARY_URL_V2 + MapillaryApi.IMAGE_PATH + image_id + "?" \
              + MapillaryApi.CLIENT_PARAM + "=" + config['CLIENT_ID']
        req = AsyncHTTPClient()
        out = yield req.fetch(url)
        raise Return(out)

    @staticmethod
    @gen.coroutine
    def get_image_info_extra(image_id):
        url = MapillaryApi.MAPIllARY_URL_V2 + MapillaryApi.IMAGE_PATH + image_id + MapillaryApi.OBJECTS_ON_IM_PARAM\
              + "?" + MapillaryApi.CLIENT_PARAM + "=" + config['CLIENT_ID']
        req = AsyncHTTPClient()
        out = yield req.fetch(url)
        raise Return(out)

    @staticmethod
    @gen.coroutine
    def get_image(image_id, version=DEFAULT_IMAGE_VERSION):
        url = MapillaryApi.IMAGE_BANK_URL + image_id + "/" + version
        req = AsyncHTTPClient()
        out = yield req.fetch(url)
        raise Return(out)


