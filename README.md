# 🚗 ParkVision – AI-Based Smart Parking Management System

> An intelligent system for managing and monitoring parking lots in real-time.

---

## 🧠 Overview

**ParkVision** is a Smart Parking Management System built using **Raspberry Pi 5**, **Camera Module 3**, **OpenCV**, **React Native**, and **Django**.  
The system offers **real-time detection of parking spot occupancy** and **automatic vehicle license plate recognition**.

Its primary goal is to **optimize parking management**, **enhance user experience**, and **reduce traffic congestion and parking search time**.

---

## 🎬 Demo

Want to see the system in action?  
📺 **[Click here to watch the demo video](#)**

---

## 🚀 Features

- 🎯 **Real-time parking spot detection** using YOLOv8 + OpenCV  
- 🔍 **License plate recognition** with Levenshtein distance validation  
- 🧠 **Django-powered backend** for logic and database management  
- 🚨 **Notifications** for unauthorized parking and updates on spot status  
- 📊 **Parking history tracking** per vehicle  
- ⏱️ **Spot reservation** for up to 60 minutes  
- 🧾 **Automatic report generation** for admins  
- 📍 **Location-based nearest spot detection**  
- 🔴 **Live video stream** to the admin panel via WebSocket (React Native)

---

## 🛠️ Built With

- [Python](https://www.python.org/) – Core programming language  
- [OpenCV](https://opencv.org/) – Image processing and detection  
- [YOLOv8](https://github.com/ultralytics/ultralytics) – Object detection model  
- [Django](https://www.djangoproject.com/) – Web framework for backend  
- [React Native](https://reactnative.dev/) – Cross-platform mobile frontend  
- [Raspberry Pi 5 + Camera Module 3](https://www.raspberrypi.com/) – Hardware platform

---

## 🧾 Project File Descriptions

- `main.py` – Main video processing loop. Captures frames, runs YOLO detection, checks license plates, updates spot states, and triggers alerts.
- `initial.py` – GUI-based tool to manually define parking spot regions on a still image and save them to the database.
- `settings.py` – Django settings, including database configuration, static files, CORS, and ASGI settings.
- `urls.py` – Route manager that connects Django views to endpoint URLs.
- `models.py` – Django models representing lots, spots, vehicles, users, and parking sessions.
- `views.py` – Backend logic handling parking reservations, releases, license recognition, and live stream frame serving.
- `consumers.py` – Django Channels WebSocket logic to stream video frames in real-time.
- `utils/ocr.py` – Handles license plate extraction and Levenshtein-based matching.
- `utils/spot_utils.py` – Parking spot validation, IOU calculations, and boundary checks.
- `media/` – Directory where uploaded vehicle images and video frames are saved.
- `parkingApp/templates/` – Optional: HTML templates if the backend needs web admin views.

---

## 📌 Future Improvements (Optional Section)

- 📡 Integrate automatic payment via license plate recognition  
- 🌧️ Improve detection accuracy under extreme weather or lighting  
- 🏢 Support for multi-lot management and large-scale deployments  
- 📱 Add user-facing app for spot reservation and live updates

---

## 🙌 Acknowledgments

Special thanks to all contributors, testers, and researchers who helped shape this project.

---

# 💻 Tech Stack:
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54) ![JavaScript](https://img.shields.io/badge/javascript-%23323330.svg?style=for-the-badge&logo=javascript&logoColor=%23F7DF1E) ![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white) ![DjangoREST](https://img.shields.io/badge/DJANGO-REST-ff1709?style=for-the-badge&logo=django&logoColor=white&color=ff1709&labelColor=gray) ![NPM](https://img.shields.io/badge/NPM-%23CB3837.svg?style=for-the-badge&logo=npm&logoColor=white) ![OpenCV](https://img.shields.io/badge/opencv-%23white.svg?style=for-the-badge&logo=opencv&logoColor=white) ![React](https://img.shields.io/badge/react-%2320232a.svg?style=for-the-badge&logo=react&logoColor=%2361DAFB) ![React Native](https://img.shields.io/badge/react_native-%2320232a.svg?style=for-the-badge&logo=react&logoColor=%2361DAFB) ![Socket.io](https://img.shields.io/badge/Socket.io-black?style=for-the-badge&logo=socket.io&badgeColor=010101) ![Sequelize](https://img.shields.io/badge/Sequelize-52B0E7?style=for-the-badge&logo=Sequelize&logoColor=white) ![Git](https://img.shields.io/badge/git-%23F05033.svg?style=for-the-badge&logo=git&logoColor=white) ![GitHub](https://img.shields.io/badge/github-%23121011.svg?style=for-the-badge&logo=github&logoColor=white) ![Raspberry Pi](https://img.shields.io/badge/-Raspberry_Pi-C51A4A?style=for-the-badge&logo=Raspberry-Pi) ![PyTorch](https://img.shields.io/badge/PyTorch-%23EE4C2C.svg?style=for-the-badge&logo=PyTorch&logoColor=white) ![NumPy](https://img.shields.io/badge/numpy-%23013243.svg?style=for-the-badge&logo=numpy&logoColor=white) ![Pandas](https://img.shields.io/badge/pandas-%23150458.svg?style=for-the-badge&logo=pandas&logoColor=white) ![Matplotlib](https://img.shields.io/badge/Matplotlib-%23ffffff.svg?style=for-the-badge&logo=Matplotlib&logoColor=black) ![nVIDIA](https://img.shields.io/badge/cuda-000000.svg?style=for-the-badge&logo=nVIDIA&logoColor=green) ![Context-API](https://img.shields.io/badge/Context--Api-000000?style=for-the-badge&logo=react) ![Expo](https://img.shields.io/badge/expo-1C1E24?style=for-the-badge&logo=expo&logoColor=#D04A37)

## 🧱 Project Structure

- `main.py` – Handles video processing and object detection (vehicles, license plates, and numbers).
- `initial.py` – Script for marking parking spots manually and initializing a parking lot in the database.
- **Django Backend** – Manages API endpoints, WebSocket, and database interactions.
- **React Native App** – Displays parking lot status in real time and manages user interactions.
- `settings.py` – Configures database, authentication, and WebSocket settings.

---

## ⚙️ Installation

### 📌 Prerequisites

- Raspberry Pi 5 with Camera Module 3  
- Python 3.x installed on the Raspberry Pi  
- Django installed (`pip install django`)  
- React Native setup for the frontend

### 🛠️ Setup Instructions

1. **Clone this repository**
```bash
git clone <repository-url>
```

2. **Install Python dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up Django server**
```bash
python manage.py makemigrations
python manage.py migrate
```

4. **Run the Django server**
```bash
daphne -b 0.0.0.0 -p 8000 parkingProject.asgi:application
```

5. **Initialize a new parking lot**
```bash
cd parkingProject
python3 -m parkingApp.initial
```

---

## 📲 Usage

- Access the **React Native app** to monitor the parking lot in real time  
- Admin can view the **live video stream** and receive notifications for authorized and unauthorized parking  
- **Parking spot statuses** update automatically in the database

---

## 📈 Future Improvements

- 🅿️ Support for multiple parking lots  
- 💳 Automatic payment processing based on parking duration  
- 🌙 Enhanced recognition accuracy in low-light conditions  
- 🛵 Expanded vehicle support (e.g., bicycles, scooters)

