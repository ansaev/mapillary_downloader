import tornado.ioloop
import tornado.web
import json
import os
from mapillary_api import MapillaryApi
from tornado import gen
from zipfile import *

DOWNLOAD_SEQUENCES_PATH = 'downloads/'
IMAGE_EXTENSION = ".jpg"
INFO_FILE_EXTENSION = '.json'


class SequenceHandler(tornado.web.RequestHandler):
    def data_received(self, chunk):
        pass

    @gen.coroutine
    def get(self, sequence_id):
        assert sequence_id
        sequence_response = yield MapillaryApi.get_sequence(sequence_id=sequence_id)
        json_response = json.loads(sequence_response.body)
        skey = json_response['key']
        dir_path = DOWNLOAD_SEQUENCES_PATH+skey+"/"
        # create directories if needed
        try:
            os.makedirs(dir_path)
        except OSError:
            pass
        # create zip
        zip_path = DOWNLOAD_SEQUENCES_PATH + skey + ".zip"
        if not os.path.isfile(zip_path):
            z = ZipFile(zip_path, 'w')
        else:
            z = None
        # save sequence info in file
        sequence_info_path = DOWNLOAD_SEQUENCES_PATH + skey + INFO_FILE_EXTENSION
        with open(sequence_info_path, "w") as f:
            f.write(sequence_response.body)
        image_count = 0
        for image_key in json_response['keys']:
            # write info in file
            image_info_path = dir_path + str(image_count) + INFO_FILE_EXTENSION
            image_path = dir_path + str(image_count) + IMAGE_EXTENSION
            if not os.path.isfile(image_info_path):
                image_info_response = yield MapillaryApi.get_image_info(image_id=image_key)
                z.writestr(image_info_path, image_info_response.body)
                with open(image_info_path, "w") as f:
                    f.write(image_info_response.body)
            # download image
            if not os.path.isfile(image_path):
                image_file_response = yield MapillaryApi.get_image(image_id=image_key)
                z.writestr(image_path, image_file_response.body)
                with open(image_path, "w") as f:
                    f.write(image_file_response.body)
            image_count += 1
        self.write("all done!")
        if z:
            z.close()
        self.write("<br/> zip created!")
        self.flush()
        with open(zip_path, "r") as f:
            self.write(f.read())


def make_app():
    return tornado.web.Application([
        (r"/sequence/(\w+)", SequenceHandler),
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()