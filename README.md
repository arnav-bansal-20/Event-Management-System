# 🎉 Event Management System

An **Event Management System** designed to simplify the process of organizing, scheduling, and managing events. This project provides an intuitive interface for creating, updating, viewing, and deleting event records while maintaining them in a structured database. It is suitable for academic projects, event organizers, and anyone looking to learn CRUD operations, database integration, and front-end/back-end communication.

The system allows users to efficiently manage event details such as event name, description, priority, and date. It also displays upcoming events, helping users keep track of their schedules and important activities.

---

## 📖 Features

- ➕ Add new events
- 📅 View all scheduled events
- ✏️ Update existing event details
- ❌ Delete events
- ⭐ Assign event priorities
- ⏰ Display upcoming events
- 🔍 Search and organize event records
- 💾 Database storage for persistent data
- 📱 Simple and user-friendly interface

---

## 🛠 Technologies Used

- **C**: Core data structures (Hash Table for $O(1)$ search, Min-Heap Priority Queue for event scheduling)
- **Python (Flask)**: REST API backend and `ctypes` foreign function interface to the compiled C engine
- **HTML5 / CSS3 / JavaScript**: Modern, responsive web user interface
- **File Storage**: Persistent storage (`events.db`)

---

## 📂 Project Structure

```
Event-Management-System/
│
├── app.py                # Flask web server & C shared library bridge (ctypes)
├── build.sh              # Compilation script for macOS/Linux
├── build.bat             # Compilation script for Windows
├── main.c                # Interactive C CLI program
├── functions.c           # Core C engine (Hash Table, Priority Queue, I/O)
├── structures.h          # C data structure definitions
├── events.db             # Persistent database file
├── index.html            # Web dashboard interface
├── style.css             # Glassmorphic UI stylesheet
├── static/
│   ├── index.html        # Web dashboard interface
│   ├── script.js         # Frontend interactivity & REST API client
│   └── style.css         # UI stylesheet
├── requirements.txt      # Python package dependencies (Flask)
├── .gitignore            # Git exclusion rules
└── README.md
```

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/arnav-bansal-20/Event-Management-System.git
cd Event-Management-System
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Build the C Engine

- **On macOS / Linux**:
  ```bash
  chmod +x build.sh
  ./build.sh
  ```
- **On Windows**:
  ```cmd
  build.bat
  ```

### 4. Run the Application

- **Web Application**:
  ```bash
  python3 app.py
  ```
  Open your browser and navigate to `http://127.0.0.1:5000`.

- **Terminal CLI Application**:
  ```bash
  ./event_system        # On macOS/Linux
  event_system.exe      # On Windows
  ```

---

## 🎯 Learning Objectives

This project demonstrates:

- CRUD (Create, Read, Update, Delete) operations
- Database integration
- Event scheduling and management
- Front-end and back-end communication
- Basic API handling
- File and data management
- Practical implementation of data structures

---

## ✨ Highlights

- Clean and responsive user interface
- Easy-to-understand code structure
- Persistent event storage
- Beginner-friendly project
- Suitable for academic demonstrations and mini projects

---

## 📌 Future Enhancements

- User authentication and login
- Email and SMS reminders
- Calendar integration
- Event categories and filtering
- Dashboard with analytics
- Export events to PDF or CSV
- Mobile-friendly responsive design
- Multi-user support

---

## 🤝 Contributing

Contributions are welcome! Feel free to fork this repository, improve the project, fix bugs, or add new features by creating a pull request.

---

## 📄 License

This project is intended for educational purposes. You are free to use, modify, and enhance it for learning and academic work.

---

## 👨‍💻 Author

**Arnav**

Computer Science Student | Web Development | Artificial Intelligence | C Programming

---

## ⭐ Support

If you found this project useful, please consider giving it a **⭐ Star** on GitHub. Your support helps motivate future improvements and new projects.

Happy Coding! 🚀
