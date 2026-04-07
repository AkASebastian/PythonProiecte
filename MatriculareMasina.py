#Numar Inmatriculare
import cv2
import imutils
import numpy as np
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Users\Student\AppData\Local\Tesseract-OCR\tesseract.exe'
img = cv2.imread(r'C:\Users\Student\Desktop\HolteaSebastian\image.png')
img = cv2.resize(img, (800, 600))
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
#cv2.imshow('GRAY SCALE IMAGE', gray)
gray = cv2.bilateralFilter(gray, 13, 15, 15)
#cv2.imshow('Imagine filtrata', gray)
edged = cv2.Canny(gray, 30, 200)
#cv2.imshow('Canny', edged)
contur = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
contur = imutils.grab_contours(contur)
contur = sorted(contur, key = cv2.contourArea, reverse = True)[:10]
screenCnt = None 
for c in contur:
    peri = cv2.arcLength(c,True)
    approx= cv2.approxPolyDP(c, 0.018 * peri, True)
    if (len(approx) == 4):
        screenCnt = approx
        break
if screenCnt is None:
    detected = 0 
    print ("NU AM GASIT NICIUN CONTUR")
else:
     detected = 1
#print ("A fost detectat un nr de: ", detected)
mask = np.zeros(gray.shape,np.uint8)
new_image = cv2.drawContours(mask,[screenCnt],0,255,-1,)
new_image = cv2.bitwise_and(img,img,mask=mask)
#cv2.imshow('Contour', new_image)
(x, y) = np.where(mask == 255)
(topx, topy) = (np.min(x),np.min(y))
(bottomx,bottomy) = (np.max(x), np.max(y))
Crop = gray[topx:bottomx+1, topy:bottomy+1]
text_numar = pytesseract.image_to_string(Crop,config='--psm 10')
print("Numarul de inmatriculare detectat este: ",text_numar)
img = cv2.resize(img,(500,300))
Crop = cv2.resize(Crop,(400,200))
cv2.imshow('Crop',Crop)
cv2.waitKey(0)
cv2.destroyAllWindows()
