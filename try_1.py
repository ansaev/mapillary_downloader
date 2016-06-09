import numpy
import cv2


def minus_background_white(img, background):
    rows = len(img)
    columns = len(img[0])
    img_res = img.copy()
    for i in xrange(rows):
        for j in xrange(columns):
            if background[i][j] > 100:
                img_res[i][j] = 0
    return img_res

def minus_background_black(img, background):
    rows = len(img)
    columns = len(img[0])
    img_res = img.copy()
    for i in xrange(rows):
        for j in xrange(columns):
            if background[i][j] < 200:
                img_res[i][j] = 0
    return img_res


def count_length(point1, point2):
    return ((point2[0]-point1[0])**2+(point2[1]-point1[1])**2)**0.5

def detect_blur(contour, grey_img):
    rect = cv2.minAreaRect(contour)
    box = cv2.boxPoints(rect)
    box = numpy.int0(box)
    # count area sides
    width=rect[1][0]
    height=rect[1][1]
    # calculate ratio
    if width == 0 or height == 0:
        ratio = 0
    else:
        ratio = width/height if width > height else height/width
    if not (1.5 < ratio < 7):
        return numpy.array([box]), False
    # square of rectangle
    square = int(width*height)
    if not (6000 > square > 500):
        return numpy.array([box]), False
    # laplacian
    xs = [box[i][0] for i in xrange(len(box))]
    ys = [box[i][1] for i in xrange(len(box))]
    block = grey_img[min(ys):max(ys), min(xs):max(xs)]
    laplacian = cv2.Laplacian(block, cv2.CV_64F)
    if laplacian is None:
        return numpy.array([box]), False
    val = laplacian.var()
    if not (140 > val):
        return numpy.array([box]), False
    # orientaion
    x_len = max(xs) - min(xs)
    y_len = max(ys) - min(ys)
    if y_len > x_len:
        return numpy.array([box]), False
    # ortagonality
    xdif_1 = box[0][0] - box[1][0] if box[0][0] > box[1][0] else box[1][0] - box[0][0]
    ydif_1 = box[0][1] - box[1][1] if box[0][1] > box[1][1] else box[1][1] - box[0][1]

    xdif_2 = box[1][0] - box[2][0] if box[1][0] > box[2][0] else box[2][0] - box[1][0]
    ydif_2 = box[1][1] - box[2][1] if box[1][1] > box[2][1] else box[2][1] - box[1][1]
    afordable_diff = 5
    if xdif_1 > ydif_1:
        if ydif_1 > afordable_diff:
            return numpy.array([box]), False
    elif xdif_1 > afordable_diff:
            return numpy.array([box]), False

    if xdif_2 > ydif_2:
        if ydif_2 > afordable_diff:
            return numpy.array([box]), False
    elif xdif_2 > afordable_diff:
            return numpy.array([box]), False

    # include in blure areas
    print('laplacian: '+str(val))
    print('rect' , rect,'square', square, 'ratio', ratio,'points', len(contour))
    print('box' , box)
    return numpy.array([box]), True


def find_blur(img):
    image_src = img.copy()
    # make img grey
    grey_img = cv2.cvtColor(image_src, cv2.COLOR_BGR2GRAY)
    # delete sky and light objects
    blur_1=cv2.GaussianBlur(grey_img,(5,5),22)
    adaptive_1 = cv2.adaptiveThreshold(blur_1, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 2241, -21)
    se_1=cv2.getStructuringElement(cv2.MORPH_RECT,(23,5))
    closing_1=cv2.morphologyEx(adaptive_1, cv2.MORPH_CLOSE, se_1)
    minus_1 = minus_background_white(grey_img, closing_1)
    # delete black background from grey img
    adaptive_2 = cv2.adaptiveThreshold(blur_1, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 1111, 22)
    minus_2 = minus_background_black(minus_1, adaptive_2)
    # prepera new img for detection
    adaptive_search = cv2.adaptiveThreshold(minus_2, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 211, -11) # 5
    # detect counturs
    image, contours, hierarchy = cv2.findContours(adaptive_search, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    pass_contours = []
    rejected_conturs = []
    for contour in contours:
        box, is_blury = detect_blur(contour, grey_img)
        if is_blury:
            pass_contours.append(box)
        else:
            rejected_conturs.append(box)
    # draw contours
    cv2.drawContours(image_src, pass_contours, -1, (0,255,0), 0)
    cv2.drawContours(image_src, rejected_conturs, -1, (0,0,255), 0)
    return image_src

for i in range(8)[1:]:
    # read img
    name = str(i) + '.jpg'
    print(name)
    img = cv2.imread(name)
    new_img = find_blur(img)
    cv2.imshow('conturs ' + name, new_img)
cv2.waitKey(0)
cv2.destroyAllWindows()
