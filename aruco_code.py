import cv2
def main():
    aruco_dicts_to_detect = {
        "4X4": cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_4X4_250),
        "5X5": cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_5X5_250),
        "6X6": cv2.aruco.getPredefinedDictionary(cv2.aruco.DICT_6X6_250),
    }
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open webcam.")
        return
    print("Webcam opened successfully. Press 'q' to quit.")
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not receive frame. Exiting...")
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        for dict_name, aruco_dict in aruco_dicts_to_detect.items():
            aruco_detector = cv2.aruco.ArucoDetector(aruco_dict)
            corners, ids, rejected = aruco_detector.detectMarkers(gray)
            if ids is not None:
                cv2.aruco.drawDetectedMarkers(frame, corners, ids)          
                for i in range(len(ids)):
                    print(f"Detected marker from {dict_name} dictionary with ID: {ids[i][0]}")
        cv2.imshow('Basic ArUco Detection', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    print("Releasing resources...")
    cap.release()
    cv2.destroyAllWindows()
if __name__ == '__main__':
    main()


