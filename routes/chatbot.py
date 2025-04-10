from flask import Blueprint, render_template, request, jsonify
from flask_login import current_user, login_required
from extensions import db
from models import Task, Project, User
from sqlalchemy import func, and_
import re

chatbot_bp = Blueprint('chatbot', __name__, url_prefix='/chatbot')

@chatbot_bp.route('/')
@login_required
def chatbot():
    return render_template('chatbot.html')

@chatbot_bp.route('/query', methods=['POST'])
@login_required
def process_query():
    data = request.get_json()
    if not data or 'query' not in data:
        return jsonify({'error': 'Missing query'}), 400
    query = data['query'].lower().strip()
    # Process the query and generate a response
    response = process_chatbot_query(query, current_user)
    return jsonify({'response': response})

def process_chatbot_query(query, user):
    """Process a chatbot query and return a response"""
    # Check for task count queries
    if re.search(r'how many tasks (do i have|are assigned to me)', query):
        return get_task_count_response(user)
    # Check for task list queries
    elif re.search(r'what( are| is)? (my|the) tasks', query) or query == "what are these tasks?":
        return get_task_list_response(user)
    # Check for project manager queries
    elif re.search(r'(who is assigned to|what is the status of) (the )?tasks i created', query):
        return get_manager_task_status_response(user)
    # Check for project list queries
    elif re.search(r'what projects (am i on|do i have|am i working on)', query):
        return get_project_list_response(user)
    # Check for help queries
    elif re.search(r'(help|what can you do)', query):
        return get_help_response()
    # Default response for unrecognized queries
    else:
        return "I'm not sure how to answer that. Try asking about your tasks, projects, or task assignments."

def get_task_count_response(user):
    """Get a response about the number of tasks assigned to the user"""
    # Count tasks by status
    todo_count = Task.query.filter_by(assignee_id=user.id, status='To Do').count()
    in_progress_count = Task.query.filter_by(assignee_id=user.id, status='In Progress').count()
    done_count = Task.query.filter_by(assignee_id=user.id, status='Done').count()
    total_count = todo_count + in_progress_count + done_count

    if total_count == 0:
        return "You don't have any tasks assigned to you."

    response = f"You have {total_count} tasks assigned to you: "
    response += f"{todo_count} to do, {in_progress_count} in progress, and {done_count} completed."
    return response

def get_task_list_response(user):
    """Get a response listing the tasks assigned to the user"""
    # Get tasks by status
    todo_tasks = Task.query.filter_by(assignee_id=user.id, status='To Do').all()
    in_progress_tasks = Task.query.filter_by(assignee_id=user.id, status='In Progress').all()

    if not todo_tasks and not in_progress_tasks:
        return "You don't have any active tasks assigned to you."

    response = "Here are your current tasks:\n\n"
    if todo_tasks:
        response += "To Do:\n"
        for task in todo_tasks:
            project = Project.query.get(task.project_id)
            response += f"- {task.title} (Project: {project.name})\n"
        response += "\n"

    if in_progress_tasks:
        response += "In Progress:\n"
        for task in in_progress_tasks:
            project = Project.query.get(task.project_id)
            response += f"- {task.title} (Project: {project.name})\n"
    return response

def get_manager_task_status_response(user):
    """Get a response about tasks created by the user and their assignees"""
    created_tasks = Task.query.filter_by(creator_id=user.id).all()
    if not created_tasks:
        return "You haven't created any tasks."

    task_summary = {}
    for task in created_tasks:
        assignee = User.query.get(task.assignee_id) if task.assignee_id else None
        assignee_name = assignee.username if assignee else "Unassigned"
        if assignee_name not in task_summary:
            task_summary[assignee_name] = {'To Do': [], 'In Progress': [], 'Done': []}
        task_summary[assignee_name][task.status].append(task)

    response = "Here's a summary of the tasks you created:\n\n"
    for assignee, statuses in task_summary.items():
        response += f"{assignee}:\n"
        for status, tasks in statuses.items():
            if tasks:
                response += f"  {status}: {len(tasks)} tasks\n"
                for task in tasks:
                    response += f"    - {task.title}\n"
        response += "\n"
    return response

def get_project_list_response(user):
    """Get a response listing the projects the user is a member of"""
    user_projects = user.projects
    if not user_projects:
        return "You are not a member of any projects."

    response = "You are a member of the following projects:\n\n"
    for project in user_projects:
        role = project.get_user_role(user.id)
        task_count = Task.query.filter_by(project_id=project.id).count()
        assigned_count = Task.query.filter_by(project_id=project.id, assignee_id=user.id).count()
        response += f"- {project.name} (Role: {role})\n"
        response += f"  Total tasks: {task_count}, Assigned to you: {assigned_count}\n"
    return response

def get_help_response():
    """Get a help response listing available commands"""
    response = "I can help you with the following:\n\n"
    response += "- How many tasks do I have?\n"
    response += "- What are my tasks?\n"
    response += "- Who is assigned to tasks I created?\n"
    response += "- What is the status of tasks I created?\n"
    response += "- What projects am I working on?\n"
    response += "- Help (shows this message)\n\n"
    response += "Feel free to ask any of these questions!"
    return response

# Примеры возможных запросов:
# - How many tasks do I have?
# - What are my tasks?
# - Who is assigned to tasks I created?
# - What is the status of tasks I created?
# - What projects am I working on?
# - Help
