
from extensions import db
from models import Task, Project, User
from flask_login import current_user
from datetime import datetime


def get_project_tasks(project_id):
    """Get all tasks for a project"""
    return Task.query.filter_by(project_id=project_id).all()


def get_tasks_by_status(project_id):
    """Get tasks grouped by status for a project"""
    tasks = get_project_tasks(project_id)
    task_columns = {
        'To Do': [],
        'In Progress': [],
        'Done': []
    }

    for task in tasks:
        if task.status in task_columns:
            task_columns[task.status].append(task)

    return task_columns


def create_task(project_id, title, description=None, status='To Do', priority='Medium', assignee_id=None,
                due_date=None):
    """Create a new task in a project"""
    # Validate project exists
    project = Project.query.get(project_id)
    if not project:
        raise ValueError("Project not found")

    # Validate assignee if provided
    if assignee_id:
        assignee = User.query.get(assignee_id)
        if not assignee:
            raise ValueError("Assignee not found")

        # Check if assignee is a member of the project
        if project not in assignee.projects:
            raise ValueError("Assignee is not a member of this project")

    # Create task
    task = Task(
        title=title,
        description=description,
        status=status,
        priority=priority,
        due_date=due_date,
        project_id=project_id,
        creator_id=current_user.id,
        assignee_id=assignee_id
    )

    db.session.add(task)
    db.session.commit()

    return task


def update_task_status(task_id, new_status):
    """Update the status of a task"""
    # Validate status
    if new_status not in ['To Do', 'In Progress', 'Done']:
        raise ValueError("Invalid status")

    # Get task
    task = Task.query.get(task_id)
    if not task:
        raise ValueError("Task not found")

    # Update status
    task.status = new_status
    task.updated_at = datetime.utcnow()
    db.session.commit()

    return task


def assign_task(task_id, assignee_id=None):
    """Assign a task to a user"""
    # Get task
    task = Task.query.get(task_id)
    if not task:
        raise ValueError("Task not found")

    # Validate assignee if provided
    if assignee_id:
        assignee = User.query.get(assignee_id)
        if not assignee:
            raise ValueError("Assignee not found")

        # Check if assignee is a member of the project
        project = Project.query.get(task.project_id)
        if project not in assignee.projects:
            raise ValueError("Assignee is not a member of this project")

    # Update assignee
    task.assignee_id = assignee_id
    task.updated_at = datetime.utcnow()
    db.session.commit()

    return task