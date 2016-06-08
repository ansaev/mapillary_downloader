import numpy
import cv2
import matplotlib
matplotlib.rcsetup.all_backends
matplotlib.use('GTK')
from matplotlib import pyplot as plt

def find_bad_blur(image, row_len, cell_len):
    values = []
    for row_pointer in xrange(int(len(image)/row_len)):
        for cell_pointer in xrange(int(len(image[0])/cell_len)):
            block = [[image[row_index][cell_index] for cell_index in xrange(cell_pointer*cell_len, (cell_pointer+1)*cell_len)] for row_index in xrange(row_pointer*row_len, (row_pointer+1)*row_len)]
            block = numpy.array(block)
            val = numpy.max(cv2.convertScaleAbs(cv2.Laplacian(block,3)))
            values.append(val)
            for row_index in xrange(row_pointer*row_len, (row_pointer+1)*row_len):
                for cell_index in xrange(cell_pointer*cell_len, (cell_pointer+1)*cell_len):
                    new_rep = int(val)
                    new_rep = new_rep if new_rep < 256 else 255
                    image[row_index][cell_index] = new_rep
    print(' face img min value', min(values),  max(values))
    return image

def find_blur(image, row_len, cell_len, step):
    values = []
    for row_pointer in xrange(int((len(image) - row_len)/step) + 1):
        for cell_pointer in xrange(int((len(image[0]) - cell_len)/step) + 1):
            block = [[image[row_index][cell_index] for cell_index in xrange(cell_pointer*step, cell_pointer*step+cell_len)] for row_index in xrange(row_pointer*step, row_pointer*step + row_len)]
            block = numpy.array(block)
            val = cv2.Laplacian(block, cv2.CV_64F).var()
            values.append({'row_pointer': row_pointer, 'cell_pointer': cell_pointer, 'val':val})

    # search min value
    min_value = values[0]['val']
    min_values = [values[0]]
    max_value = values[0]['val']
    max_values = []
    for v in values[1:]:
        if min_value > v['val']:
            min_value = v['val']
            min_values = [v]
        elif min_value == v['val']:
            min_values.append(v)

        # if max_value < v['val']:
        #     max_value = v['val']
        #     max_values = [v]
        if 257 > v['val'] > 256:
            max_values.append(v)
    print('min_value', min_value)
    print('max_value', max_value)
    min_img = image.copy()
    max_img = image.copy()
    for v in min_values:
        row_pointer = v['row_pointer']
        cell_pointer = v['cell_pointer']
        val = v['val']
        for row_index in  xrange(row_pointer*step, row_pointer*step + row_len):
            for cell_index in xrange(cell_pointer*step, cell_pointer*step+cell_len):
                min_img[row_index][cell_index] = 255
    for v in max_values:
        row_pointer = v['row_pointer']
        cell_pointer = v['cell_pointer']
        val = v['val']
        for row_index in  xrange(row_pointer*step, row_pointer*step + row_len):
            for cell_index in xrange(cell_pointer*step, cell_pointer*step+cell_len):
                max_img[row_index][cell_index] = 255
    cv2.imshow('min laplacian', min_img)
    cv2.imshow('max_img laplacian', max_img)


    # return image

def minus_trshhold_white(grey_img, trashhold, param2, apply_img=None):
    apply_img = grey_img if apply_img is None else apply_img
    adaptive = cv2.adaptiveThreshold(grey_img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, trashhold, param2)
    # cv2.imshow('adaptive_'+str(trashhold), adaptive)

    minus_img = apply_img.copy()
    row_len = len(adaptive)
    column_length = len(adaptive[0])
    for row_i in xrange(row_len):
        for column_i in xrange(column_length):
            minus_img[row_i][column_i] = minus_img[row_i][column_i] if adaptive[row_i][column_i] < 200 else 0
    return minus_img

