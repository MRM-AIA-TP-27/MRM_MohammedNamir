import cv2 as cv
import numpy as np

# --- Tunable Parameters ---

# 1. HSV Color range for Tennis Ball Yellow
ly = np.array([20, 100, 100])
uy = np.array([30, 255, 255])

# 2. Texture Threshold
# This is the most important value to tune.
# A real ball will have a HIGH value (e.g., > 400).
# A flat paper circle will have a LOW value (e.g., < 200).
# Use the print(texture_val) statement below to find your value.
TEXTURE_THRESHOLD = 400 

# 3. Hough Circle Parameters
# (minRadius and maxRadius are in pixels)
C_PARAM_1 = 100 # Canny edge high threshold
C_PARAM_2 = 30  # Accumulator threshold (lower = more circles)
C_MIN_RAD = 40  # Smaller than this is probably noise
C_MAX_RAD = 400 # Larger than this is probably not a ball


# --- Texture Analysis Function ---

def get_texture_variance(image_roi):
    """
    Calculates the variance of the Laplacian.
    A high variance means high texture/fuzziness.
    A low variance means low texture/smoothness.
    """
    if image_roi.size == 0:
        return 0
    # Convert ROI to grayscale and compute Laplacian
    laplacian = cv.Laplacian(cv.cvtColor(image_roi, cv.COLOR_BGR2GRAY), cv.CV_64F)
    # Calculate the variance
    variance = laplacian.var()
    return variance

# --- Initialization ---

cam = cv.VideoCapture(0)
pcircle = None
distance = lambda a,b,x,y: (a-x)**2 + (b-y)**2

# Initialize CLAHE (Contrast Limited Adaptive Histogram Equalization)
# This will help normalize lighting in all conditions.
clahe = cv.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))

print("Starting camera... Press 'q' to quit.")
print(f"Set TEXTURE_THRESHOLD is: {TEXTURE_THRESHOLD}. Tune this if needed.")

while True:
    ret, frame = cam.read()
    if not ret: 
        break

    # --- 1. Lighting Correction ---
    
    # Create grayscale image
    grayFrame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    
    # Create HSV image
    hsv = cv.cvtColor(frame, cv.COLOR_BGR2HSV)
    
    # Apply CLAHE to the Grayscale image for better edge detection
    gray_equalized = clahe.apply(grayFrame)
    
    # Apply CLAHE to the V (Value/Brightness) channel of HSV
    h, s, v = cv.split(hsv)
    v_equalized = clahe.apply(v)
    hsv_equalized = cv.merge([h, s, v_equalized])

    # Blur the equalized gray image
    blured = cv.GaussianBlur(gray_equalized, (17,17), 0)

    # --- 2. Find ALL Circles ---
    # Detect circles on the equalized, blurred grayscale image
    circles = cv.HoughCircles(blured, cv.HOUGH_GRADIENT, 1.2, 100,
                              param1=C_PARAM_1, param2=C_PARAM_2, 
                              minRadius=C_MIN_RAD, maxRadius=C_MAX_RAD)

    valid_tennis_balls = []

    if circles is not None:
        circles = np.uint16(np.around(circles))
        
        # --- 3. Filter Circles by Color and Texture ---
        for i in circles[0, :]:
            x, y, r = i[0], i[1], i[2]
            
            # --- Color Check ---
            # Create a mask for just this circle
            mask = np.zeros(hsv.shape[:2], dtype="uint8")
            cv.circle(mask, (x, y), r, 255, -1)
            
            # Get the average color *within the circle* from the equalized HSV image
            mean_hsv = cv.mean(hsv_equalized, mask=mask)
            
            is_yellow = (mean_hsv[0] >= ly[0] and mean_hsv[0] <= uy[0])
            is_saturated = (mean_hsv[1] >= ly[1] and mean_hsv[1] <= uy[1])
            is_bright = (mean_hsv[2] >= ly[2] and mean_hsv[2] <= uy[2])
            
            if is_yellow and is_saturated and is_bright:
                # --- Texture Check ---
                # Get the ROI (Region of Interest) from the *original color frame*
                x_start = max(x - r, 0)
                x_end = min(x + r, frame.shape[1])
                y_start = max(y - r, 0)
                y_end = min(y + r, frame.shape[0])
                
                circle_roi = frame[y_start:y_end, x_start:x_end]
                
                texture_val = get_texture_variance(circle_roi)
                
                # UNCOMMENT THIS LINE TO TUNE YOUR THRESHOLD:
                # print(f"Circle at ({x},{y}) has texture value: {texture_val:.2f}")
                
                if texture_val > TEXTURE_THRESHOLD:
                    # This circle is yellow AND fuzzy. It's a valid ball.
                    valid_tennis_balls.append(i)

    # --- 4. Track the Best Ball ---
    
    chosen = None
    if len(valid_tennis_balls) > 0:
        # We have at least one valid tennis ball.
        # Now, find the one closest to the previous frame's ball.
        for ball in valid_tennis_balls:
            if chosen is None:
                chosen = ball
            if pcircle is not None:
                # Compare distances to find the closest ball
                if distance(ball[0], ball[1], pcircle[0], pcircle[1]) < distance(chosen[0], chosen[1], pcircle[0], pcircle[1]):
                    chosen = ball
        
        # --- 5. Draw the Chosen Ball ---
        x, y, r = chosen[0], chosen[1], chosen[2]
        
        # Draw center
        cv.circle(frame, (x, y), 1, (0, 0, 255), 3)
        # Draw outline
        cv.circle(frame, (x, y), r, (255, 0, 255), 3)
        
        # Draw text
        position = (x - 70, y - r - 15)
        cv.putText(frame, " ball", position, cv.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
        
        pcircle = chosen # Update the previous circle
    
    else:
        # No valid tennis balls were found in this frame
        pcircle = None

    # --- 6. Display Results ---
    cv.imshow("Ball Ball  Detection", frame)
    cv.imshow("Debugging - Equalized/Blurred", blured)

    if cv.waitKey(1) & 0xFF == ord('q'): 
        break

# --- Cleanup ---
cam.release()
cv.destroyAllWindows()