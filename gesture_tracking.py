import cv2
import time
import mediapipe as mp
import warnings
warnings.filterwarnings("ignore")

model_path = "gesture_recognizer.task"

BaseOptions = mp.tasks.BaseOptions
GestureRecognizer = mp.tasks.vision.GestureRecognizer
GestureRecognizerOptions = mp.tasks.vision.GestureRecognizerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

current_gesture = None
in_control = False
prev_center = None # movement state outside the callback
curr_center = None

def result_callback(result, output_image, timestamp_ms):
    global current_gesture, in_control, prev_center, curr_center
    dx=0
    dy=0

    if result.gestures:
        # First hand, top prediction
        gesture = result.gestures[0][0] 
        # current_gesture = f"{gesture.category_name}"
        in_control = True
    else:
        # current_gesture = None
        in_control = False

    if  in_control:
        hand_landmarks = result.hand_landmarks # list of hands eg, [hand0, hand1, ...]
        points = [ # first hand hand0 's landmarks
            hand_landmarks[0][0],   # wrist
            hand_landmarks[0][5],   # index MCP
            hand_landmarks[0][9],   # middle MCP
            hand_landmarks[0][13],  # ring MCP
            hand_landmarks[0][17],  # pinky MCP
        ]
        curr_center = (sum(i.x for i in points)/5, sum(i.y for i in points)/5)
        if prev_center:
            dx = curr_center[0] - prev_center[0]
            dy = curr_center[1] - prev_center[1]
        prev_center = curr_center

        if abs(dx)>abs(dy):
            if(dx<0):
                direction = "LEFT"
            else:
                direction = "RIGHT"
        else:
            if(dy<0):
                direction = "UP"
            else:
                direction = "DOWN"
        current_gesture = f"{gesture.category_name}_{direction}"
    else:
        prev_center = None
        curr_center = None

    
        
options = GestureRecognizerOptions(
    base_options=BaseOptions(model_asset_path=model_path),
    running_mode=VisionRunningMode.LIVE_STREAM,
    result_callback=result_callback,
)

cap = cv2.VideoCapture(0)

with GestureRecognizer.create_from_options(options) as recognizer:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb
        )

        recognizer.recognize_async(mp_image, int(time.time() * 1000))

        if current_gesture:
            cv2.putText(frame,current_gesture,(40, 80),cv2.FONT_HERSHEY_SIMPLEX,1,(0, 255, 255),1)
            # if current_gesture == "Open_Palm":
                
        cv2.imshow("Gesture Recognition", frame)

        if cv2.waitKey(1) & 0xFF == 27: 
            break

cap.release()
cv2.destroyAllWindows()