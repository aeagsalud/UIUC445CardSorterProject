import cv2
import os
import time
import numpy as np

from smbus import SMBus

# Initialize I2C
addr = 0x55         # bus address
bus = SMBus(1)      # indicates /dev/ic2-1

time.sleep(1)

# Initialize openCV
path = 'ImagesQuery'
images = []
cardNames = []
myList = os.listdir(path)
orb = cv2.ORB_create(nfeatures=1000)

# Import images
for card in myList:
    curImg = cv2.imread(f'{path}/{card}', 0)
    images.append(curImg)
    cardNames.append(os.path.splitext(card)[0])

# Function to get descriptors
def findDes(images):
    desList = []
    for img in images:
        kp,des = orb.detectAndCompute(img,None)     # Get keypoints and descriptors
        desList.append(des)
    return desList

# Function to find the card id by comparing descriptors
def findID(img, desList, thresh):
    kp2, des2 = orb.detectAndCompute(img,None)
    bf = cv2.BFMatcher()
    matchList = []
    finalIdx = -1
    try:
        for des1 in desList:
            matches = bf.knnMatch(des1, des2, k=2)
            good = []
            for m,n in matches:
                if m.distance < 0.75 * n.distance:
                    good.append([m])
            matchList.append(len(good))
    except:
        pass
    if len(matchList) != 0:
        if max(matchList) > thresh:
            finalIdx = matchList.index(max(matchList))
    return finalIdx

desList = findDes(images)

# Get camera feed and process
cap = cv2.VideoCapture(-1)
while True:
    ret, img2 = cap.read()
    imgOriginal = img2.copy()
    img2 = cv2.cvtColor(img2,cv2.COLOR_BGR2GRAY)        # Converts image to grayscale

    id = findID(img2, desList, 14)
    if id != -1:
        cv2.putText(imgOriginal, cardNames[id], (50,50), cv2.FONT_HERSHEY_COMPLEX, 1, (0,0,255), 2)
        for char in cardNames[id]:
            bus.write_byte(addr, ord(char))

    cv2.imshow('frame', imgOriginal)
    cv2.waitKey(1)

cap.release()
cv2.destroyAllWindows()
