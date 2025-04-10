# Project Management Portal

A comprehensive web application for managing projects and tasks with a chatbot assistant.

## Features

- **User Management**
  - Registration and login system
  - User profiles with role-based permissions

- **Project Management**
  - Create and manage projects
  - Invite team members with different roles (admin, manager, member)
  - Project dashboard with statistics

- **Task Management**
  - Create, edit, and delete tasks
  - Assign tasks to team members
  - View tasks in list or Kanban board format
  - Drag-and-drop functionality for status updates

- **Chatbot Assistant**
  - Natural language queries about tasks and projects
  - Get task counts and summaries
  - View task assignments and statuses
  - Project manager-specific information

## Technical Implementation

- **Backend**: Flask web framework with SQLAlchemy ORM
- **Frontend**: HTML/CSS with Bootstrap 5 and JavaScript
- **Database**: SQLite (can be easily upgraded to PostgreSQL or MySQL)
- **Authentication**: Flask-Login for secure user sessions

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/project-portal.git
   cd project-portal
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```
   pip install flask flask-sqlalchemy flask-login flask-bcrypt flask-wtf flask-migrate
   ```

4. Run the application:
   ```
   python app.py
   ```

5. Access the application at http://localhost:5000

## Usage

1. Register a new account
2. Create a new project
3. Invite team members to collaborate
4. Create and assign tasks
5. Use the Kanban board to track task progress
6. Ask the chatbot for quick status updates

## Project Structure

```
project_portal/
├── app.py                  # Main Flask application
├── extensions.py           # Flask extensions
├── models.py               # Database models
├── config.py               # Configuration settings
├── utils/                  # Helper functions
├── routes/                 # Route handlers
├── static/                 # Static assets (CSS, JS)
├── templates/              # HTML templates
└── instance/               # Instance-specific data
```

## Differences from a Basic Kanban Board

This project management portal extends beyond a basic Kanban board by adding:

1. **Multi-project support** - Create and manage multiple projects
2. **Team collaboration** - Invite users with different permission levels
3. **Comprehensive task management** - Assign tasks, set priorities, track due dates
4. **Chatbot assistant** - Get quick updates without navigating the UI
5. **Role-based permissions** - Control who can do what within each project

## License

MIT
