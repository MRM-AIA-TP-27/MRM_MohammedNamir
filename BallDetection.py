import cv2 as cv
import numpy as np

ly = np.array([20, 100, 100])
uy = np.array([30, 255, 255])

cam = cv.VideoCapture(0)
pcircle = None
distance = lambda a,b,x,y: (a-x)**2 + (b-y)**2

while True:
    ret, frame = cam.read()
    if not ret: 
        break

    hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
    
    yellowconvert = cv.inRange(hsv, ly, uy)
    
    blured = cv.GaussianBlur(yellowconvert, (17,17), 0)

    circles = cv.HoughCircles(blured, cv.HOUGH_GRADIENT, 1.2, 100,
                              param1=100, param2=20, minRadius=75, maxRadius=400)

    if circles is not None:
        circles = np.uint16(np.around(circles))
        chosen = None
        for i in circles[0, :]:
            if chosen is None: chosen = i
            if pcircle is not None:
                if distance(chosen[0],chosen[1],pcircle[0],pcircle[1]) <= distance(i[0],i[1],pcircle[0],pcircle[1]):
                    chosen = i
        
        cv.circle(frame, (chosen[0], chosen[1]), 1, (0, 0, 255), 3)
        cv.circle(frame, (chosen[0], chosen[1]), chosen[2], (255, 0, 255), 3)
        
        x, y, r = chosen[0], chosen[1], chosen[2]
        position = (x - 70, y - r - 15)
        cv.putText(frame, "tennis ball", position, cv.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
        
        pcircle = chosen

    cv.imshow("circles", frame)
    if cv.waitKey(1) & 0xFF == ord('q'): 
        break

cam.release()
cv.destroyAllWindows()