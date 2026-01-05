import cv2
import mediapipe as mp
# from gtts import gTTS
# import pygame
import threading
import time
import os
import warnings

warnings.filterwarnings("ignore")

mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

# def play_audio(text):
#     filename = f"voice_{text.replace(' ', '_').lower()}.mp3"
#     tts = gTTS(text=text, lang='id')
#     tts.save(filename)

#     pygame.mixer.init()
#     pygame.mixer.music.load(filename)
#     pygame.mixer.music.play()

#     while pygame.mixer.music.get_busy():
#         time.sleep(0.1)

#     pygame.mixer.quit()
#     os.remove(filename)


def detect_gesture(landmarks):
    thumb_tip = landmarks.landmark[4].y
    index_tip = landmarks.landmark[8].y
    middle_tip = landmarks.landmark[12].y
    ring_tip = landmarks.landmark[16].y
    pinky_tip = landmarks.landmark[20].y

    thumb_base = landmarks.landmark[2].y
    index_base = landmarks.landmark[5].y


    if (thumb_tip < thumb_base and index_tip < index_base and 
        middle_tip < index_base and ring_tip < index_base and pinky_tip < index_base):
        return "Hello"

    if (index_tip < index_base and middle_tip > index_base and 
        ring_tip > index_base and pinky_tip > index_base):
        return "My name is"

    if (index_tip > index_base and middle_tip > index_base and 
        ring_tip > index_base and pinky_tip > index_base):
        return "open hand"

    if (index_tip < index_base and pinky_tip < index_base and 
        middle_tip > index_base and ring_tip > index_base):
        return "thank you"

    return None


cap = cv2.VideoCapture(0)

last_gesture = None
last_time = 0

gesture_colors = {
    "hello": (255, 0, 0), 
    "my name is": (0, 255, 0),
    "example": (0, 165, 255), 
    "thank you": (255, 0, 255)  
}

with mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7) as hands:
    while True:
        ret, frame = cap.read()
        if not ret:
            continue

        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hands.process(rgb_frame)

        gesture = None
        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                gesture = detect_gesture(hand_landmarks)

        if gesture:
            text = gesture
            color = gesture_colors.get(text, (255, 255, 255))  # default white color
            font = cv2.FONT_HERSHEY_SIMPLEX

            # Top left corner position
            x, y = 50, 80

            # Thin black shadow to keep it visible
            cv2.putText(frame, text, (x + 2, y + 2), font, 1.2, (0, 0, 0), 3, cv2.LINE_AA)

            cv2.putText(frame, text, (x, y), font, 1.2, color, 2, cv2.LINE_AA)

            # Play a sound when a new gesture is detected.
            # if gesture != last_gesture and time.time() - last_time > 2:
            #     threading.Thread(target=play_audio, args=(text,)).start()
            #     last_gesture = gesture
            #     last_time = time.time()

        cv2.imshow("Hand Gesture Recognition", frame)

        # Press ESC to exit
        if cv2.waitKey(1) & 0xFF == 27:
            break

cap.release()
cv2.destroyAllWindows()