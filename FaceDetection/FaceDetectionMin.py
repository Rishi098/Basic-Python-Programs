import cv2
import mediapipe as mp
import time

cap = cv2.VideoCapture("4.mp4")
PTime = 0
CTime = 0

# import the face detection module from mediapipe
mpFaceDetectionModule = mp.solutions.mediapipe.python.solutions.face_detection
mpDraw = mp.solutions.mediapipe.python.solutions.drawing_utils

faceDetection = mpFaceDetectionModule.FaceDetection()


while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)

    # Convert to RGB image
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    # Process imageusing the facedetection module
    results = faceDetection.process(imgRGB)

    # if face detected extract the data
    if results.detections:
        for id, detection in enumerate(results.detections):
            print(id, detection.score)
            # draw bax around faces using built in drawing function
            # mpDraw.draw_detection(img, detection)

            # Bounding box of the face
            bboxC = detection.location_data.relative_bounding_box
            # print(bboxC)

            # TODO: draw using cv2
            h, w, c = img.shape
            bbox = tuple(map(int, [bboxC.xmin * w, bboxC.ymin * h,
                                   bboxC.width * w, bboxC.height * h]))

            cv2.rectangle(img, bbox, (255, 0, 255), 1)
            cv2.putText(img, f'{int(detection.score[0]*100)}%', (bbox[0], bbox[1]-20),
                        cv2.FONT_HERSHEY_TRIPLEX, 1, (255, 0, 255), 2)

            # TODO:Fancy drawing box
            l = 30
            thick = 4
            x, y, w, h = bbox
            x1, y1 = x+w, y+h
            # Top Left (x,y)            
            cv2.line(img, (x, y), (x+l, y), (255, 0, 255), thick)
            cv2.line(img, (x, y), (x, y+l), (255, 0, 255), thick)

            # Top right (x1,y)
            cv2.line(img, (x1, y), (x1 - l, y), (255, 0, 255), thick)
            cv2.line(img, (x1, y), (x1, y+l), (255, 0, 255), thick)

            # Down Left (x,y1)
            cv2.line(img, (x, y1), (x+l, y1), (255, 0, 255), thick)
            cv2.line(img, (x, y1), (x, y1-l), (255, 0, 255), thick)

            # Down Right(x1,y1)
            cv2.line(img, (x1, y1), (x1-l, y1), (255, 0, 255), thick)
            cv2.line(img, (x1, y1), (x1, y1-l), (255, 0, 255), thick)

    # FPS Calculation
    CTime = time.time()
    fps = 1/(CTime - PTime)
    PTime = CTime

    # Write FPS on to the Video
    cv2.putText(img, f'FPS : {str(int(fps))}', (20, 50),
                cv2.FONT_HERSHEY_TRIPLEX, 1, (255, 33, 0), 2)

    cv2.imshow("Image", img)
    cv2.waitKey(10)
