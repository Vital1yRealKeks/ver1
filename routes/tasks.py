from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import current_user, login_required
from extensions import db
from models import Task, Project, User
from datetime import datetime
from sqlalchemy import or_

tasks_bp = Blueprint('tasks', __name__, url_prefix='/tasks')


@tasks_bp.route('/')
@login_required
def list_tasks():
    assigned_tasks = Task.query.filter_by(assignee_id=current_user.id).all()
    created_tasks = Task.query.filter_by(creator_id=current_user.id).all()
    user_projects = current_user.projects
    return render_template('tasks/list.html',
                           assigned_tasks=assigned_tasks,
                           created_tasks=created_tasks,
                           user_projects=user_projects)


@tasks_bp.route('/project/int:project_id')
@login_required
def project_tasks(project_id):
    project = Project.query.get_or_404(project_id)
    if project not in current_user.projects:
        flash('You do not have access to this project', 'danger')
        return redirect(url_for('projects.list_projects'))

    tasks = Task.query.filter_by(project_id=project_id).all()
    members = project.members.all()
    user_role = project.get_user_role(current_user.id)

    return render_template('tasks/project_tasks.html',
                           project=project,
                           tasks=tasks,
                           members=members,
                           user_role=user_role)


@tasks_bp.route('/kanban/int:project_id')
@login_required
def kanban_board(project_id):
    project = Project.query.get_or_404(project_id)
    if project not in current_user.projects:
        flash('You do not have access to this project', 'danger')
        return redirect(url_for('projects.list_projects'))

    tasks = Task.query.filter_by(project_id=project_id).all()
    members = project.members.all()
    user_role = project.get_user_role(current_user.id)

    task_columns = {'To Do': [], 'In Progress': [], 'Done': []}
    for task in tasks:
        if task.status in task_columns:
            task_columns[task.status].append(task)

    return render_template('tasks/kanban.html',
                           project=project,
                           task_columns=task_columns,
                           members=members,
                           user_role=user_role)


@tasks_bp.route('/create/int:project_id', methods=['GET', 'POST'])
@login_required
def create_task(project_id):
    project = Project.query.get_or_404(project_id)
    if project not in current_user.projects:
        flash('You do not have access to this project', 'danger')
        return redirect(url_for('projects.list_projects'))

    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        status = request.form.get('status', 'To Do')
        priority = request.form.get('priority', 'Medium')
        assignee_id = request.form.get('assignee_id')
        due_date_str = request.form.get('due_date')

        if not title:
            flash('Task title is required', 'danger')
            return redirect(url_for('tasks.create_task', project_id=project_id))

        due_date = None
        if due_date_str:
            try:
                due_date = datetime.strptime(due_date_str, '%Y-%m-%d')
            except ValueError:
                flash('Invalid date format. Please use YYYY-MM-DD', 'danger')
                return redirect(url_for('tasks.create_task', project_id=project_id))

        new_task = Task(
            title=title,
            description=description,
            status=status,
            priority=priority,
            due_date=due_date,
            project_id=project_id,
            creator_id=current_user.id,
            assignee_id=assignee_id if assignee_id else None
        )
        db.session.add(new_task)
        db.session.commit()
        flash('Task created successfully', 'success')
        return redirect(url_for('tasks.project_tasks', project_id=project_id))

    members = project.members.all()
    return render_template('tasks/create.html', project=project, members=members)


@tasks_bp.route('/int:task_id')
@login_required
def view_task(task_id):
    task = Task.query.get_or_404(task_id)
    project = task.project

    if project not in current_user.projects:
        flash('You do not have access to this task', 'danger')
        return redirect(url_for('projects.list_projects'))

    user_role = project.get_user_role(current_user.id)
    members = project.members.all()

    return render_template('tasks/view.html',
                           task=task,
                           project=project,
                           members=members,
                           user_role=user_role)


@tasks_bp.route('/int:task_id/edit', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)
    project = task.project

    if project not in current_user.projects:
        flash('You do not have access to this task', 'danger')
        return redirect(url_for('projects.list_projects'))

    user_role = project.get_user_role(current_user.id)
    if user_role not in ['admin', 'manager'] and \
       task.creator_id != current_user.id and \
       task.assignee_id != current_user.id:
        flash('You do not have permission to edit this task', 'danger')
        return redirect(url_for('tasks.view_task', task_id=task_id))

    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        status = request.form.get('status')
        priority = request.form.get('priority')
        assignee_id = request.form.get('assignee_id')
        due_date_str = request.form.get('due_date')

        if not title:
            flash('Task title is required', 'danger')
            return redirect(url_for('tasks.edit_task', task_id=task_id))

        due_date = None
        if due_date_str:
            try:
                due_date = datetime.strptime(due_date_str, '%Y-%m-%d')
            except ValueError:
                flash('Invalid date format. Please use YYYY-MM-DD', 'danger')
                return redirect(url_for('tasks.edit_task', task_id=task_id))

        task.title = title
        task.description = description
        task.status = status
        task.priority = priority
        task.due_date = due_date
        task.assignee_id = assignee_id if assignee_id else None

        db.session.commit()
        flash('Task updated successfully', 'success')
        return redirect(url_for('tasks.view_task', task_id=task_id))

    members = project.members.all()
    return render_template('tasks/edit.html',
                           task=task,
                           project=project,
                           members=members)


@tasks_bp.route('/int:task_id/delete', methods=['POST'])
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    project = task.project
    project_id = project.id

    if project not in current_user.projects:
        flash('You do not have access to this task', 'danger')
        return redirect(url_for('projects.list_projects'))

    user_role = project.get_user_role(current_user.id)
    if user_role not in ['admin', 'manager'] and task.creator_id != current_user.id:
        flash('You do not have permission to delete this task', 'danger')
        return redirect(url_for('tasks.view_task', task_id=task_id))

    db.session.delete(task)
    db.session.commit()
    flash('Task deleted successfully', 'success')
    return redirect(url_for('tasks.project_tasks', project_id=project_id))


@tasks_bp.route('/int:task_id/status', methods=['POST'])
@login_required
def update_task_status(task_id):
    task = Task.query.get_or_404(task_id)
    project = task.project

    if project not in current_user.projects:
        return jsonify({'error': 'Access denied'}), 403

    data = request.get_json()
    if not data or 'status' not in data:
        return jsonify({'error': 'Missing status'}), 400

    new_status = data['status']
    if new_status not in ['To Do', 'In Progress', 'Done']:
        return jsonify({'error': 'Invalid status'}), 400

    task.status = new_status
    task.updated_at = datetime.utcnow()
    db.session.commit()
    return jsonify(task.to_dict()), 200


@tasks_bp.route('/int:task_id/assign', methods=['POST'])
@login_required
def assign_task(task_id):
    task = Task.query.get_or_404(task_id)
    project = task.project

    if project not in current_user.projects:
        flash('You do not have access to this task', 'danger')
        return redirect(url_for('projects.list_projects'))

    user_role = project.get_user_role(current_user.id)
    if user_role not in ['admin', 'manager'] and \
       task.creator_id != current_user.id and \
       task.assignee_id != current_user.id:
        flash('You do not have permission to assign this task', 'danger')
        return redirect(url_for('tasks.view_task', task_id=task_id))

    assignee_id = request.form.get('assignee_id')
    task.assignee_id = assignee_id if assignee_id else None

    db.session.commit()
    flash('Task assigned successfully', 'success')
    return redirect(url_for('tasks.view_task', task_id=task_id))
