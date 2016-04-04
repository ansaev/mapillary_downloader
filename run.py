import uuid

import tornado.ioloop
import tornado.web
from tornado import gen
import tornado.websocket
from tornado.httpclient import HTTPError
import json
import os
from mapillary_api import MapillaryApi
from config import DOWNLOAD_SEQUENCES_PATH, INFO_FILE_EXTENSION, IMAGE_EXTENSION

clients = {}


class SequenceHandler(tornado.web.RequestHandler):
    def data_received(self, chunk):
        pass

    @gen.coroutine
    def get(self, sequence_id):
        assert sequence_id
        # make download directory
        try:
            os.makedirs(DOWNLOAD_SEQUENCES_PATH)
        except OSError:
            pass
        sequence_dir = DOWNLOAD_SEQUENCES_PATH+sequence_id+"/"
        sequence_info_path = DOWNLOAD_SEQUENCES_PATH + sequence_id + INFO_FILE_EXTENSION
        # save sequence info in file
        try:
            sequence_response = yield MapillaryApi.get_sequence(sequence_id=sequence_id)
            # create sequence's directory
            try:
                os.makedirs(sequence_dir)
            except OSError:
                pass
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
        # check items to download
        images_number = len(json_response.get('keys', []))
        images_to_download = 0
        image_info_to_download = 0
        for image_num in xrange(images_number):
            if not os.path.isfile(sequence_dir + str(image_num) + IMAGE_EXTENSION):
                images_to_download += 1
            if not os.path.isfile(sequence_dir + str(image_num) + INFO_FILE_EXTENSION):
                image_info_to_download += 1
        if images_to_download == 0 and image_info_to_download == 0:
            # all downloaded
            self.render('sequence_downloaded.html', sequence_id=sequence_id, items_to_download=len(json_response.get('keys', [])))
            return
        else:
            client_id = str(uuid.uuid4())
            clients[client_id] = \
                {'handler': None,
                 'images': {'downloaded': images_number - images_to_download, 'failed': 0},
                 'image_infos': {'downloaded': images_number - image_info_to_download, 'failed': 0}
                 }
            self.render('sequence_download.html', sequence_id=sequence_id,
                        images={'downloaded': images_number - images_to_download,
                                 'failed': 0,
                                 'to_download': images_number
                                 },
                        image_infos={'downloaded': images_number - image_info_to_download,
                                      'failed': 0,
                                      'to_download': images_number
                                      }
                        , client_id=client_id
                        )
        image_count = 0
        for image_key in json_response.get('keys', []):
            # set paths
            image_info_path = sequence_dir + str(image_count) + INFO_FILE_EXTENSION
            image_path = sequence_dir + str(image_count) + IMAGE_EXTENSION
            # save image info
            if not os.path.isfile(image_info_path):
                try:
                    image_info_response = yield MapillaryApi.get_image_info(image_id=image_key)
                    with open(image_info_path, "w") as f:
                        f.write(image_info_response.body)
                    clients[client_id]['image_infos']['downloaded'] += 1
                except HTTPError as image_info_error:
                    with open(image_info_path, "w") as f:
                        f.write('failed to get image info: ' + str(image_info_error) + " for the adress: " + image_info_error.response.request.url)
                    clients[client_id]['image_infos']['failed'] += 1
            # download image
            if not os.path.isfile(image_path):
                try:
                    image_file_response = yield MapillaryApi.get_image(image_id=image_key)
                    with open(image_path, "wb") as f:
                        f.write(image_file_response.body)
                    clients[client_id]['images']['downloaded'] += 1
                except HTTPError as image_error:
                    print('failed to get image: ' + str(image_error))
                    with open(image_path, "w") as f:
                        f.write('failed to get image: ' + str(image_error) + " for the adress: " + image_info_error.response.request.url)
                    clients[client_id]['images']['failed'] += 1
            image_count += 1
            if clients[client_id]['handler']:
                clients[client_id]['handler'].notify_clent()


class DownloadProgressHandler(tornado.websocket.WebSocketHandler):
    def data_received(self, chunk):
        pass

    def __init__(self, application, request, **kwargs):
        super(DownloadProgressHandler, self).__init__(application, request, **kwargs)
        self.client_id = ''

    def open(self, client_id):
        self.client_id = client_id
        clients[self.client_id]['handler'] = self

    def on_message(self, message):
        pass

    def on_close(self):
        clients[self.client_id]['handler'] = None

    def notify_clent(self):
        client_data = {'images': clients.get(self.client_id, {}).get('images', {}), 'image_infos': clients.get(self.client_id, {}).get('image_infos', {})}
        self.write_message(json.dumps(client_data))



def make_app():
    return tornado.web.Application([
        (r"/sequence/(.*)", SequenceHandler),
        (r"/download_progress/(.*)", DownloadProgressHandler),
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()