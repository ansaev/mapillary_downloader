import os

import requests
from config import config, DOWNLOAD_SEQUENCES_PATH
import json
import sys

X_RES = 2048
Y_RES = 1536
SQUARE = X_RES * Y_RES
PRCNT = 0.02
DIRECTORY = DOWNLOAD_SEQUENCES_PATH + 'blury_images'
try:
    os.makedirs(DIRECTORY)
except OSError:
    pass

def validate_img(item):
    data = item.get('bs', [])
    if len(data) < 1:
        return False, None
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
        if float(square)/float(SQUARE) > float(PRCNT):
            valid_data = True
    if not valid_data:
        return False, None
    else:
        return True, data

def download_img(key):
    # get blur data
    blur_response = requests.get('https://a.mapillary.com/v2/im/%s/b' % key, params={
            'client_id': config['CLIENT_ID'],
        })
    blur_json = blur_response.json()
    valid, blur_data = validate_img(blur_json)
    if not valid:
        return False
    # save img
    img_responce = requests.get(url='http://d1cuyjsrcm0gby.cloudfront.net/%s/thumb-2048.jpg' % key)
    if not img_responce._content:
        return False
    with open(DIRECTORY + '/' + key + 'jpg', 'wb') as file:
        file.write(img_responce._content)
        # save_blur data
    with open(DIRECTORY + '/' + key, 'w') as file:
            file.write(json.dumps(blur_data))
    return True

def download_blury_imgs(target_number, max_lat, max_lon, min_lat, min_lon):
    current_number = 0
    page = 0
    limit = 100
    while current_number < target_number:
        responce = requests.get('https://a.mapillary.com/v2/search/im', params={
            'limit': limit,
            'page': page,
            'client_id': config['CLIENT_ID'],
            'max_lat': max_lat,
            'max_lon': max_lon,
            'min_lat': min_lat,
            'min_lon': min_lon
        })
        response_json = responce.json()
        print('response_json', responce.url, len(response_json))
        for d in response_json['ims']:
            if download_img(key=d['key']):
                current_number += 1
                print('new_img')

        if response_json['more'] is False:
            print('no_more')
            break
        page += 1

if __name__ == "__main__":
    print('max_lat, max_lon, min_lat, min_lon', sys.argv[1:])
    download_blury_imgs(100, *sys.argv[1:])