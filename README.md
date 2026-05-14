# OpenCV-Fruit-Ninja-Clone

### A computer vision-based game where you control the gameplay using real-time hand gestures.

## 📌 Project Overview
This project is an interactive arcade-style game built entirely in Python. Instead of using a mouse or keyboard, the player uses their hand to interact with falling objects on the screen. 

The game utilizes a webcam and AI-powered hand tracking to detect finger positions. The goal is to "slice" or collect specific items to increase your score while carefully avoiding the bombs to save your lives.

## 🚀 Key Features
- **Real-time AI Hand Tracking:** Powered by **MediaPipe** to accurately track hand landmarks through the webcam.
- **Collision Detection:** Custom mathematical logic to calculate the distance between the player's fingers and the moving objects on the screen.
- **Game Mechanics:** Includes a dynamic scoring system, a limited number of lives, and "Game Over" logic.
- **Custom Assets:** Supports custom PNG images for the game items and bombs.

## 🛠️ Tech Stack & Libraries
- **Language:** Python
- **Computer Vision:** OpenCV (`cv2`)
- **AI / Tracking:** MediaPipe
- **Logic & Math:** NumPy, Random, Collections

## 🎮 How to Play
1. Install the required libraries: `pip install opencv-python mediapipe numpy`
2. Ensure you have a working webcam.
3. Run the script: `python main.py`
4. Use your index finger to interact with the objects on the screen. Collect the items for points and dodge the bombs!
   <br>
https://github.com/user-attachments/assets/a0e829f0-5055-4c52-8fd1-554fe6c92ee7
---
*A fun project showcasing the integration of Computer Vision with interactive software development.*



