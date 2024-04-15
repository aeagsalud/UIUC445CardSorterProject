import cv2
import os
import time
import numpy as np

from smbus import SMBus

# Initialize Dictionary
color_ranges = {
    'red'       : [[0,30],[340,359]],
#    'orange'= [],
#    'yellow'= [],
    'green'     : [90, 180],
    'blue'      : [180,240]
#    'indigo'= [],
#    'violet'= [],
#    'purple'= [],
#    'brown' = [],
#    'white' = [54,],
#    'black' = []
}

type_ranges = {
#    'colorless' : [[33,9,71],[0,0,100]],
    'fire'      : [[8,53,100],[0,54,68]],
    'water'     : [[198,72,98],[201,79,43]],
    'lightning' : [[44,55,100],[37,75,95]],
    'grass'     : [[109,52,66],[147,86,68]],
    'fighting'  : [[17,70,92],[22,55,56]],
    'psychic'   : [[276,18,84],[292,48,51]],
    'metal'     : [[200,1,80],[210,6,56]],
    'darkness'  : [[188,75,56],[197,24,71]],
    'dragon'    : [[45,69,52],[50,25,83]],
#    'fairy'     : [[335,45,97],[328,55,73]]
}

# Initialize I2C
addr = 0x55         # bus address
bus = SMBus(1)      # indicates /dev/ic2-1

time.sleep(1)

# Initialize openCV
path = 'ImagesQuery'
images = []
cardNames = []
orig_images = []
myList = os.listdir(path)
orb = cv2.ORB_create(nfeatures=1000)

# Import images
for card in myList:
    curImg = cv2.imread(f'{path}/{card}', 0) # '0' means grayscale
    images.append(curImg)
    origImg = cv2.imread(f'{path}/{card}', -1)
    orig_images.append(origImg)
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

def findTypeColor(id):
    Cur_img = orig_images[id]
    hsv_img = cv2.cvtColor(Cur_img, cv2.COLOR_BGR2HSV)
    x, y = 680,80
    h, s, v = hsv_img[y,x]
    
    # openCV uses different ranges, so convert to "normal" values
    h_norm = int(h * 360/179)
    s_norm = int(s * 100/255)
    v_norm = int(v * 100/255)
    
    # Iterate through type dictionary
    for key in type_ranges:
        type_HSV0 = type_ranges[key][0]
        type_HSV1 = type_ranges[key][1]
        
        lowerH = min(type_HSV0[0], type_HSV1[0])
        upperH = max(type_HSV0[0], type_HSV1[0])
        
        if 0 <= s_norm <= 10:
            return "normal"
        if lowerH <= h_norm <= upperH:
            return key

def findPromColor(id):
    Cur_img = orig_images[id]
    hsv_img = cv2.cvtColor(Cur_img, cv2.COLOR_BGR2HSV)
    x, y = 680,80
    h, s, v = hsv_img[y,x]
    
    # openCV uses different ranges, so convert to "normal" values
    h_norm = int(h * 360/179)
    s_norm = int(s * 100/255)
    v_norm = int(v * 100/255)
    
    # Check for saturation
    if 0 <= s_norm <= 10:
        return 'other'
    
    # Check each color with hue
    if 0 <= h_norm <= 30:
        return 'red'
    if 340 <= h_norm <= 359:
        return 'red'
    if 90 <= h_norm <= 180:
        return 'green'
    if 180 <= h_norm <= 240:
        return 'blue'
    else:
        return 'other'

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
        cardType = findTypeColor(id)
        cardColor = findPromColor(id)
        cv2.putText(imgOriginal, cardType, (50,70), cv2.FONT_HERSHEY_COMPLEX, 1, (0,0,255), 2)
        cv2.putText(imgOriginal, cardColor, (50,90), cv2.FONT_HERSHEY_COMPLEX, 1, (0,0,255), 2)
        #for char in cardNames[id]:
            #bus.write_byte(addr, ord(char))
        bus.write_byte(addr, ord(cardColor[0]))
    
    cv2.imshow('frame', imgOriginal)
    cv2.waitKey(3)

cap.release()
cv2.destroyAllWindows()
