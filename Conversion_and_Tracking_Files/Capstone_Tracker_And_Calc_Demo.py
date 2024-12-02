import cv2
import numpy as np
from time import time
import subprocess
from math import sqrt


import socket
import threading
uAngle = 0.0
uDist = 0.0
test = 1.1

#three sockets for github file, in practice 2 of the sockets would be commented out
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
host = "10.250.16.99"
port = 1234
client_socket.connect((host, port))
client_socket1.connect((host, 2345))
client_socket2.connect((host, 3456))

#function for angle (and distance) update from Hub that will be updated with a thread
def angle_update(socket, truth):

    global uAngle
    global uDist
    while True:

        data = socket.recv(1024)
        data_str = data.decode('utf-8')
        angle, distance = data_str.split(',')
        uAngle = float(angle)
        uDist = float(distance)


truth = 1

###the thread that is updating the values previously mentioned
thred= threading.Thread(target = angle_update, args = (client_socket1,truth))
thred.start()
    
 









#linux audio control function so that amplitude of volume can be controlled
def set_volume(volume):
    command = f"amixer set Master {volume}%"
    subprocess.call(command, shell=True)

###intialize variables for calculation later
scaleDist = 0.0
scaleAng = 0.0
uAngleMag = 0.0
tAngleMag = 0.0
cond = 0.0
numerator = 0.0


calibrationDistance = 1 ##ft
areaSquare = 0 ##initialize all calibration variables
areaHexagon = 0
areaPentagon = 0
areaTriangle = 0
###FOV = input("what is your FOV: ")##takes input for camera FOV of user (for now is 120 based on my camera)
###FOV = float(FOV)##converts input into floating point data

###use cv2 to read calibration images of markers at 1ft from the camera
calibrationImageSquare =cv2.imread("square.jpg")
calibrationImageTriangle = cv2.imread("tri.jpg")
calibrationImagePentagon = cv2.imread("pent.jpg")
calibrationImageHexagon = cv2.imread("unnamed.jpg")

##use cv2 to resize images of markers to correct frame size (1:1 scaling on aspect ratio so no weird compression)
SquareScaled = cv2.resize(calibrationImageSquare, (1280, 720))
TriangleScaled = cv2.resize(calibrationImageTriangle, (1280, 720))
PentagonScaled = cv2.resize(calibrationImagePentagon, (1280, 720))
HexagonScaled = cv2.resize(calibrationImageHexagon, (1280, 720))




###block to convert scaled images into HSV ranges(hue saturation and brightness but with a V lol)
hsvSquare = cv2.cvtColor(SquareScaled, cv2.COLOR_BGR2HSV)
hsvTriangle = cv2.cvtColor(TriangleScaled, cv2.COLOR_BGR2HSV)
hsvPentagon = cv2.cvtColor(PentagonScaled, cv2.COLOR_BGR2HSV)
hsvHexagon = cv2.cvtColor(HexagonScaled, cv2.COLOR_BGR2HSV)

###sets lower and upper boundaries of HSV values we are looking for in the calibration images,
###in theory this can be literally whatever based on the color of the markers, however since I used
###green markers these are the values I used
lower_green = np.array([45, 100, 85])
upper_green = np.array([75, 255, 255])


### creates a white hot heat binary heat map, where HSV values in the boundaries above show white
###all excluded values show black
calibrationMaskSquare = cv2.inRange(hsvSquare,lower_green,upper_green)
calibrationMaskTriangle = cv2.inRange(hsvTriangle,lower_green,upper_green)
calibrationMaskPentagon = cv2.inRange(hsvPentagon,lower_green,upper_green)
calibrationMaskHexagon = cv2.inRange(hsvHexagon,lower_green,upper_green)

