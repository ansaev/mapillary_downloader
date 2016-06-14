import json
import os
import numpy
import cv2

from try_1 import process_img

IMAGES_DIRECTORY = '/home/ansaev/repos/mapillary_downloader/downloads/blury_images/'
files  = os.listdir(IMAGES_DIRECTORY)
images = [f for f in files if f[-4:] == '.jpg']
images = images[:3]
print(images)
for im in images:
    img = cv2.imread(IMAGES_DIRECTORY + im)
    with open(IMAGES_DIRECTORY + im[:-4] + '.json', 'r') as file:
        data = file.readline()
    data = json.loads(data)
    grey_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    evaluation_data = [d ['box'] for d in data]
    new_img = process_img(img, data=evaluation_data)
    # cv2.imshow(im, new_img)
cv2.waitKey(0)
cv2.destroyAllWindows()

