import cv2
import mediapipe as mp
import threading
import time
import os
import warnings

warnings.filterwarnings("ignore")

def euclidean_distance(pt1, pt2):
    return ((pt1.x - pt2.x) ** 2 + (pt1.y - pt2.y) ** 2) ** 0.5

gesture_active = False
start_pos = None
end_pos = None

def classify_movement(start, end):
    if not start and not end:
        return None
    
    dx, dy = displacement(start, end)

    if abs(dx) < 0.05 and abs(dy) < 0.05:
        return None

    if abs(dx) > abs(dy):
        return "RIGHT" if dx > 0 else "LEFT"
    else:
        return "DOWN" if dy > 0 else "UP"

def track_movement(lm):
    global gesture_active, start_pos, end_pos
    
    curr = lm[8].x, lm[8].y

    gesture_detected = detect_gesture(lm)

    if gesture_detected and not gesture_active:
        gesture_active = True
        start_pos = curr
    elif gesture_active and gesture_detected:
        end_pos = curr
    elif gesture_active and not gesture_detected:
        gesture_active = False
        start_pos = None
        end_pos = None
        return f"{gesture_detected}_{classify_movement(start_pos, end_pos)}"

# def get_point(lm):
#     return lm[8].x, lm[8].y

def displacement(p1, p2):
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    hand_size = euclidean_distance(lm[0], lm[9])
    dx /= hand_size
    dy /= hand_size
    return dx, dy

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

    # if (thumb_tip < index_base and index_tip > index_base and middle_tip > index_base and 
    #     ring_tip > index_base and pinky_tip > index_base):
    #     return "thumbs up"

    # if (index_tip > index_base and middle_tip > index_base and 
    #     ring_tip > index_base and pinky_tip > index_base):
    #     return "fist"
    
    # if (euclidean_distance(landmarks[4], landmarks[8]) < 0.03):
    #     return "pinch"
    
    return None

model_path = "hand_landmarker.task"

BaseOptions = mp.tasks.BaseOptions
HandLandmarker = mp.tasks.vision.HandLandmarker
HandLandmarkerOptions = mp.tasks.vision.HandLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

options = HandLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=model_path),
    running_mode=VisionRunningMode.IMAGE,
    num_hands=1,
    min_hand_detection_confidence=0.7,
    min_hand_presence_confidence=0.7,
    min_tracking_confidence=0.7
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

        result = landmarker.detect(mp_image)

        gesture = None

        if result.hand_landmarks:
            for hand_landmarks in result.hand_landmarks:
                dg = detect_gesture(hand_landmarks)
                tm = track_movement(hand_landmarks)
                if dg:
                    gesture = dg
                if tm:
                    gesture = tm

                h, w, _ = frame.shape
                for lm in hand_landmarks:
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    cv2.circle(frame, (cx, cy), 4, (0, 255, 0), -1)

        if gesture:
            text = gesture
            color = (215, 70, 123) 
            font = cv2.FONT_HERSHEY_SIMPLEX

            x, y = 50, 80

            cv2.putText(frame, text, (x + 2, y + 2), font, 2, (0, 0, 0), 3, cv2.LINE_AA)
            cv2.putText(frame, text, (x, y), font, 2, color, 2, cv2.LINE_AA)


        cv2.imshow("Hand Gesture Recognition", frame)

        if cv2.waitKey(1) & 0xFF == 27:
            break

cap.release()
cv2.destroyAllWindows()