###creates a tuple object of all contours in the mask created above for each marker type, and approximates using
###simple shapes knowledge base
contoursSquare, hier = cv2.findContours(calibrationMaskSquare, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
contoursTriangle, hier = cv2.findContours(calibrationMaskTriangle, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
contoursPentagon, hier = cv2.findContours(calibrationMaskPentagon, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
contoursHexagon, hier = cv2.findContours(calibrationMaskHexagon, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

###loops to access each contour in the tuple
for cnt in contoursSquare:
    area = cv2.contourArea(cnt)###cv2 approximates area by detecting boundaries of created shapes
    if area >= 3000: ###filter to remove visual noise that might be detected in calibration image
        areaSquare += area ###just incase the shape is split into multiple contours, used += instead of =
        ###above line finds area of calibration image, will be used later

###same as above but for triangular looking marker
for cnt in contoursTriangle:
    area = cv2.contourArea(cnt)
    if area >= 3000:
        areaTriangle += area

###ditto for pentagon marker
for cnt in contoursPentagon:
    area = cv2.contourArea(cnt)
    if area >= 3000:
        areaPentagon += area

###ditto for hexagon marker
for cnt in contoursHexagon:
    area = cv2.contourArea(cnt)
    if area >= 3000:
        areaHexagon += area

print(areaHexagon)
print(areaSquare)
print(areaTriangle)
print(areaPentagon)

    

###capture video from camera
cap = cv2.VideoCapture(0)

###set dimensions of capture (must be same as calibration native size)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
width = cap.get(cv2.CAP_PROP_FRAME_WIDTH )
height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT )
print(width)
print(height) ###check to make sure output is right dimensions

###creation of sliders window for setting inputs on marker detection
###cv2.namedWindow("sliders")
###we dont want the sliders themselves to actually call a function, so we define a null function
def nothing(x):
    pass
###creates sliders for lower and upper bounds of H, S, and V respectively, THESE ARE NOT USED ANYMORE AS THEY DESTROYED FRAMERATE
###cv2.createTrackbar("L=H", "sliders", 0 ,180, nothing)
###cv2.createTrackbar("L=S", "sliders", 0 ,255, nothing)
###cv2.createTrackbar("L=V", "sliders", 0 ,255, nothing)
###cv2.createTrackbar("U=H", "sliders", 0 ,180, nothing)
###cv2.createTrackbar("U=S", "sliders", 0 ,255, nothing)
###cv2.createTrackbar("U=V", "sliders", 0 ,255, nothing)

###not used for now
iterationCount = 0

###creation of channels, also no longer used but could be in a less precise system
front = 0
left = 0
right = 0
back = 0

##live updating audio channel initialization, same case as above
channelFront = 0
channelLeft = 0
channelRight = 0
channelBack = 0

###realtime loop
while True:
    ###takes a frame at the refresh rate of camera
    _, frame = cap.read()
    ###reinitialized channels
    angle = 0
    ###applies HSV binary output to the captured frame
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    ###much the same as above, initialize boundary variables for HSV range, however instead
    ###of using static values, we use slider values for troubleshooting/detection optimization
    ###lowerH = cv2.getTrackbarPos("L=H","sliders")
    ###upperH = cv2.getTrackbarPos("U=H","sliders")
    ###lowerS = cv2.getTrackbarPos("L=S","sliders")
   ### upperS = cv2.getTrackbarPos("U=S","sliders")
    ###lowerV = cv2.getTrackbarPos("L=V","sliders")
    ###upperV = cv2.getTrackbarPos("U=V","sliders")


    ###create new boundary arrays for realtime detection rather than for a still image
    lower_greenLive = np.array([35, 40, 40])
    upper_greenLive = np.array([88, 255, 255])

    ###creates a binary heatmap like at the start for realtime shapes in frame
    mask = cv2.inRange(hsv, lower_greenLive, upper_greenLive)

    ###to track the xy position (2d) of the shape, we need to find the moment of the contour
    ###the moment is simply the center of the contour/contour group 
    #(the center of a contour group happens if two markers are detected, which is ok)
    #(ok due to head being in between two markers)
    M = cv2.moments(mask)
    ###need this if statement to prevent code from throwing error when no objects are on screen
    if M["m00"] != 0:
        cX = int(M["m10"] / M["m00"])
        cY = int(M["m01"] / M["m00"])
        ###because we are using 1920x1080p camera, the center point of the camera axis is 960 pixels
        ###we want to center our output around 960 rather than 0
        LR = cX-960

        ###angle is the ratio of our displacement times 1 half FOV due to 1 half of the output grid
        ###being 1 half of the total FOV
        ###up down does not matter in terms of application so only left right angle is tracked
        LR_angle = 1
    else:
        print("no valid marker detected")

    ###create contours tuple like in the calibration phase
    contours, hier = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    ###checks amount of contours for trouble shooting
    cntCount = 0
    ###finds area of largest contour(primary marker)
    maxArea = 0 ###initialize area of main contour

    ###so no errors are thrown, only check for max if there is at least one object to check over

    if len(contours) != 0:
        c = max(contours, key = cv2.contourArea)
        maxArea = cv2.contourArea(c)
        cApp = cv2.approxPolyDP(cnt, 0.04*cv2.arcLength(cnt, True), True)
    for cnt in contours:
        ###finds the total amount of sides in a contour, which can then be applied to a polygonal marker
        app = cv2.approxPolyDP(cnt, 0.04*cv2.arcLength(cnt, True), True)

        ###draws bounding box around the detected image OUTSIDE of the mask
        cv2.drawContours(frame, [app], 0, (0,0,0), 3)

        ###area calculation for all contours
        area = cv2.contourArea(cnt)
        ###initialize sidecount for the if statements to follow
        sideCount = 0

        ###check sidecount for contours bigger than 5000 square pixels

        if area > 5000:
            sideCount = len(app)
            ###iterate per contour
            cntCount += 1
            print(sideCount)
        ###if there is a big enough contour, check the sidecount of the largest one
        if area > 5000:
            if sideCount == 4:
        ###front facing marker
                angle = 0


        ###distance calculation
                distance = (areaSquare/maxArea)*calibrationDistance
        ###relaxation factor if two contours are detected to minimize maximum error
                if cntCount >= 2:
                    distance = distance*1.1
        ###outputs when square is primary detected
                print("left right displacement is", LR)
                print("LR angular displacement is", LR_angle)
                print("up down displacement is", cY)
                print("z displacement is", distance, "ft")
                if(LR < -200):
                    angle -= 15
                if(LR>200):
                    angle+=15
                ###ACTUAL SCALING CALCULATION
                tAngle = angle
                tDist = distance
                scaleDist = tDist/(uDist*.5)
                if scaleDist >= 1.43:
                    scaleDist = 1.43
                uAngleMag = sqrt(uAngle**2)
                tAngleMag = sqrt(tAngle**2)
                cond = sqrt((uAngle-tAngle)**2)
                if cond <= 90:
                    scaleAng = 1-(cond/90)
                else:
                    scaleAng = 0.0
                volumeOut = scaleDist*scaleAng*100
                print("volume is", volumeOut)
                set_volume(volumeOut)




            if sideCount == 3:
        ###back facing marker
                angle = 180

        ###distance calculation
                distance = (.5*areaSquare/maxArea)*calibrationDistance
        ###relaxation factor if two contours are detected to minimize maximum error
                if cntCount >= 2:
                    distance = distance*1.15
        ###outputs when square is primary detected
                print("left right displacement is", LR)
                print("LR angular displacement is", LR_angle)
                print("up down displacement is", cY)
                print("z displacement is", distance, "ft")
                if(LR < -200):
                    angle = -(angle) + 15
                if(LR>200):
                    angle -= 15
                print(angle)
                ###ACTUAL SCALING CALCULATION
                tAngle = angle
                tDist = distance
                scaleDist = tDist/(uDist*.5)
                
                if scaleDist >= 1.42:
                    scaleDist = 1.42
                uAngleMag = sqrt(uAngle**2)
                tAngleMag = sqrt(tAngle**2)
                cond = sqrt((tAngleMag-uAngleMag)**2)
                if cond <= 90:
                    scaleAng = 1-(cond/90)
                else:
                    scaleAng = 0.0
                volumeOut = scaleDist*scaleAng*100
                print("volume is", volumeOut)
                set_volume(volumeOut)
                



            if sideCount == 5:
        ###left facing marker
                angle = -90


        ###distance calculation
                distance = (areaPentagon/maxArea)*calibrationDistance
        ###relaxation factor if two contours are detected to minimize maximum error
                if cntCount >= 2:
                    distance = distance*1.15
                    
        ###outputs when square is primary detected
                print("left right displacement is", LR)
                print("LR angular displacement is", LR_angle)
                print("up down displacement is", cY)
                print("z displacement is", distance, "ft")
                if(LR < -200):
                    angle += 15
                if(LR>200):
                    angle -= 15
                print(angle)
                ###ACTUAL SCALING CALCULATION
                tAngle = angle
                tDist = distance
                scaleDist = tDist/(uDist*.5)
                if scaleDist >= 1.42:
                    scaleDist = 1.42
                uAngleMag = sqrt(uAngle**2)
                tAngleMag = sqrt(tAngle**2)
                cond = sqrt((tAngle-uAngle)**2)
                if cond <= 90:
                    scaleAng = 1-(cond/90)
                else:
                    scaleAng = 0.0
                volumeOut = scaleDist*scaleAng*100
                print("volume is", volumeOut)
                set_volume(volumeOut)
                


            if sideCount == 6:
        ###right facing marker
                angle = 90

        ###distance calculation
                distance = (areaHexagon/maxArea)*calibrationDistance
        ###relaxation factor if two contours are detected to minimize maximum error
                if cntCount >= 2:
                    distance = distance/1.2
        ###outputs when square is primary detected
                print("left right displacement is", LR)
                print("LR angular displacement is", LR_angle)
                print("up down displacement is", cY)
                print("z displacement is", distance, "ft")
                print(angle)
                if(LR < -600):
                    angle += 15
                if(LR>-200):
                    angle-=15
                print(angle)
                ###ACTUAL SCALING CALCULATION
                tAngle = angle
                tDist = distance
                scaleDist = tDist/(uDist*.5)
                if scaleDist >= 1.42:
                    scaleDist = 1.42
                uAngleMag = sqrt(uAngle**2)
                tAngleMag = sqrt(tAngle**2)
                cond = sqrt((tAngle-uAngle)**2)
                if cond <= 90:
                    scaleAng = 1-(cond/90)
                else:
                    scaleAng = 0.0
                volumeOut = scaleDist*scaleAng*100
                print("volume is", volumeOut)
                set_volume(volumeOut)
                






 
   


    ###show the initial live frame, and the masked output
    cv2.imshow("frame",frame)
    ###cv2.imshow("Mask",mask)
    
    ###how to quit the loop
    if cv2.waitKey(1) == ord("q"): 
        break

