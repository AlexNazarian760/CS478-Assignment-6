import pytesseract
from pytesseract import Output
import cv2
import numpy as np
from matplotlib import pyplot as plt
import time
from collections import namedtuple
import re
import json
import sys

class Receipt_reader:
    def __init__(self):
        self.market_info = []
        self.title = ""
        self.product = []
        self.price = []
        self.total = ""
        self.subtotal = ""
        self.random = []
        self.tax = ""

    def ticket_reader(self,filename):
        img = cv2.imread(filename)
        scale_percent = 200 # percent of original size
        width = int(img.shape[1] * scale_percent / 100)
        height = int(img.shape[0] * scale_percent / 100)
        dim = (width, height)
        img = cv2.resize(img, dim, interpolation = cv2.INTER_AREA)
        d = pytesseract.image_to_data(img, output_type=Output.DICT)
        n_boxes = len(d['level'])
        for i in range(n_boxes):
            (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])    
        ret,thresh1 = cv2.threshold(img,210,255,cv2.THRESH_BINARY)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (5, 5), 0)
        thresh = cv2.adaptiveThreshold(gray,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV,11,30)
        extracted_text = pytesseract.image_to_string(img)
        return(extracted_text)

    def parser(self,text):
        textList = text.split('\n')
        self.title = textList[0]
        product_done = False
        stop_product = False
        tt_done = False

        for line in textList:
            line = line.strip()
            if re.match("SUBTOTAL|TOTAL|TAX|tax|subtotal|total|Tax|Total|Subtotal", line) and stop_product == False:
                stop_product = True
            elif re.match("[A-z]*.* \d*\.\d*", line) and stop_product == False:
                match = re.search("\d*\.\d*", line).group()
                product = line.split(match)
                self.product.append(product[0])
                self.price.append(match)
                product_done = True
            elif re.match("SUBTOTAL|subtotal|Subtotal", line):
                self.subtotal = re.search("\d*\.\d*", line).group()
                tt_done = True
            elif re.match("TOTAL|total|Total", line):
                self.total = re.search("\d*\.\d*", line).group()
                tt_done = True
            elif re.match("TAX|tax|Tax", line):
                self.tax = re.search("\d*\.\d*", line).group()
                tt_done = True
            elif tt_done == True and line and line != "" :
                self.random.append(line)
            elif line != textList[0] and product_done == True and tt_done == True and line and line != "":
                self.market_info.append(line)
        
    def jsonProduct(self,name,price):
        result = {}
        result["Name"] = name
        result["Price"] = price
        return(result)

    def toJson(self):
        company = {"name" : self.title}
        for i, elem in enumerate(self.market_info):
            company["Info " + str(i) ] = elem
        i = 0
        product = {}
        while i < len(self.price):
            product["Product" + str(i)] = self.jsonProduct(self.product[i],self.price[i])
            i +=1
        if self.subtotal != "":
            product["Subtotal"] = self.subtotal
        if self.total != "":
            product["Total"] = self.total
        if self.tax != "":
            product["Tax"] = self.tax
        i = 0
        infos = {}
        for i, elem in enumerate(self.random):
            infos["Info " + str(i) ] = elem
        receipt = {"Company" : company , "Product" : product, "Infos" : infos}
        return(receipt)

def main():
    if len(sys.argv) < 2 or sys.argv[1] == "-h":
        print("Receipt reader\nTanguy Raeymaekers - Alexander Nazarian\nUse : python3 receipt_reader.py \"file path\"")
        return()
    if len(sys.argv) == 2:
        file = sys.argv[1]
    receipReader = Receipt_reader()
    text = receipReader.ticket_reader(file)
    receipReader.parser(text)
    receipt = Receipt_reader.toJson(receipReader)
    with open("receipt.json", "w") as write_file:
        json.dump(receipt, write_file)

if __name__ == "__main__":
    main()