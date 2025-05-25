ParkVision - An AI Parking Management Application
This project is a Smart Parking Management System built using a Raspberry Pi 5, Camera Module 3, OpenCV, React Native and Django. The system provides real-time detection of parking spot occupancy and automatic recognition of vehicle license plates. It is designed to streamline parking management, enhance user experience, and minimize traffic congestion and time spent searching for parking.
Demo
If you want to see the system in action, you can watch the demo video here.
Features
Real-time parking spot detection using YOLOv8 and OpenCV.
License plate recognition using computer vision and Levenshtein distance for verification.
Integration with Django for backend management and database operations.
Notifications for unauthorized parking and parking status updates.
Parking history tracking for each vehicle.
Reservation of parking spots for up to 60 minutes from the time of request.
Automatic generation of parking reports for admins.
Location-based detection of the nearest available parking spots.
Live video stream to the admin interface using WebSocket (React Native).

Built With

# 💻 Tech Stack:
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54) ![JavaScript](https://img.shields.io/badge/javascript-%23323330.svg?style=for-the-badge&logo=javascript&logoColor=%23F7DF1E) ![Django](https://img.shields.io/badge/django-%23092E20.svg?style=for-the-badge&logo=django&logoColor=white) ![DjangoREST](https://img.shields.io/badge/DJANGO-REST-ff1709?style=for-the-badge&logo=django&logoColor=white&color=ff1709&labelColor=gray) ![NPM](https://img.shields.io/badge/NPM-%23CB3837.svg?style=for-the-badge&logo=npm&logoColor=white) ![OpenCV](https://img.shields.io/badge/opencv-%23white.svg?style=for-the-badge&logo=opencv&logoColor=white) ![React](https://img.shields.io/badge/react-%2320232a.svg?style=for-the-badge&logo=react&logoColor=%2361DAFB) ![React Native](https://img.shields.io/badge/react_native-%2320232a.svg?style=for-the-badge&logo=react&logoColor=%2361DAFB) ![Socket.io](https://img.shields.io/badge/Socket.io-black?style=for-the-badge&logo=socket.io&badgeColor=010101) ![Sequelize](https://img.shields.io/badge/Sequelize-52B0E7?style=for-the-badge&logo=Sequelize&logoColor=white) ![Git](https://img.shields.io/badge/git-%23F05033.svg?style=for-the-badge&logo=git&logoColor=white) ![GitHub](https://img.shields.io/badge/github-%23121011.svg?style=for-the-badge&logo=github&logoColor=white) ![Raspberry Pi](https://img.shields.io/badge/-Raspberry_Pi-C51A4A?style=for-the-badge&logo=Raspberry-Pi) ![PyTorch](https://img.shields.io/badge/PyTorch-%23EE4C2C.svg?style=for-the-badge&logo=PyTorch&logoColor=white) ![NumPy](https://img.shields.io/badge/numpy-%23013243.svg?style=for-the-badge&logo=numpy&logoColor=white) ![Pandas](https://img.shields.io/badge/pandas-%23150458.svg?style=for-the-badge&logo=pandas&logoColor=white) ![Matplotlib](https://img.shields.io/badge/Matplotlib-%23ffffff.svg?style=for-the-badge&logo=Matplotlib&logoColor=black) ![nVIDIA](https://img.shields.io/badge/cuda-000000.svg?style=for-the-badge&logo=nVIDIA&logoColor=green) ![Context-API](https://img.shields.io/badge/Context--Api-000000?style=for-the-badge&logo=react) ![Expo](https://img.shields.io/badge/expo-1C1E24?style=for-the-badge&logo=expo&logoColor=#D04A37)

Project Structure
main.py: Handles video processing and object detection (vehicles, license plate, and plate’s numbers).
initial.py: Script for marking parking spots manually and initializing a parking lot in the database.
Django Backend: Manages API endpoints, WebSocket, and database interactions.
React Native App: Displays parking lots status in real time and manages user interactions.
settings.py: Configures database, authentication, and WebSocket settings.
Installation
Prerequisites
Raspberry Pi 5 with Camera Module 3.
Python 3.x installed on the Raspberry Pi.
Django installed (pip install django).
React Native setup for the frontend.
Setup Instructions
Clone this repository:
git clone <repository-url>
Install Python dependencies:
pip install -r requirements.txt
Open a terminal on your Raspberry Pi and set up a Django server:
python manage.py makemigrations
python manage.py migrate
Run the Django server:
daphne -b 0.0.0.0 -p 8000 parkingProject.asgi:application
For initializing a new parking lot, go to the parkingProject folder:
python3 -m parkingApp.initial


Usage
Access the React Native app to monitor the parking lot in real-time.
Admin can view the live video stream and receive notifications for authorized and unauthorized parking.
Parking spot statuses update automatically in the database.
Future Improvements
Support for multiple parking lots.
Automatic payment processing for parking duration.
Enhanced recognition accuracy in low light conditions.
Expanded vehicle support (e.g., bicycles, scooters).
