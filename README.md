# AI-EdTech-Immersive-Lab
Real-time Computer Vision Hand-Tracking for 3D Educational Simulations

🚀 Overview

The AI-EdTech Immersive Lab bridges the gap between static educational content and interactive technology. By leveraging real-time computer vision, this project allows teachers to manipulate 3D educational models (GLB/GLTF) directly using hand gestures, providing a seamless and highly engaging way to explain complex History or Science concepts.

🌟 Key Features

Smart Teacher-Zone Isolation: An integrated AI Face-Eraser module filters out facial and bodily movements, ensuring the 3D model only responds to deliberate hand gestures.

Intuitive Gesture Control: Uses real-time geometric analysis to detect hand positioning and spread (pinch-to-zoom) gestures.

Zero-Dependency Core: Built using optimized OpenCV algorithms, eliminating the need for heavy, error-prone AI frameworks.

Dynamic Content Loader: Automatically organizes and fetches 3D models based on your local directory structure.

🛠 Tech Stack

Computer Vision: OpenCV (Haar Cascades, Contour Analysis, Skin Segmentation)

Backend: FastAPI, Uvicorn

Frontend: Three.js, WebGL, WebSocket (for real-time streaming)

📁 Folder Structure
To organize your educational content, use the following directory structure inside the models/ folder:

Plaintext
models/

├── Grade_9/

│   ├── Physics/

│   │   └── atom_model.glb

│   └── Biology/

│       └── heart_model.glb

└── Grade_10/

    └── History/
    
        └── historical_artifact.glb
        
🚀 How to Run

Clone the repository:

Bash

git clone https://github.com/ismailiqbal2773/AI-EdTech-Immersive-Lab.git

cd Interactive-3D-AI-HistoryScience-Sandbox

Activate your environment:

Bash
myenv\Scripts\activate
Launch the Application:
Run the application using the provided launcher or the command:

Bash
python main.py
The application will automatically open in your default browser at http://127.0.0.1:8000.

✋ Hand Gesture Guide
Rotation & Movement: Keep your palm open and move it within the frame to rotate the 3D model. The system intelligently ignores your face and torso for a smoother experience.

Zoom Control: Use a "Pinch" gesture (bringing thumb and index finger together) or "Spread" (opening the palm) to scale the 3D model size dynamically.

Stable State: When your hand is removed from the camera's view, the model smoothly stops at its last position, ensuring no sudden glitches.

🎓 About the Project
This project is an exploration of Human-Computer Interaction (HCI). It utilizes Color-based Segmentation and Geometric Feature Extraction to interpret human intent. The Face-Eraser logic is a custom implementation of Haar Cascade classifiers, preventing interference during live presentations.
