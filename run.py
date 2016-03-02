import tornado.ioloop
import tornado.web
import json
import os
from mapillary_api import MapillaryApi
from tornado import gen

DOWNLOAD_SEQUENCES_PATH = 'downloads/'
IMAGE_EXTENSION = ".jpg"


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
        try:
            os.makedirs(dir_path)
        except OSError:
            pass
        image_count = 0
        for image_key_info in json_response['map_images']:
            # write info in file
            image_info_path = dir_path + str(image_count)
            image_path = dir_path + str(image_count) + IMAGE_EXTENSION
            image_info_response = yield MapillaryApi.get_image_info(image_id=image_key_info['key'])
            with open(image_info_path, "w") as f:
                f.write(image_info_response.body)
            # download image
            image_file_response = yield MapillaryApi.get_image(image_key_info['key'])
            with open(image_path, "w") as f:
                f.write(image_file_response.body)
            image_count += 1
        self.write("all done!")


def make_app():
    return tornado.web.Application([
        (r"/sequence/(\w+)", SequenceHandler),
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()