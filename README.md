# TaskFlow - Team Task Manager

TaskFlow is a production-style SaaS Team Collaboration Platform built with a modern web stack. It provides a robust, responsive, and intuitive interface for managing projects, tasks, and team members.

## 🚀 Features

* **Authentication:** Secure signup and login with JWT access and refresh tokens.
* **Role-Based Access Control:** Differentiate between `admin` and `member` roles for access control.
* **Dashboard:** At-a-glance analytics of total projects, pending tasks, overdue tasks, and recent activities.
* **Project Management:** Create, view, update, and delete projects. Manage project members and assign roles within the project.
* **Task Management (Kanban):** Create tasks within projects, assign them to members, set priorities, and track them across a Kanban-style board (To do, In progress, Done).
* **"My Tasks" View:** A personalized view of tasks assigned to or created by the logged-in user.
* **Activity Logging:** Comprehensive tracking of changes (e.g., status updates, member additions) across the platform.
* **Notifications:** Real-time-style notifications for task assignments, updates, project invites, and approaching deadlines.
* **Comments & Attachments:** Collaborate on specific tasks by adding comments and uploading relevant files.

## 💻 Tech Stack

### Frontend
* **Framework:** React + Vite
* **Routing:** React Router DOM
* **Styling:** Vanilla CSS + custom design tokens
* **HTTP Client:** Axios

### Backend
* **Framework:** FastAPI (Python)
* **Database:** PostgreSQL
* **ORM:** SQLAlchemy
* **Data Validation:** Pydantic V2
* **Authentication:** Passlib (Bcrypt) + python-jose (JWT)

## 🛠️ Prerequisites

* Node.js (v18+)
* Python (3.9+)
* PostgreSQL server running locally or remotely

## 🚦 Local Development Setup

### 1. Database Setup

Create a PostgreSQL database for the project:
```sql
CREATE DATABASE "team-task-manager";
```

### 2. Backend Setup

Navigate to the `backend` directory, create a virtual environment, and install dependencies:

```bash
cd backend
python -m venv venv
# Activate the virtual environment
# Windows:
.\venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

pip install -r requirements.txt
```

Create a `.env` file in the `backend` directory and add your configurations:

```env
DATABASE_URL=postgresql://postgres:yourpassword@localhost/team-task-manager
SECRET_KEY=your_super_secret_64_char_hex_key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```
> **Note:** Generate a strong secret key using `python -c "import secrets; print(secrets.token_hex(32))"`

Run the backend development server:

```bash
uvicorn backend:app --reload
```
The API will be available at `http://localhost:8000`.

### 3. Frontend Setup

Navigate to the `frontend` directory and install dependencies:

```bash
cd frontend
npm install
```

Create a `.env.local` file in the `frontend` directory pointing to your local backend:

```env
VITE_API_URL=http://localhost:8000
```

Run the frontend development server:

```bash
npm run dev
```
The app will be available at `http://localhost:5173`.

## ☁️ Deployment (Railway)

This project is configured to be easily deployable on [Railway](https://railway.app/).

1. **Database:** Provision a PostgreSQL database on Railway.
2. **Backend Service:**
   * Deploy the backend directory.
   * Add the following environment variables:
     * `DATABASE_URL`: (Use the connection string from your provisioned Postgres)
     * `SECRET_KEY`: (A strong generated key)
   * Set the Start Command (or use the provided `Procfile`/`Dockerfile` if applicable).
3. **Frontend Service:**
   * Deploy the frontend directory.
   * Add the environment variable:
     * `VITE_API_URL`: (The URL of your deployed backend service)

## 📁 Project Structure

```
Team-task-manager/
├── backend/
│   ├── backend.py       # Main FastAPI application, models, and routes
│   ├── requirements.txt # Python dependencies
│   ├── .env             # Backend environment variables
│   └── uploads/         # Directory for file attachments
├── frontend/
│   ├── src/
│   │   ├── main.jsx     # Main React application, components, and router
│   │   ├── index.css    # Global styles and design tokens
│   │   └── api.js       # Axios configuration
│   ├── vite.config.js   # Vite configuration
│   ├── package.json     # Node dependencies
│   └── .env.local       # Local frontend environment variables
├── .gitignore           # Git ignore rules
└── README.md            # Project documentation
```

## 🔒 Security Features Built-In

* Passwords are hashed using bcrypt before storage.
* Short-lived JWT Access Tokens combined with longer-lived Refresh Tokens.
* SQL Injection protection via SQLAlchemy ORM.
* Safe parsing and validation of incoming data via Pydantic.
* Filenames sanitized on upload to prevent directory traversal.
* Role-based checks on sensitive endpoints (e.g., project deletion, member management).
