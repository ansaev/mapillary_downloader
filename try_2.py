# find and download images with blur
# find some response_json
import json
import os
import requests
from config import config, DOWNLOAD_SEQUENCES_PATH

def save_blury_data(response_json):
    for item in response_json:
        data = item['b']['blurs']
        if len(data) < 1:
            continue
        # filter only big blurs
        valid_data = False
        for id in xrange(len(data)):
            box = [
                [int(data[id]['rect'][2]*X_RES), int(data[id]['rect'][3]*Y_RES)],
                [int(data[id]['rect'][0]*X_RES), int(data[id]['rect'][3]*Y_RES)],
                [int(data[id]['rect'][0]*X_RES), int(data[id]['rect'][1]*Y_RES)],
                [int(data[id]['rect'][2]*X_RES), int(data[id]['rect'][1]*Y_RES)],
            ]
            square = (box[0][0] - box[1][0]) * (box[1][1] - box[2][1])
            data[id]['box'] = box
            data[id]['square'] = square
            if square/SQUARE > PRCNT:
                valid_data = True
        if not valid_data:
            continue
        # save_img
        img_responce = requests.get(url='http://d1cuyjsrcm0gby.cloudfront.net/%s/thumb-2048.jpg' % item['key'])
        if not img_responce._content:
            continue
        with open(DIRECTORY + '/' + item['key'] + 'jpg', 'wb') as file:
            file.write(img_responce._content)
        with open(DIRECTORY + '/' + item['key'], 'w') as file:
            file.write(json.dumps(data))


X_RES = 2048
Y_RES = 1536
SQUARE = X_RES * Y_RES
PRCNT = 0.002
DIRECTORY = DOWNLOAD_SEQUENCES_PATH + 'blury_images'
try:
    os.makedirs(DIRECTORY)
except OSError:
    pass
images_num = 100
responce = requests.get('https://a.mapillary.com/v2/search/b', params={
    'limit': images_num,
    'page': 0,
    'client_id': config['CLIENT_ID']
})
response_json = responce.json()['bs']
print('response_json', responce.url, len(response_json))
save_blury_data(response_json)





