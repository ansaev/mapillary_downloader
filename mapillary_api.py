from config import config
from tornado import gen
from tornado.gen import Return
from tornado.httpclient import AsyncHTTPClient
DEFAULT_IMAGE_VERSION = "thumb-2048.jpg"


class MapillaryApi(object):
    MAPIllARY_URL_V2 = 'https://a.mapillary.com/v2/'
    IMAGE_BANK_URL = "https://d1cuyjsrcm0gby.cloudfront.net/"
    SEQUENCE_PATH = 's/'
    IMAGE_PATH = 'im/'
    CLIENT_PARAM = "client_id"
    OBJECTS_ON_IM_PARAM = '/or'
    BLUR_INFO = '/b'
    TRYINGS = 5

    def __init__(self):
        pass

    @staticmethod
    @gen.coroutine
    def get_sequence(sequence_id):
        url = MapillaryApi.MAPIllARY_URL_V2 + MapillaryApi.SEQUENCE_PATH + sequence_id + "?" \
              + MapillaryApi.CLIENT_PARAM + "=" + config['CLIENT_ID']
        req = AsyncHTTPClient()
        out = yield req.fetch(url)
        if not(out.code is 200 or out.code is 404):
            for i in xrange(MapillaryApi.TRYINGS):
                out = yield req.fetch(url)
                if out.code is 200 or out.code is 404:
                    break
        raise Return(out)

    @staticmethod
    @gen.coroutine
    def get_image_info(image_id):
        url = MapillaryApi.MAPIllARY_URL_V2 + MapillaryApi.IMAGE_PATH + image_id + "?" \
              + MapillaryApi.CLIENT_PARAM + "=" + config['CLIENT_ID']
        req = AsyncHTTPClient()
        out = yield req.fetch(url)
        if not(out.code is 200 or out.code is 404):
            for i in xrange(MapillaryApi.TRYINGS):
                out = yield req.fetch(url)
                if out.code is 200 or out.code is 404:
                    break
        raise Return(out)

    @staticmethod
    @gen.coroutine
    def get_image_info_extra(image_id):
        url = MapillaryApi.MAPIllARY_URL_V2 + MapillaryApi.IMAGE_PATH + image_id + MapillaryApi.OBJECTS_ON_IM_PARAM\
              + "?" + MapillaryApi.CLIENT_PARAM + "=" + config['CLIENT_ID']
        req = AsyncHTTPClient()
        out = yield req.fetch(url)
        if not(out.code is 200 or out.code is 404):
            for i in xrange(MapillaryApi.TRYINGS):
                out = yield req.fetch(url)
                if out.code is 200 or out.code is 404:
                    break
        raise Return(out)

    @staticmethod
    @gen.coroutine
    def get_image_blur_info(image_id):
        url = MapillaryApi.MAPIllARY_URL_V2 + MapillaryApi.IMAGE_PATH + image_id + MapillaryApi.BLUR_INFO\
              + "?" + MapillaryApi.CLIENT_PARAM + "=" + config['CLIENT_ID']
        req = AsyncHTTPClient()
        out = yield req.fetch(url)
        if not(out.code is 200 or out.code is 404):
            for i in xrange(MapillaryApi.TRYINGS):
                out = yield req.fetch(url)
                if out.code is 200 or out.code is 404:
                    break
        raise Return(out)

    @staticmethod
    @gen.coroutine
    def get_image(image_id, version=DEFAULT_IMAGE_VERSION):
        url = MapillaryApi.IMAGE_BANK_URL + image_id + "/" + version
        req = AsyncHTTPClient()
        out = yield req.fetch(url)
        if not(out.code is 200 or out.code is 404):
            for i in xrange(MapillaryApi.TRYINGS):
                out = yield req.fetch(url)
                if out.code is 200 or out.code is 404:
                    break
        raise Return(out)


