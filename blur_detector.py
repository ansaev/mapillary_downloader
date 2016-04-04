import numpy

import cv2
print('hi')
image_src = cv2.imread('face.jpg')
kernel = numpy.ones((5,5),numpy.float32)/10
image_src = cv2.filter2D(image_src,-1,kernel)
image = cv2.cvtColor(image_src, cv2.COLOR_BGR2GRAY)

print(len(image), len(image[0]))
row_len = 5
cell_len = 5
values = []
for row_pointer in xrange(int(len(image)/row_len)):
    for cell_pointer in xrange(int(len(image[0])/cell_len)):
        block = [[image[row_index][cell_index] for cell_index in xrange(cell_pointer*cell_len, (cell_pointer+1)*cell_len)] for row_index in xrange(row_pointer*row_len, (row_pointer+1)*row_len)]
        block = numpy.array(block)
        val = cv2.Laplacian(block, cv2.CV_64F).var()
        values.append(val)
        if  val <= 10 :
            for row_index in xrange(row_pointer*row_len, (row_pointer+1)*row_len):
                for cell_index in xrange(cell_pointer*cell_len, (cell_pointer+1)*cell_len):
                    image[row_index][cell_index] = 0
            print(val)
print(' face img min value', min(values))
cv2.imshow('image', image)
cv2.waitKey(0)
cv2.destroyAllWindows()

# image_src = cv2.imread('blur.jpg')
# image = cv2.cvtColor(image_src, cv2.COLOR_BGR2GRAY)
# print(len(image), len(image[0]))
# # cv2.imshow('image', image)
# # cv2.waitKey(0)
# # cv2.destroyAllWindows()
# row_len = 20
# cell_len = 20
# values = []
# for row_pointer in xrange(int(len(image)/row_len)):
#     for cell_pointer in xrange(int(len(image[0])/cell_len)):
#         block = [[image[row_index][cell_index] for cell_index in xrange(cell_pointer*cell_len, (cell_pointer+1)*cell_len)] for row_index in xrange(row_pointer*row_len, (row_pointer+1)*row_len)]
#         block = numpy.array(block)
#         val = cv2.Laplacian(block, cv2.CV_64F).var()
#         values.append(val)
#         if val < 130:
#             print(val)
# print(' blur imgmin value', min(values))
