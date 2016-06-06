import numpy
import cv2

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
            val = val = cv2.Laplacian(block, cv2.CV_64F).var()
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
    cv2.imshow('adaptive_'+str(trashhold), adaptive)

    minus_img = apply_img.copy()
    row_len = len(adaptive)
    column_length = len(adaptive[0])
    for row_i in xrange(row_len):
        for column_i in xrange(column_length):
            minus_img[row_i][column_i] = minus_img[row_i][column_i] if adaptive[row_i][column_i] < 200 else 0
    return minus_img

def minus_trshhold_black(grey_img, trashhold, param2):
    adaptive = cv2.adaptiveThreshold(grey_img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, trashhold, param2)
    cv2.imshow('adaptive_'+str(trashhold), adaptive)

    minus_img = grey_img.copy()
    row_len = len(adaptive)
    column_length = len(adaptive[0])
    for row_i in xrange(row_len):
        for column_i in xrange(column_length):
            minus_img[row_i][column_i] = minus_img[row_i][column_i] if adaptive[row_i][column_i] > 200 else 0
    return minus_img

# read img
image_src = cv2.imread('6.jpg')
# make img grey
grey_img = cv2.cvtColor(image_src, cv2.COLOR_BGR2GRAY)
cv2.imshow('grey_img', grey_img)

# minus black background
minus_img = minus_trshhold_black(grey_img=grey_img,trashhold=221, param2=-5)
# cv2.imshow('minus_img', minus_img)

# minus from already modifyid image white background from grey image
minus_img2 = minus_trshhold_white(grey_img=grey_img, apply_img=minus_img, trashhold=4401, param2=-15)
cv2.imshow('minus_img 2', minus_img2)

# minus from already modifyid image white background from grey image
minus_img3 = minus_trshhold_white(grey_img=minus_img2, trashhold=323, param2=-45)
cv2.imshow('minus_img 3', minus_img3)

# invert
# for rowi in xrange(len(minus_img)):
#     for columni in xrange(len(minus_img[0])):
#         minus_img[rowi][columni] = minus_img[rowi][columni] if minus_img[rowi][columni] > 5 else 255
# cv2.imshow('minus_img 1 invert', minus_img)

# # count laplaciion factor
# laplacian_calues_img = find_bad_blur(image=minus_img, row_len=4, cell_len=4)
# cv2.imshow('laplacian_calues_img', laplacian_calues_img)

# minus_img2 = minus_trshhold(grey_img=minus_img,trashhold=999)

# img_th = cv2.adaptiveThreshold(minus_img2,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,11,2)
# image, contours, hierarchy = cv2.findContours(img_th, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
# cv2.drawContours(image_src, contours, -1, (0,255,255), 0)
# cv2.imshow('image_src conturs', image_src)
# cv2.drawContours(image, contours, -1, (0,255,255), 0)

# find_blur(minus_img2, 20, 100, 8)

cv2.waitKey(0)
cv2.destroyAllWindows()




