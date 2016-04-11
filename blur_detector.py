import numpy
import cv2

def find_bad_blur(image, row_len, cell_len):
    values = []
    image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    for row_pointer in xrange(int(len(image)/row_len)):
        for cell_pointer in xrange(int(len(image[0])/cell_len)):
            block = [[image[row_index][cell_index] for cell_index in xrange(cell_pointer*cell_len, (cell_pointer+1)*cell_len)] for row_index in xrange(row_pointer*row_len, (row_pointer+1)*row_len)]
            block = numpy.array(block)
            val = cv2.Laplacian(block, cv2.CV_64F).var()
            values.append(val)
            for row_index in xrange(row_pointer*row_len, (row_pointer+1)*row_len):
                for cell_index in xrange(cell_pointer*cell_len, (cell_pointer+1)*cell_len):
                    new_rep = int(val)
                    new_rep = new_rep if new_rep < 256 else 255
                    image[row_index][cell_index] = new_rep
    print(' face img min value', min(values),  max(values))
    return image

image_src = cv2.imread('face.jpg')
# grey_img = cv2.cvtColor(image_src, cv2.COLOR_BGR2GRAY)
grey_img = find_bad_blur(image=image_src, row_len=2, cell_len=2)
img_filt = cv2.GaussianBlur(grey_img,(7,7),0)
img_filt = cv2.medianBlur(img_filt,7)
img_filt = cv2.GaussianBlur(img_filt,(7,7),0)
img_filt = cv2.medianBlur(img_filt,7)
img_filt = cv2.GaussianBlur(img_filt,(7,7),0)
img_th = cv2.adaptiveThreshold(img_filt,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,11,2)
image, contours, hierarchy = cv2.findContours(img_th, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
cv2.drawContours(image_src, contours, -1, (0,255,255), 0)
cv2.imshow('save_img', image_src)
cv2.waitKey(0)
cv2.destroyAllWindows()




