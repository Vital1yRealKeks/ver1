from flask import Blueprint, render_template, redirect, url_for, flash, request, jsonify
from flask_login import current_user, login_required
from extensions import db
from models import Project, User, Invitation, project_users
from datetime import datetime, timedelta
import uuid
from sqlalchemy import or_

projects_bp = Blueprint('projects', __name__, url_prefix='/projects')


@projects_bp.route('/dashboard')
@login_required
def dashboard():
    user_projects = current_user.projects
    assigned_tasks = current_user.tasks
    created_tasks = current_user.created_tasks
    return render_template(
        'dashboard.html',
        user_projects=user_projects,
        assigned_tasks=assigned_tasks,
        created_tasks=created_tasks
    )


@projects_bp.route('/')
@login_required
def list_projects():
    user_projects = current_user.projects
    return render_template('projects/list.html', projects=user_projects)


@projects_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create_project():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')

        if not name:
            flash('Project name is required', 'danger')
            return redirect(url_for('projects.create_project'))

        new_project = Project(
            name=name,
            description=description,
            creator_id=current_user.id
        )
        db.session.add(new_project)
        db.session.flush()

        stmt = project_users.insert().values(
            user_id=current_user.id,
            project_id=new_project.id,
            role='admin'
        )
        db.session.execute(stmt)
        db.session.commit()

        flash('Project created successfully', 'success')
        return redirect(url_for('projects.view_project', project_id=new_project.id))

    return render_template('projects/create.html')


@projects_bp.route('/<int:project_id>')
@login_required
def view_project(project_id):
    project = Project.query.get_or_404(project_id)

    if project not in current_user.projects:
        flash('You do not have access to this project', 'danger')
        return redirect(url_for('projects.list_projects'))

    user_role = project.get_user_role(current_user.id)
    tasks = project.tasks
    members = project.members.all()
    invitations = []

    if user_role in ['admin', 'manager']:
        invitations = Invitation.query.filter_by(project_id=project_id).all()

    return render_template(
        'projects/detail.html',
        project=project,
        tasks=tasks,
        members=members,
        invitations=invitations,
        user_role=user_role
    )


@projects_bp.route('/<int:project_id>/invite', methods=['POST'])
@login_required
def invite_user(project_id):
    project = Project.query.get_or_404(project_id)
    user_role = project.get_user_role(current_user.id)

    if user_role not in ['admin', 'manager']:
        flash('You do not have permission to invite users', 'danger')
        return redirect(url_for('projects.view_project', project_id=project_id))

    email = request.form.get('email')
    role = request.form.get('role', 'member')

    if not email:
        flash('Email is required', 'danger')
        return redirect(url_for('projects.view_project', project_id=project_id))

    user = User.query.filter_by(email=email).first()
    if user and project in user.projects:
        flash('User is already a member of this project', 'warning')
        return redirect(url_for('projects.view_project', project_id=project_id))

    existing_invitation = Invitation.query.filter_by(email=email, project_id=project_id).first()
    if existing_invitation:
        flash('Invitation has already been sent to this email', 'warning')
        return redirect(url_for('projects.view_project', project_id=project_id))

    token = str(uuid.uuid4())
    expires_at = datetime.utcnow() + timedelta(days=7)

    invitation = Invitation(
        email=email,
        project_id=project_id,
        role=role,
        token=token,
        expires_at=expires_at
    )
    db.session.add(invitation)
    db.session.commit()

    flash(f'Invitation sent to {email}. Token: {token}', 'success')
    return redirect(url_for('projects.view_project', project_id=project_id))


@projects_bp.route('/accept-invitation/<token>')
@login_required
def accept_invitation(token):
    invitation = Invitation.query.filter_by(token=token).first_or_404()

    if invitation.expires_at < datetime.utcnow():
        flash('Invitation has expired', 'danger')
        return redirect(url_for('projects.dashboard'))

    if current_user.email != invitation.email:
        flash('This invitation was not sent to your email address', 'danger')
        return redirect(url_for('projects.dashboard'))

    stmt = project_users.insert().values(
        user_id=current_user.id,
        project_id=invitation.project_id,
        role=invitation.role
    )
    db.session.execute(stmt)
    db.session.delete(invitation)
    db.session.commit()

    flash('You have successfully joined the project', 'success')
    return redirect(url_for('projects.view_project', project_id=invitation.project_id))


@projects_bp.route('/<int:project_id>/members/<int:user_id>/role', methods=['POST'])
@login_required
def change_member_role(project_id, user_id):
    project = Project.query.get_or_404(project_id)
    current_user_role = project.get_user_role(current_user.id)

    if current_user_role != 'admin':
        flash('Only project admins can change member roles', 'danger')
        return redirect(url_for('projects.view_project', project_id=project_id))

    new_role = request.form.get('role')
    if new_role not in ['admin', 'manager', 'member']:
        flash('Invalid role', 'danger')
        return redirect(url_for('projects.view_project', project_id=project_id))

    stmt = project_users.update().where(
        project_users.c.user_id == user_id,
        project_users.c.project_id == project_id
    ).values(role=new_role)

    db.session.execute(stmt)
    db.session.commit()

    flash('Member role updated successfully', 'success')
    return redirect(url_for('projects.view_project', project_id=project_id))


@projects_bp.route('/<int:project_id>/members/<int:user_id>/remove', methods=['POST'])
@login_required
def remove_member(project_id, user_id):
    project = Project.query.get_or_404(project_id)
    current_user_role = project.get_user_role(current_user.id)

    if current_user_role != 'admin':
        flash('Only project admins can remove members', 'danger')
        return redirect(url_for('projects.view_project', project_id=project_id))

    if user_id == current_user.id and current_user_role == 'admin':
        admin_count = db.session.query(project_users).filter_by(
            project_id=project_id,
            role='admin'
        ).count()
        if admin_count <= 1:
            flash('Cannot remove the last admin from the project', 'danger')
            return redirect(url_for('projects.view_project', project_id=project_id))

    stmt = project_users.delete().where(
        project_users.c.user_id == user_id,
        project_users.c.project_id == project_id
    )
    db.session.execute(stmt)
    db.session.commit()

    flash('Member removed from project successfully', 'success')
    return redirect(url_for('projects.view_project', project_id=project_id))


@projects_bp.route('/<int:project_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_project(project_id):
    project = Project.query.get_or_404(project_id)
    user_role = project.get_user_role(current_user.id)

    if user_role not in ['admin', 'manager']:
        flash('You do not have permission to edit this project', 'danger')
        return redirect(url_for('projects.view_project', project_id=project_id))

    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')

        if not name:
            flash('Project name is required', 'danger')
            return redirect(url_for('projects.edit_project', project_id=project_id))

        project.name = name
        project.description = description
        db.session.commit()

        flash('Project updated successfully', 'success')
        return redirect(url_for('projects.view_project', project_id=project_id))

    return render_template('projects/edit.html', project=project)


@projects_bp.route('/<int:project_id>/delete', methods=['POST'])
@login_required
def delete_project(project_id):
    project = Project.query.get_or_404(project_id)
    user_role = project.get_user_role(current_user.id)

    if user_role != 'admin':
        flash('Only project admins can delete projects', 'danger')
        return redirect(url_for('projects.view_project', project_id=project_id))

    db.session.delete(project)
    db.session.commit()

    flash('Project deleted successfully', 'success')
    return redirect(url_for('projects.list_projects'))
