import cv2
import time
import mediapipe as mp
import warnings
warnings.filterwarnings("ignore")

g_model_path = "gesture_recognizer.task"
l_model_path = "hand_landmarker.task"

BaseOptions = mp.tasks.BaseOptions
GestureRecognizer = mp.tasks.vision.GestureRecognizer
GestureRecognizerOptions = mp.tasks.vision.GestureRecognizerOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
HandLandmarkerResult = mp.tasks.vision.HandLandmarkerResult
VisionRunningMode = mp.tasks.vision.RunningMode

current_gesture = None
in_control = False
prev_center = None # movement state outside the callback
curr_center = None

def g_result_callback(result, output_image, timestamp_ms):
    global current_gesture, in_control

    if result.gestures:
        # First hand, top prediction
        gesture = result.gestures[0][0] 
        # if gesture:
        in_control = True
        current_gesture = gesture.category_name
    else:
        in_control = False
        current_gesture = None

lldm = None
def l_result_callback(result: HandLandmarkerResult, output_image: mp.Image, timestamp_ms: int):
    global lldm
    if result.hand_landmarks:
        lldm = result.hand_landmarks[0]
    else:
        lldm = None

disp_ges = None # text to put on screen (don't rely on async callback)
def track_movement():
    global prev_center, curr_center, current_gesture, disp_ges
    if not in_control or lldm is None:
        prev_center = None
        return

    points = [lldm[i] for i in [0,5,9,13,17]] # first hand hand0 's landmarks
    curr_center = (sum(i.x for i in points)/5, sum(i.y for i in points)/5)
    
    if prev_center is None:
        prev_center = curr_center
        return
    
    dx = curr_center[0] - prev_center[0]
    dy = curr_center[1] - prev_center[1]

    MOVE_THRESH = 0.015
    AXIS_RATIO = 1.3

    if abs(dx) < MOVE_THRESH and abs(dy) < MOVE_THRESH:
        prev_center = curr_center
        return

    if abs(dx) > abs(dy) * AXIS_RATIO:
        direction = "LEFT" if dx < 0 else "RIGHT"
    elif abs(dy) > abs(dx) * AXIS_RATIO:
        direction = "UP" if dy < 0 else "DOWN"
    else:
        prev_center = curr_center
        return

    current_gesture = f"{current_gesture}_{direction}"
    disp_ges = current_gesture 
    prev_center = curr_center 

g_options = GestureRecognizerOptions(
    base_options=BaseOptions(model_asset_path=g_model_path),
    running_mode=VisionRunningMode.LIVE_STREAM,
    result_callback=g_result_callback,
)
l_options = HandLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=l_model_path),
    running_mode=VisionRunningMode.LIVE_STREAM,
    min_hand_detection_confidence=0.7,
    min_hand_presence_confidence=0.7,
    min_tracking_confidence=0.7,
    result_callback=l_result_callback
)
cap = cv2.VideoCapture(0)

with GestureRecognizer.create_from_options(g_options) as recognizer, HandLandmarker.create_from_options(l_options) as landmarker:
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

        ts = int(time.time() * 1000)
        recognizer.recognize_async(mp_image, ts)
        landmarker.detect_async(mp_image, ts)
        
        track_movement()
        if disp_ges:
            cv2.putText(frame,disp_ges,(40, 80),cv2.FONT_HERSHEY_SIMPLEX,1.5,(255, 0, 255),3)

        cv2.imshow("Gesture Recognition", frame)

        if cv2.waitKey(1) & 0xFF == 27: 
            break

cap.release()
cv2.destroyAllWindows()