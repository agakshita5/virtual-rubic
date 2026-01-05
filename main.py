import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import numpy as np

cap = cv2.VideoCapture(0) # webcam

# as it is
base_options = python.BaseOptions(
    model_asset_path= '/Users/agakshita/AI/virtual-rubic/hand_landmarker.task'
)

options = vision.HandLandmarkerOptions(
    base_options=base_options,
    num_hands=2,
    running_mode = vision.RunningMode.IMAGE # required
)

landmarker = vision.HandLandmarker.create_from_options(options)
#

def classify_gesture(landmarks):

    # Normalize using wrist as reference
    wrist = landmarks[0]
    
    fingertips_ids = [8,12,16,20]

    distances = [] # fingertips to wrist

    for idx in fingertips_ids:
        tip = landmarks[idx]
        dist = np.linalg.norm(
            np.array([tip.x - wrist.x, tip.y - wrist.y])
        )
        distances.append(dist)

    # average distance of fingertips from wrist
    avg_dist = np.mean(distances)

    # thumb distances
    thumb_tip = landmarks[4]
    thumb_dist = np.linalg.norm(np.array([thumb_tip.x - wrist.x, thumb_tip.y - wrist.y]))

    all_distances = distances + [thumb_dist]
    avg_dist_all = np.mean(all_distances)

    pinch_dist = np.linalg.norm(np.array([thumb_tip.x - landmarks[8].x, thumb_tip.y - landmarks[8].y]))

    if pinch_dist < 0.03:
        return 'pinch'
    if thumb_tip.y < wrist.y and avg_dist < 0.12: # thumb tip above wrist
        return 'thumbs up'
    if thumb_tip.y > wrist.y and avg_dist < 0.12: # thumb tip below wrist
        return 'thumbs down'
    # fist = all fingers are close to wrist
    if avg_dist_all < 0.15: 
        return 'fist'

    return "open hand"

while True:
    ret, frame = cap.read()
    if not ret:
        break
    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
    result = landmarker.detect(mp_image)
    # drawing points ourselves - task api doesn't auto-draw
    if result.hand_landmarks:
        for hand_landmarks in result.hand_landmarks:

            for lm in hand_landmarks:
                h, w, _ = frame.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                cv2.circle(frame, (cx, cy), 5, (0, 255, 0), -1)

            # Detect fist
            result = classify_gesture(hand_landmarks)
            cv2.putText(frame, result, (30, 60), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 0, 255), 3)

    cv2.imshow("Gestures", frame)

    if cv2.waitKey(1) == 27:
        break

cap.release()
cv2.destroyAllWindows()
