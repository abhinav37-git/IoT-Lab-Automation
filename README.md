# Smart IoT Lab Automation with RFID-Based Attendance System

## Overview

The **Smart IoT Lab Automation with RFID-Based Attendance System** is a comprehensive solution designed to enhance power efficiency, security, student monitoring, inventory management, and attendance tracking in a laboratory setting. Combining IoT and RFID technologies, this project significantly reduces manual intervention while improving efficiency and user experience. 

This project achieved:
- A **30% reduction in power consumption**.
- Enhanced security and streamlined lab operations.
- Recognition with the **Third Prize** at the University Projects Expo, competing against 400 teams.

## Features

### Lab Automation
- **Power Efficiency**: Automated monitoring and reduction of power usage.
- **Security**: Enhanced security with minimal manual intervention.
- **Student Monitoring**: Real-time tracking of student activities within the lab.
- **Inventory Management**: Efficient tracking and management of lab inventory.

### RFID-Based Attendance System
- **RFID Card Reader**: Integration with NodeMCU to read unique RFID card/tag IDs.
- **Real-Time Data Transfer**: Attendance data sent from NodeMCU to the Django backend.
- **Database Management**: Django backend stores attendance data for easy retrieval and analysis.
- **Web Interface**: User-friendly interface for managing attendance records and generating reports.

## Technologies Used

- **IoT Controllers**: Programmed using C++ (e.g., Arduino, ESP8266).
- **Server-Side**: Python 3 with Django for backend operations.
- **Blynk IoT Cloud**: For web interface design and automation configuration via API calls.
- **RFID Technology**: NodeMCU with an RFID reader for attendance tracking.

## System Architecture

The system architecture consists of:
1. IoT controllers interfacing with lab equipment and sensors.
2. A central server for processing data and automating tasks.
3. Blynk IoT Cloud for a user-friendly monitoring and control interface.
4. An RFID-based attendance system integrating NodeMCU and Django for real-time attendance tracking.

---

## Getting Started

### Prerequisites

#### For Lab Automation
- IoT Controllers (e.g., Arduino, ESP8266).
- A server with Python 3 installed.
- A Blynk IoT Cloud account.

#### For RFID Attendance System
- **NodeMCU Board**: ESP8266-based development board.
- **RFID Card Reader**: Capable of reading unique IDs from RFID cards or tags.
- **RFID Cards or Tags**: Each student or participant should have a unique RFID card/tag.
- **Django Framework**: For backend operations.

---

## Setup Instructions

### Lab Automation Setup
1. **Hardware Configuration**:
   - Connect sensors and lab equipment to IoT controllers.
2. **Server Setup**:
   - Install Python 3 and necessary libraries.
   - Integrate with Blynk IoT Cloud for interface design.
3. **Software Deployment**:
   - Program IoT controllers with automation logic using C++.
   - Deploy the server to manage automation tasks and data.

### RFID Attendance System Setup
1. **Hardware Setup**:
   - Connect the RFID card reader to the NodeMCU board.
   - Ensure the NodeMCU board is connected to the internet.
2. **Django Backend Setup**:
   - Install Python and Django:  
     ```bash
     pip install django
     ```
   - Create a new Django project:
     ```bash
     django-admin startproject attendance_system
     ```
   - Create a Django app for RFID attendance:
     ```bash
     cd attendance_system && python manage.py startapp rfid_attendance
     ```
   - Configure database settings and create models for attendance tracking.
   - Implement API endpoints for receiving RFID data from NodeMCU.
3. **NodeMCU Firmware Setup**:
   - Install the Arduino IDE and ESP8266 board package.
   - Configure the Arduino IDE for NodeMCU (select the appropriate board and port).
   - Install libraries for RFID card reading and Wi-Fi connectivity.
   - Write firmware code to read RFID card data and send it to the Django backend.
4. **Deploy and Test**:
   - Deploy the Django backend to a web server or host locally.
   - Upload the firmware to NodeMCU.
   - Test by swiping RFID cards and verifying data in the Django backend.

---

## Usage

1. **Lab Automation**:
   - Monitor and control lab systems through the Blynk IoT Cloud interface.
   - Automate tasks like power management, security, and inventory tracking.

2. **RFID Attendance**:
   - Administrators can access the Django web interface to:
     - Manage attendance records.
     - View and generate reports.
   - When participants swipe their RFID cards, the NodeMCU sends data to the Django backend for recording.

---

## Enhancements and Future Scope

- **Authentication**: Add user authentication for enhanced security.
- **Notifications**: Real-time alerts for attendance and other lab events.
- **Integration**: Connect with email or messaging platforms for automated communication.
- **Mobile Application**: Provide a convenient interface for administrators and users.
- **Data Visualization**: Generate interactive reports and insights from attendance and lab data.

---

## Components Required

### Hardware
- IoT Controllers (Arduino, ESP8266).
- Sensors and actuators for lab automation.
- NodeMCU board.
- RFID card reader and RFID cards/tags.

### Software
- Python 3.
- Django framework.
- Arduino IDE.
- Blynk IoT Cloud account.