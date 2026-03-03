Toop Sawari

Toop Sawari is a lightweight taxi booking system built with Python and SQLite3. The project enables users to book rides, manage drivers, calculate fares, and maintain trip records efficiently. It is designed for simplicity and serves as a solid academic or beginner-friendly backend project.

Features

User registration and login system

Taxi booking workflow

Driver management

Automatic fare calculation

Basic map handling

SQLite3 database integration

Admin module support

Modular Python file structure

Tech Stack

Language: Python 3

Database: SQLite3

Architecture: Modular Python scripts

Interface: CLI / basic GUI (depending on implementation)

Project Structure
Toop_Sawari/
├── admin.py
├── assets.py
├── customer.py
├── database.py
├── driver.py
├── farecalculation.py
├── login.py
├── main.py
├── map.py
├── register.py
├── taxi.db
├── backgrounds/
└── __pycache__/
Getting Started
Prerequisites

Python 3.x installed

No external database setup required

Installation
git clone https://github.com/samyamx/Toop_Sawari.git
cd Toop_Sawari
Run the Project
python main.py
Database

The project uses SQLite3, a lightweight file-based database stored as taxi.db. No separate database server is required.

Future Improvements

Web or GUI interface

Real-time GPS tracking

Online payment integration

REST API support

Improved user interface
