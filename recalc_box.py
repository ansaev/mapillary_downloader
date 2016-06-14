import json
import os
import numpy
import cv2

IMAGES_DIRECTORY = '/home/ansaev/repos/mapillary_downloader/downloads/blury_images/'
files  = os.listdir(IMAGES_DIRECTORY)
images = [f for f in files if f[-3:] == 'jpg']
print(images)
for im in images:
    try:
        img = cv2.imread(IMAGES_DIRECTORY + im)
        grey_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        with open(IMAGES_DIRECTORY + im[:-4] + '.json', 'r') as file:
            data = file.readline()
        data = json.loads(data)
        X_RES = len(img[0])
        Y_RES = len(grey_img)
        contours = []
        for id in xrange(len(data)):
            box = [
                [int(data[id]['rect'][0] * X_RES), int(data[id]['rect'][1] * Y_RES)],
                [int(data[id]['rect'][2] * X_RES), int(data[id]['rect'][1] * Y_RES)],
                [int(data[id]['rect'][2] * X_RES), int(data[id]['rect'][3] * Y_RES)],
                [int(data[id]['rect'][0] * X_RES), int(data[id]['rect'][3] * Y_RES)]
            ]
            data[id]['box'] = box

        with open(IMAGES_DIRECTORY + im[:-4]+'.json', 'w') as file:
            file.write(json.dumps(data))
    except BaseException as e:
        print str(e)




