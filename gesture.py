import cv2
import mediapipe as mp
import threading
from datetime import datetime
import os
import warnings

warnings.filterwarnings("ignore")

def euclidean_distance(pt1, pt2):
    return ((pt1.x - pt2.x) ** 2 + (pt1.y - pt2.y) ** 2) ** 0.5

gesture_active = False
start_pos = None
end_pos = None

def classify_movement(start, end, lm):
    if not start or not end:
        return None
    
    dx, dy = displacement(start, end, lm)

    if abs(dx) < 0.1 and abs(dy) < 0.1:
        return None

    if abs(dx) > abs(dy):
        return "RIGHT" if dx > 0 else "LEFT"
    else:
        return "DOWN" if dy > 0 else "UP"

def track_movement(lm):
    global gesture_active, start_pos, end_pos
    
    curr = (lm[8].x, lm[8].y)

    gesture_detected = detect_gesture(lm)
    gesture_name = None

    if gesture_detected and not gesture_active:
        gesture_active = True
        gesture_name = gesture_detected
        start_pos = curr
    elif gesture_active and gesture_detected:
        end_pos = curr
    elif gesture_active and not gesture_detected:
        gesture_active = False
        if end_pos is None: # when gesture active but gesture not there (eg, hand remove)
            end_pos= start_pos
        movement = classify_movement(start_pos, end_pos, lm)
        # reset after movement is computed
        start_pos = None
        end_pos = None
        if movement: 
            return f"{gesture_name}_{movement}"
    
    return None

def displacement(p1, p2, lm):
    if p2 is not None or p1 is not None:
        return 0,0
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    # normalizing
    hand_size = euclidean_distance(lm[0], lm[9])
    if hand_size == 0:
        return 0,0
    return dx/hand_size, dy/hand_size

def detect_gesture(landmarks):
    thumb_tip = landmarks[4].y
    index_tip = landmarks[8].y
    middle_tip = landmarks[12].y
    ring_tip = landmarks[16].y
    pinky_tip = landmarks[20].y

    thumb_base = landmarks[2].y
    index_base = landmarks[5].y

    if (thumb_tip < thumb_base and index_tip < index_base and 
        middle_tip < index_base and ring_tip < index_base and pinky_tip < index_base):
        return "open hand"
    
    return None

model_path = "hand_landmarker.task"

BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
HandLandmarkerResult = mp.tasks.vision.HandLandmarkerResult
VisionRunningMode = mp.tasks.vision.RunningMode

rresult = None
def print_result(result: HandLandmarkerResult, output_image: mp.Image, timestamp_ms: int):
    global rresult
    rresult = result

options = HandLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=model_path),
    running_mode=VisionRunningMode.LIVE_STREAM,
    num_hands=1,
    min_hand_detection_confidence=0.7,
    min_hand_presence_confidence=0.7,
    min_tracking_confidence=0.7,
    result_callback=print_result
)

cap = cv2.VideoCapture(0)

with HandLandmarker.create_from_options(options) as landmarker:
    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb_frame
        )

        landmarker.detect_async(mp_image, int(datetime.now().timestamp() * 1000))

        gesture = None

        if rresult and rresult.hand_landmarks:
            for hand_landmarks in rresult.hand_landmarks:
                # gesture : static, movement : not static (spl case of gesture)
                tm = track_movement(hand_landmarks)
                if tm:
                    gesture = tm
                else:
                    gesture = detect_gesture(hand_landmarks)
                
                h, w, _ = frame.shape
                for lm in hand_landmarks:
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    cv2.circle(frame, (cx, cy), 4, (0, 255, 0), -1)

        if gesture:
            cv2.putText(frame, gesture, (52, 82), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 3, cv2.LINE_AA)
            cv2.putText(frame, gesture, (50, 80), cv2.FONT_HERSHEY_SIMPLEX, 2, (215, 70, 123) , 2, cv2.LINE_AA)

        cv2.imshow("Hand Gesture Recognition", frame)

        if cv2.waitKey(1) & 0xFF == 27:
            break

cap.release()
cv2.destroyAllWindows()