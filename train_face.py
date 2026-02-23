import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import numpy as np
import os
import json
import time

def calculate_face_signature(landmarks):
    # landmarks is a list of NormalizedLandmark objects
    def dist(p1, p2):
        return np.sqrt((p1.x - p2.x)**2 + (p1.y - p2.y)**2 + (p1.z - p2.z)**2)

    # Indices for Face Mesh (Tasks API indices are the same)
    # 33: Left Eye Inner, 133: Left Eye Outer
    # 362: Right Eye Inner, 263: Right Eye Outer
    # 1: Nose Tip
    # 61: Mouth Left, 291: Mouth Right
    # 10: Forehead, 152: Chin
    # 234, 454: Cheekbones
    
    # Structural Ratios (Invariant to distance/lighting/hair)
    left_eye_w = dist(landmarks[33], landmarks[133])
    right_eye_w = dist(landmarks[362], landmarks[263])
    eye_dist = dist(landmarks[133], landmarks[362])
    nose_w = dist(landmarks[61], landmarks[291]) # Mouth width as reference
    face_h = dist(landmarks[10], landmarks[152])
    face_w = dist(landmarks[234], landmarks[454])
    
    signature = [
        eye_dist / face_w,
        left_eye_w / face_w,
        nose_w / face_w,
        face_h / face_w,
        dist(landmarks[1], landmarks[152]) / face_h, # Nose to chin
        dist(landmarks[33], landmarks[263]) / face_w # Global eye span
    ]
    return signature

def train_face():
    # Setup MediaPipe Tasks
    model_path = 'face_landmarker.task'
    if not os.path.exists(model_path):
        print(f"Error: {model_path} not found.")
        return

    BaseOptions = mp.tasks.BaseOptions
    FaceLandmarker = mp.tasks.vision.FaceLandmarker
    FaceLandmarkerOptions = mp.tasks.vision.FaceLandmarkerOptions
    VisionRunningMode = mp.tasks.vision.RunningMode

    options = FaceLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=model_path),
        running_mode=VisionRunningMode.VIDEO)

    cap = cv2.VideoCapture(0)
    
    print("\n[SYSTEM]: INITIALIZING NEURAL STRUCTURAL SCAN...")
    print("--------------------------------------------------")
    print("This High-Accuracy AI system analyzes 478 points.")
    print("It uses 3D geometric ratios, making it resistant")
    print("to lighting shifts, hairstyles, and backgrounds.")
    print("--------------------------------------------------")
    time.sleep(2)

    signatures = []
    target = 40
    
    with FaceLandmarker.create_from_options(options) as landmarker:
        while len(signatures) < target:
            ret, frame = cap.read()
            if not ret: break
            
            frame = cv2.flip(frame, 1)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            
            # Tasks API requires timestamp in ms
            timestamp_ms = int(time.time() * 1000)
            result = landmarker.detect_for_video(mp_image, timestamp_ms)
            
            if result.face_landmarks:
                landmarks = result.face_landmarks[0]
                sig = calculate_face_signature(landmarks)
                signatures.append(sig)
                
                # Visual dots for feedback
                h, w, _ = frame.shape
                for idx in [33, 133, 362, 263, 1, 10, 152]:
                    pt = landmarks[idx]
                    cv2.circle(frame, (int(pt.x * w), int(pt.y * h)), 2, (0, 255, 255), -1)
                
                cv2.putText(frame, f"ANALYZING MESH: {int((len(signatures)/target)*100)}%", 
                            (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

            cv2.imshow('JARVIS - 3D Geometric Training', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()

    if len(signatures) > 0:
        avg_sig = np.mean(signatures, axis=0).tolist()
        with open('user_face_signature.json', 'w') as f:
            json.dump(avg_sig, f)
        print("\n--------------------------------------------------")
        print("SUCCESS: Geometric Identity Secured.")
        print("Jarvis now remembers the architecture of your face.")
        print("--------------------------------------------------")
    else:
        print("Error: No landmarks detected.")

if __name__ == "__main__":
    train_face()
