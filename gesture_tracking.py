import cv2
import time
import mediapipe as mp
# from mediapipe.tasks.python import vision
import warnings
warnings.filterwarnings("ignore")

model_path = "gesture_recognizer.task"

BaseOptions = mp.tasks.BaseOptions
GestureRecognizer = mp.tasks.vision.GestureRecognizer
GestureRecognizerOptions = mp.tasks.vision.GestureRecognizerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

current_gesture = None

def result_callback(result, output_image, timestamp_ms):
    global current_gesture
    if result.gestures:
        # First hand, top prediction
        gesture = result.gestures[0][0]
        
        current_gesture = f"{gesture.category_name}"
    else:
        current_gesture = None

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
            cv2.putText(frame,current_gesture,(40, 80),cv2.FONT_HERSHEY_SIMPLEX,2,(0, 255, 255),3)
            if current_gesture == "Open_Palm":
                # todo
        cv2.imshow("Gesture Recognition", frame)

        if cv2.waitKey(1) & 0xFF == 27: 
            break

cap.release()
cv2.destroyAllWindows()