def minus_trshhold_black(grey_img, trashhold, param2):
    adaptive = cv2.adaptiveThreshold(grey_img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, trashhold, param2)
    # cv2.imshow('adaptive_'+str(trashhold), adaptive)

    minus_img = grey_img.copy()
    row_len = len(adaptive)
    column_length = len(adaptive[0])
    for row_i in xrange(row_len):
        for column_i in xrange(column_length):
            minus_img[row_i][column_i] = minus_img[row_i][column_i] if adaptive[row_i][column_i] > 200 else 0
    return minus_img

# read img
image_src = cv2.imread('4.jpg')
# make img grey
grey_img = cv2.cvtColor(image_src, cv2.COLOR_BGR2GRAY)
cv2.imshow('grey_img', grey_img)

# minus black background
minus_img = minus_trshhold_black(grey_img=grey_img,trashhold=221, param2=-14)
# cv2.imshow('minus_img', minus_img)

# minus from already modifyid image white background from grey image
minus_img2 = minus_trshhold_white(grey_img=grey_img, apply_img=minus_img, trashhold=4401, param2=-15)
# cv2.imshow('minus_img 2', minus_img2)

# minus from already modifyid image white background from grey image
minus_img3 = minus_trshhold_white(grey_img=minus_img2, trashhold=135, param2=-56)
# minus_img3 = minus_img2
cv2.imshow('minus_img 3', minus_img3)

image, contours, hierarchy = cv2.findContours(minus_img3, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
pass_contours = []
rejected_conturs = []

def count_length(point1, point2):
    return ((point2[0]-point1[0])**2+(point2[1]-point1[1])**2)**0.5

for contour in contours:
    rect = cv2.minAreaRect(contour)
    box = cv2.boxPoints(rect)
    box = numpy.int0(box)
    # count area sides
    a = count_length(box[0], box[1])
    b = count_length(box[1], box[2] )
    # calculate ratio
    if a == 0 or b == 0:
        ratio = 0
    else:
        ratio = b/a if b > a else a/b

    if not (1.5 < ratio < 7):
        rejected_conturs.append(contour)
        continue
    # square of rectangle
    square = int(a*b)
    if not (7000 > square > 500):
        rejected_conturs.append(contour)
        continue
    # density of rectangle
    density = float(len(contour))/float(square) if square != 0 else -1.0
    if not density > 0.09:
        rejected_conturs.append(contour)
        continue
    # lets calculate laplacian
    xs = [box[i][0] for i in xrange(len(box))]
    ys = [box[i][1] for i in xrange(len(box))]
    block = grey_img[min(ys):max(ys), min(xs):max(xs)]
    laacian = cv2.Laplacian(block, cv2.CV_64F)
    if laacian is None:
        rejected_conturs.append(contour)
        continue
    val = laacian.var()
    if val > 150:
        rejected_conturs.append(contour)
        continue
    # include in blure areas
    pass_contours.append(numpy.array([box]))
    print('laplacian: '+str(val))
    print('rect' , rect,'square', square, 'ratio', ratio,'points', len(contour), 'density', density)
    print('box' , box)
    # show iterations images
    cv2.drawContours(image_src,[box],-1,(0,255,255),0)
    window_name = 'rect: '+str(rect)
    window_name1 = 'laplacian: '+str(val)
    cv2.imshow(window_name1, block)
    cv2.imshow(window_name, image_src)
    plt.hist(block.ravel(),256,[0,256]); plt.show()
    cv2.waitKey(0)
    cv2.destroyWindow(window_name)
    cv2.destroyWindow(window_name1)



# count laplaciion factor
# laplacian_calues_img = find_bad_blur(image=grey_img, row_len=4, cell_len=4)
# cv2.imshow('laplacian_calues_img', laplacian_calues_img)

cv2.drawContours(image_src, pass_contours, -1, (0,255,0), 0)
cv2.drawContours(image_src, rejected_conturs, -1, (0,0,255), 0)
cv2.imshow('image_src conturs', image_src)
# find_blur(minus_img2, 20, 100, 8)

cv2.waitKey(0)
cv2.destroyAllWindows()




