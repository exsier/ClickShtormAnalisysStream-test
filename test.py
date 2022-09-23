import cv2
import numpy as np

url = 'https://img3.goodfon.ru/original/1920x1080/a/ac/les-tuman-tma.jpg'
cap = cv2.VideoCapture(url)
ret,img = cap.read()
#sav = img.copy()    

#img = sav.copy()
overlay = img.copy()
font = cv2.FONT_HERSHEY_DUPLEX
fontScale = 1
label = 'player1 vs player2'
thickness = 1
text_color = (255,255,255)
text_width, text_height = cv2.getTextSize(label, font, fontScale, thickness)
img_height, img_width, channels = overlay.shape
print(text_width, text_height)
text_coord = (20,900 + 2 * text_width[1] - 10)
cv2.rectangle(overlay, 
              (20, 900), (20 + text_width[0],  900 + 2 * text_width[1]),
              (0,0,0),
              -1)
opacity = 1
cv2.addWeighted(overlay, opacity, img, 0, 0, img)

cv2.putText(img, label, text_coord, font, fontScale, text_color,thickness)

cv2.imshow('image', img)
cv2.waitKey()
#cv2.imwrite(r'd:/temp/lena_result.jpg', img)