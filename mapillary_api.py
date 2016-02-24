from tornado.httpclient import AsyncHTTPClient



class MapillaryApi(object):
    MAPIllARY_URL = 'http://api.mapillary.com/v1/'
    SEQUENCE_PATH = 's/'
    def __init__(self):
        pass

    @staticmethod
    def get_sequence(sequence_id, handler):
        url = MapillaryApi.MAPIllARY_URL+MapillaryApi.SEQUENCE_PATH+sequence_id
        req = AsyncHTTPClient()
        req.fetch(url, callback=handler)


