import tornado.ioloop
import tornado.web
import json
import os
from mapillary_api import MapillaryApi
from tornado import gen
from tornado.httpclient import HTTPError

DOWNLOAD_SEQUENCES_PATH = 'downloads/'
IMAGE_EXTENSION = ".jpg"
INFO_FILE_EXTENSION = '.json'


class SequenceHandler(tornado.web.RequestHandler):
    def data_received(self, chunk):
        pass

    @gen.coroutine
    def get(self, sequence_id):
        assert sequence_id
        dir_path = DOWNLOAD_SEQUENCES_PATH+sequence_id+"/"
        sequence_info_path = DOWNLOAD_SEQUENCES_PATH + sequence_id + INFO_FILE_EXTENSION
        # create directories if needed
        try:
            os.makedirs(dir_path)
        except OSError:
            pass
        # save sequence info in file
        try:
            sequence_response = yield MapillaryApi.get_sequence(sequence_id=sequence_id)
            with open(sequence_info_path, "w") as f:
                f.write(sequence_response.body)
        except HTTPError as e:
            with open(sequence_info_path, "w") as f:
                f.write('failed to get sequence info: ' + str(e) + " for the adress: " + e.response.request.url)
            self.send_error(404)
            return
        image_count = 0
        if sequence_response:
            json_response = json.loads(sequence_response.body)
        else:
            json_response = {}
        for image_key in json_response.get('keys', []):
            # set paths
            image_info_path = dir_path + str(image_count) + INFO_FILE_EXTENSION
            image_path = dir_path + str(image_count) + IMAGE_EXTENSION
            # save image info
            if not os.path.isfile(image_info_path):
                try:
                    image_info_response = yield MapillaryApi.get_image_info(image_id=image_key)
                    with open(image_info_path, "w") as f:
                        f.write(image_info_response.body)
                except HTTPError as image_info_error:
                    with open(image_info_path, "w") as f:
                        f.write('failed to get image info: ' + str(image_info_error) + " for the adress: " + image_info_error.response.request.url)
            # download image
            if not os.path.isfile(image_path):
                try:
                    image_file_response = yield MapillaryApi.get_image(image_id=image_key)
                    with open(image_path, "wb") as f:
                        f.write(image_file_response.body)
                except HTTPError as image_error:
                    with open(image_path, "w") as f:
                        print('failed to get image: ' + str(image_error))
                        f.write('failed to get image: ' + str(image_error) + " for the adress: " + image_info_error.response.request.url)
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