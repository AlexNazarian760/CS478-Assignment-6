import pytesseract
from pytesseract import Output
import cv2

import cv2
import numpy as np
from matplotlib import pyplot as plt
import time


img = cv2.imread('tickts.png')
d = pytesseract.image_to_data(img, output_type=Output.DICT)
n_boxes = len(d['level'])
for i in range(n_boxes):
    (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])    
    #img = cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 2)
ret,thresh1 = cv2.threshold(img,210,255,cv2.THRESH_BINARY)
#cv2.imshow('gray',thresh1)

#cv2.imshow('img',img)
extracted_text = pytesseract.image_to_string(img)
print(extracted_text)
