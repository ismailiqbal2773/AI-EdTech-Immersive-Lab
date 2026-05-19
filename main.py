import cv2
import numpy as np
import os
import math
import webbrowser
import threading
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI(title="AI EdTech Immersive Lab - Final Stable Release")

# CORS setup for flawless frontend connection
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("models", exist_ok=True)
app.mount("/models", StaticFiles(directory="models"), name="models")

# OpenCV's built-in AI model to detect and block faces from being tracked
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

@app.get("/")
async def get_dashboard():
    try:
        with open("index.html", "r", encoding="utf-8") as f:
            return HTMLResponse(f.read())
    except Exception as e:
        return HTMLResponse(f"<h3>Critical File Missing: index.html - {str(e)}</h3>", status_code=500)

@app.get("/api/catalog")
async def get_catalog():
    catalog = {}
    try:
        if os.path.exists("models"):
            for grade in os.listdir("models"):
                grade_path = os.path.join("models", grade)
                if os.path.isdir(grade_path):
                    catalog[grade] = {}
                    for subject in os.listdir(grade_path):
                        subject_path = os.path.join(grade_path, subject)
                        if os.path.isdir(subject_path):
                            files = [f for f in os.listdir(subject_path) if f.endswith(('.glb', '.gltf'))]
                            catalog[grade][subject] = files
    except Exception as e:
        pass
    return catalog

@app.websocket("/ws")
async def ai_tracking_engine(websocket: WebSocket):
    await websocket.accept()
    
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    if cap.isOpened():
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, 30)
    
    # Butter-smooth Kinematics
    smoothed_x, smoothed_y = 0.5, 0.5
    smoothed_area = 5000
    alpha = 0.15
    
    try:
        while True:
            data = {"detected": False, "zoom_active": False}
            
            if cap.isOpened():
                success, frame = cap.read()
                if success:
                    frame = cv2.flip(frame, 1)
                    
                    # --- AI FACE ERASER MODULE ---
                    # Converts frame to grayscale for face detection
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    faces = face_cascade.detectMultiScale(gray, 1.3, 5)
                    
                    # Create a blank mask that allows everything (255)
                    face_exclusion_mask = np.ones(frame.shape[:2], dtype="uint8") * 255
                    
                    # Draw black boxes (0) over detected faces & necks so they are ignored
                    for (x, y, w, h) in faces:
                        cv2.rectangle(face_exclusion_mask, (x - 30, y - 50), (x + w + 30, y + h + 100), 0, -1)
                        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
                        cv2.putText(frame, "FACE IGNORED", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

                    # --- SKIN DETECTION MODULE ---
                    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
                    lower_skin = np.array([0, 30, 60], dtype="uint8")
                    upper_skin = np.array([20, 150, 255], dtype="uint8")
                    skin_mask = cv2.inRange(hsv, lower_skin, upper_skin)
                    
                    # Apply Face Eraser to Skin Mask
                    final_mask = cv2.bitwise_and(skin_mask, face_exclusion_mask)
                    
                    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (7, 7))
                    final_mask = cv2.morphologyEx(final_mask, cv2.MORPH_OPEN, kernel)
                    final_mask = cv2.morphologyEx(final_mask, cv2.MORPH_CLOSE, kernel)
                    
                    contours, _ = cv2.findContours(final_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                    
                    if contours:
                        valid_contours = [c for c in contours if cv2.contourArea(c) > 4000]
                        if valid_contours:
                            hand_contour = max(valid_contours, key=cv2.contourArea)
                            M = cv2.moments(hand_contour)
                            
                            if M["m00"] != 0:
                                cX = int(M["m10"] / M["m00"])
                                cY = int(M["m01"] / M["m00"])
                                
                                smoothed_x = (alpha * (cX / frame.shape[1])) + ((1 - alpha) * smoothed_x)
                                smoothed_y = (alpha * (cY / frame.shape[0])) + ((1 - alpha) * smoothed_y)
                                
                                data["detected"] = True
                                data["x"] = smoothed_x
                                data["y"] = smoothed_y
                                
                                # --- ZOOM GESTURE (Fingers Spread) ---
                                hull = cv2.convexHull(hand_contour, returnPoints=False)
                                if len(hull) > 3:
                                    defects = cv2.convexityDefects(hand_contour, hull)
                                    if defects is not None:
                                        finger_gaps = 0
                                        for i in range(defects.shape[0]):
                                            s, e, f, d = defects[i, 0]
                                            start = tuple(hand_contour[s][0])
                                            end = tuple(hand_contour[e][0])
                                            far = tuple(hand_contour[f][0])
                                            
                                            a = math.sqrt((end[0] - start[0])**2 + (end[1] - start[1])**2)
                                            b = math.sqrt((far[0] - start[0])**2 + (far[1] - start[1])**2)
                                            c = math.sqrt((end[0] - far[0])**2 + (end[1] - far[1])**2)
                                            
                                            angle = math.acos((b**2 + c**2 - a**2) / (2 * b * c + 1e-5)) * 57.29
                                            if angle <= 85:
                                                finger_gaps += 1
                                        
                                        if finger_gaps >= 2:
                                            data["zoom_active"] = True
                                            smoothed_area = (alpha * cv2.contourArea(hand_contour)) + ((1 - alpha) * smoothed_area)
                                            data["zoom_distance"] = smoothed_area
                                
                                cv2.drawContours(frame, [hand_contour], -1, (0, 255, 0), 2)
                                cv2.circle(frame, (int(smoothed_x * frame.shape[1]), int(smoothed_y * frame.shape[0])), 10, (255, 0, 0), -1)
                    
                    try:
                        cv2.putText(frame, "TEACHER MODE ACTIVE", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                        cv2.imshow('AI Vision Pipeline Viewport', frame)
                        if cv2.waitKey(1) & 0xFF == 27:
                            break
                    except Exception:
                        pass
            
            await websocket.send_json(data)
            # Remove any local blocking by yielding control perfectly
            import asyncio
            await asyncio.sleep(0.01)
            
    except WebSocketDisconnect:
        pass
    finally:
        if cap.isOpened():
            cap.release()
        cv2.destroyAllWindows()

def open_ui():
    print("\n[SUCCESS] Launching Browser Interface...\n")
    webbrowser.open("http://127.0.0.1:8000")

if __name__ == "__main__":
    print("[AI ENGINE] Starting Final Production Build...")
    # Using Threading Timer instead of asyncio event loop fixes the deprecation warning 100%
    timer = threading.Timer(1.5, open_ui)
    timer.start()
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="error")