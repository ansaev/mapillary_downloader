import tornado.ioloop
import tornado.web
import json
import os
from mapillary_api import MapillaryApi
from tornado.httpclient import AsyncHTTPClient
DOWNLOAD_SEQUENCES_PATH = '/home/ansaev/repos/mapillary_downloader/downloads/'
THUMB_KEYS = ["thumb-2048", "thumb-1024", "thumb-640", "thumb-320",]


class MainHandler(tornado.web.RequestHandler):
    def get(self, sequence_id):
        assert sequence_id

        def handle_response(response):
            assert response
            json_response = json.loads(response.body)
            skey = json_response['key']
            dir_path = DOWNLOAD_SEQUENCES_PATH+skey+"/"
            try:
                os.makedirs(dir_path)
            except OSError:
                pass
            for image_info in json_response['map_images']:
                # write info in file
                with open(dir_path+image_info['key'], "w") as f:
                    f.write(json.dumps(image_info))
                # save_image
                for thumb in THUMB_KEYS:
                    if thumb in image_info['versions']:
                        path = dir_path+image_info['key']+"-"+thumb+".jpg"
                        if not os.path.isfile(path):
                            download_img(image_info['versions'][thumb], path)
                        break

            print('done')
        MapillaryApi.get_sequence(sequence_id=sequence_id, handler=handle_response)


def download_img(url, path):
    assert url, path
    req = AsyncHTTPClient()

    def handler(response):
        with open(path, "w") as f:
            f.write(response.body)

    req.fetch(url, callback=handler)


def make_app():
    return tornado.web.Application([
        (r"/sequence/(\w+)", MainHandler),
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()