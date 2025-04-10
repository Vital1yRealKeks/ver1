
from models import Task, Project, User
from sqlalchemy import func, and_
import re


def parse_query(query):
    """Parse a chatbot query to determine the intent"""
    query = query.lower().strip()

    # Task count queries
    if re.search(r'how many tasks (do i have|are assigned to me)', query):
        return 'task_count'

    # Task list queries
    elif re.search(r'what( are| is)? (my|the) tasks', query) or query == "what are these tasks?":
        return 'task_list'

    # Project manager queries
    elif re.search(r'(who is assigned to|what is the status of) (the )?tasks i created', query):
        return 'manager_task_status'

    # Project list queries
    elif re.search(r'what projects (am i on|do i have|am i working on)', query):
        return 'project_list'

    # Help queries
    elif re.search(r'(help|what can you do)', query):
        return 'help'

    # Unknown intent
    else:
        return 'unknown'


def get_user_task_stats(user_id):
    """Get statistics about a user's tasks"""
    # Count tasks by status
    todo_count = Task.query.filter_by(assignee_id=user_id, status='To Do').count()
    in_progress_count = Task.query.filter_by(assignee_id=user_id, status='In Progress').count()
    done_count = Task.query.filter_by(assignee_id=user_id, status='Done').count()
    total_count = todo_count + in_progress_count + done_count

    # Count tasks by priority
    high_priority = Task.query.filter_by(assignee_id=user_id, priority='High').count()
    medium_priority = Task.query.filter_by(assignee_id=user_id, priority='Medium').count()
    low_priority = Task.query.filter_by(assignee_id=user_id, priority='Low').count()

    # Get projects with tasks
    projects_with_tasks = Project.query.join(Task).filter(Task.assignee_id == user_id).distinct().count()

    return {
        'total': total_count,
        'todo': todo_count,
        'in_progress': in_progress_count,
        'done': done_count,
        'high_priority': high_priority,
        'medium_priority': medium_priority,
        'low_priority': low_priority,
        'projects_with_tasks': projects_with_tasks
    }


def get_manager_task_stats(user_id):
    """Get statistics about tasks created by a user"""
    # Count tasks by status
    todo_count = Task.query.filter_by(creator_id=user_id, status='To Do').count()
    in_progress_count = Task.query.filter_by(creator_id=user_id, status='In Progress').count()
    done_count = Task.query.filter_by(creator_id=user_id, status='Done').count()
    total_count = todo_count + in_progress_count + done_count

    # Count assigned vs unassigned tasks
    assigned_count = Task.query.filter(Task.creator_id == user_id, Task.assignee_id != None).count()
    unassigned_count = Task.query.filter(Task.creator_id == user_id, Task.assignee_id == None).count()

    # Count unique assignees
    unique_assignees = User.query.join(Task, User.id == Task.assignee_id).filter(
        Task.creator_id == user_id).distinct().count()

    return {
        'total': total_count,
        'todo': todo_count,
        'in_progress': in_progress_count,
        'done': done_count,
        'assigned': assigned_count,
        'unassigned': unassigned_count,
        'unique_assignees': unique_assignees
    }


def format_task_list(tasks):
    """Format a list of tasks for display in the chatbot"""
    if not tasks:
        return "No tasks found."

    result = ""
    for task in tasks:
        project = Project.query.get(task.project_id)
        assignee = User.query.get(task.assignee_id) if task.assignee_id else None

        result += f"- {task.title}\n"
        result += f"  Project: {project.name}\n"
        result += f"  Status: {task.status}\n"
        result += f"  Priority: {task.priority}\n"

        if assignee:
            result += f"  Assigned to: {assignee.username}\n"
        else:
            result += f"  Assigned to: Unassigned\n"

        if task.due_date:
            result += f"  Due date: {task.due_date.strftime('%Y-%m-%d')}\n"

        result += "\n"

    return result


These
utility
files
provide
helper
functions
for the Kanban board and chatbot features, making the code more modular and easier to maintain.
:computer: View
my
work
Was
this
response
helpful?
9: 37
Now
let
's create the templates for the application. Let'
s
start
with the base template:
    13.
    templates / base.html
Create
a
directory
named
templates and inside
it
create
a
file
named
base.html:
html
< !DOCTYPE
html >
< html
lang = & quot;
en & quot; >
< head >
< meta
charset = & quot;
UTF - 8 & quot; >
< meta
name = & quot;
viewport & quot;
content = & quot;
width = device - width, initial - scale = 1.0 & quot; >
< title > { % block
title %}Project
Portal
{ % endblock %} < / title >

link
href = & quot;
https: // cdn.jsdelivr.net / npm / bootstrap @ 5.3
.0 - alpha1 / dist / css / bootstrap.min.css & quot;
rel = & quot;
stylesheet & quot;

link
rel = & quot;
stylesheet & quot;
href = & quot;
https: // cdnjs.cloudflare.com / ajax / libs / font - awesome / 6.0
.0 / css / all.min.css & quot;

< link
rel = & quot;
stylesheet & quot;
href = & quot;
{{url_for('static', filename='css/style.css')}} & quot; >

{ % block
extra_css %}{ % endblock %}
< / head >
< body >

< nav


class =& quot;navbar navbar-expand-lg navbar-dark bg-primary & quot; >

< div


class =& quot;container & quot; >

< a


class =& quot;navbar-brand & quot; href= & quot;{{url_for('projects.dashboard') if current_user.is_authenticated else url_for('auth.login')}} & quot; >

< i


class =& quot;fas fa-tasks me-2 & quot; > < / i > Project Portal

< / a >
< button


class =& quot;navbar-toggler & quot; type= & quot;button & quot; data-bs-toggle= & quot;collapse & quot; data-bs-target= & quot;  # navbarNav&quot;>

< span


class =& quot;navbar-toggler-icon & quot; > < / span >

< / button >
< div


class =& quot;collapse navbar-collapse & quot; id= & quot;navbarNav & quot; >

< ul


class =& quot;navbar-nav me-auto & quot; >


{ % if current_user.is_authenticated %}
< li


class =& quot;nav-item & quot; >

< a


class =& quot;nav-link & quot; href= & quot;{{url_for('projects.dashboard')}} & quot; >

< i


class =& quot;fas fa-home me-1 & quot; > < / i > Dashboard

< / a >
< / li >
< li


class =& quot;nav-item & quot; >

< a


class =& quot;nav-link & quot; href= & quot;{{url_for('projects.list_projects')}} & quot; >

< i


class =& quot;fas fa-project-diagram me-1 & quot; > < / i > Projects

< / a >
< / li >
< li


class =& quot;nav-item & quot; >

< a


class =& quot;nav-link & quot; href= & quot;{{url_for('tasks.list_tasks')}} & quot; >

< i


class =& quot;fas fa-clipboard-list me-1 & quot; > < / i > Tasks

< / a >
< / li >
< li


class =& quot;nav-item & quot; >

< a


class =& quot;nav-link & quot; href= & quot;{{url_for('chatbot.chatbot')}} & quot; >

< i


class =& quot;fas fa-robot me-1 & quot; > < / i > Chatbot

< / a >
< / li >
{ % endif %}
< / ul >
< ul


class =& quot;navbar-nav & quot; >


{ % if current_user.is_authenticated %}
< li


class =& quot;nav-item dropdown & quot; >

< a


class =& quot;nav-link dropdown-toggle & quot; href= & quot;  # &quot; id=&quot;userDropdown&quot; role=&quot;button&quot; data-bs-toggle=&quot;dropdown&quot;>

< i


class =& quot;fas fa-user me-1 & quot; > < / i > {{current_user.username}}

< / a >
< ul


class =& quot;dropdown-menu dropdown-menu-end & quot; >

< li >
< a


class =& quot;dropdown-item & quot; href= & quot;{{url_for('auth.profile')}} & quot; >

< i


class =& quot;fas fa-id-card me-1 & quot; > < / i > Profile

< / a >
< / li >
< li > < hr


class =& quot;dropdown-divider & quot; > < / li >

< li >
< a


class =& quot;dropdown-item & quot; href= & quot;{{url_for('auth.logout')}} & quot; >

< i


class =& quot;fas fa-sign-out-alt me-1 & quot; > < / i > Logout

< / a >
< / li >
< / ul >
< / li >
{ % else %}
< li


class =& quot;nav-item & quot; >

< a


class =& quot;nav-link & quot; href= & quot;{{url_for('auth.login')}} & quot; >

< i


class =& quot;fas fa-sign- in -alt me-1 & quot; > < / i > Login

< / a >
< / li >
< li


class =& quot;nav-item & quot; >

< a


class =& quot;nav-link & quot; href= & quot;{{url_for('auth.register')}} & quot; >

< i


class =& quot;fas fa-user-plus me-1 & quot; > < / i > Register

< / a >
< / li >
{ % endif %}
< / ul >
< / div >
< / div >
< / nav >

< div


class =& quot;container mt-3 & quot; >


{ %
with messages = get_flashed_messages(with_categories=true) %}
{ % if messages %}
{ %
for category, message in messages %}
< div


class =& quot;alert alert-{{category}} alert-dismissible fade show & quot; >


{{message}}
< button
type = & quot;
button & quot; class = & quot;
btn - close & quot;
data - bs - dismiss = & quot;
alert & quot; > < / button >
< / div >
{ % endfor %}
{ % endif %}
{ % endwith %}
< / div >

< div


class =& quot;container mt-4 & quot; >


{ % block
content %}{ % endblock %}
< / div >

< footer


class =& quot;bg-light text-center text-muted py-3 mt-5 & quot; >

< div


class =& quot;container & quot; >

< p


class =& quot;mb-0 & quot; > & copy; 2023 Project Portal.All rights reserved.< / p >

< / div >
< / footer >

script
src = & quot;
https: // cdn.jsdelivr.net / npm / bootstrap @ 5.3
.0 - alpha1 / dist / js / bootstrap.bundle.min.js & quot; < / script >

script
src = & quot;
https: // code.jquery.com / jquery - 3.6
.0.min.js & quot; < / script >

{ % block
extra_js %}{ % endblock %}
< / body >
< / html >
:computer: View
my
work
Was
this
response
helpful?
9: 38
14.
templates / index.html
Create
a
file
named
index.html in the
templates
directory:
html
{ % extends
'base.html.html' %}

{ % block
title %}Welcome
to
Project
Portal
{ % endblock %}

{ % block
content %}
< div


class =& quot;row justify-content-center & quot; >

< div


class =& quot;col-md-8 text-center & quot; >

< div


class =& quot;card shadow-lg border-0 rounded-lg mt-5 & quot; >

< div


class =& quot;card-body p-5 & quot; >

< h1


class =& quot;display-4 mb-4 & quot; > Welcome to Project Portal < / h1 >

< p


class =& quot;lead mb-4 & quot; > A powerful platform for managing projects and tasks with your team.< / p >

< div


class =& quot;row mb-4 & quot; >

< div


class =& quot;col-md-4 & quot; >

< div


class =& quot;card mb-3 & quot; >

< div


class =& quot;card-body & quot; >

< i


class =& quot;fas fa-project-diagram fa-3x mb-3 text-primary & quot; > < / i >

< h5


class =& quot;card-title & quot; > Project Management < / h5 >

< p


class =& quot;card-text & quot; > Create and manage projects with your team.< / p >

< / div >
< / div >
< / div >
< div


class =& quot;col-md-4 & quot; >

< div


class =& quot;card mb-3 & quot; >

< div


class =& quot;card-body & quot; >

< i


class =& quot;fas fa-tasks fa-3x mb-3 text-primary & quot; > < / i >

< h5


class =& quot;card-title & quot; > Task Tracking < / h5 >

< p


class =& quot;card-text & quot; > Track tasks with Kanban boards or lists.< / p >

< / div >
< / div >
< / div >
< div


class =& quot;col-md-4 & quot; >

< div


class =& quot;card mb-3 & quot; >

< div


class =& quot;card-body & quot; >

< i


class =& quot;fas fa-robot fa-3x mb-3 text-primary & quot; > < / i >

< h5


class =& quot;card-title & quot; > Chatbot Assistant < / h5 >

< p


class =& quot;card-text & quot; > Get quick updates on your tasks and projects.< / p >

< / div >
< / div >
< / div >
< / div >

< div


class =& quot;d-grid gap-2 d-md-block & quot; >

< a
href = & quot;
{{url_for('auth.login')}} & quot; class = & quot;
btn
btn - primary
btn - lg
me - md - 2 & quot; >
< i


class =& quot;fas fa-sign- in -alt me-2 & quot; > < / i > Login

< / a >
< a
href = & quot;
{{url_for('auth.register')}} & quot; class = & quot;
btn
btn - outline - primary
btn - lg & quot; >
< i


class =& quot;fas fa-user-plus me-2 & quot; > < / i > Register

< / a >
< / div >
< / div >
< / div >
< / div >
< / div >
{ % endblock %}
15.
templates / dashboard.html
Create
a
file
named
dashboard.html in the
templates
directory:
html
{ % extends
'base.html.html' %}

{ % block
title %}Dashboard - Project
Portal
{ % endblock %}

{ % block
content %}
< div


class =& quot;row mb-4 & quot; >

< div


class =& quot;col-md-8 & quot; >

< h1


class =& quot;mb-4 & quot; > Welcome, {{current_user.username}}! < / h1 >

< / div >
< div


class =& quot;col-md-4 text-end & quot; >

< a
href = & quot;
{{url_for('projects.create_project')}} & quot; class = & quot;
btn
btn - primary & quot; >
< i


class =& quot;fas fa-plus me-1 & quot; > < / i > New Project

< / a >
< / div >
< / div >

< div


class =& quot;row & quot; >

< div


class =& quot;col-md-6 mb-4 & quot; >

< div


class =& quot;card shadow-sm h-100 & quot; >

< div


class =& quot;card-header bg-primary text-white & quot; >

< h5


class =& quot;mb-0 & quot; >

< i


class =& quot;fas fa-project-diagram me-2 & quot; > < / i > My Projects

< / h5 >
< / div >
< div


class =& quot;card-body & quot; >


{ % if user_projects %}
< div


class =& quot;list-group & quot; >


{ %
for project in user_projects %}
< a
href = & quot;
{{url_for('projects.view_project', project_id=project.id)}} & quot; class = & quot;
list - group - item
list - group - item - action & quot; >
< div


class =& quot;d-flex w-100 justify-content-between & quot; >

< h5


class =& quot;mb-1 & quot; > {{project.name}} < / h5 >

< small > {{project.created_at.strftime('%Y-%m-%d')}} < / small >
< / div >
< p


class =& quot;mb-1 & quot; > {{project.description | truncate(100)}} < / p >

< small >
< span


class =& quot;badge bg-info & quot; > {{project.tasks | length}} tasks < / span >

< / small >
< / a >
{ % endfor %}
< / div >
{ % else %}
< p


class =& quot;text-muted & quot; > You don't have any projects yet.</p>

< a
href = & quot;
{{url_for('projects.create_project')}} & quot; class = & quot;
btn
btn - outline - primary & quot; >
< i


class =& quot;fas fa-plus me-1 & quot; > < / i > Create Your First Project

< / a >
{ % endif %}
< / div >
< div


class =& quot;card-footer & quot; >

< a
href = & quot;
{{url_for('projects.list_projects')}} & quot; class = & quot;
btn
btn - sm
btn - outline - primary & quot; >
View
All
Projects
< / a >
< / div >
< / div >
< / div >

< div


class =& quot;col-md-6 mb-4 & quot; >

< div


class =& quot;card shadow-sm h-100 & quot; >

< div


class =& quot;card-header bg-primary text-white & quot; >

< h5


class =& quot;mb-0 & quot; >

< i


class =& quot;fas fa-tasks me-2 & quot; > < / i > My Tasks

< / h5 >
< / div >
< div


class =& quot;card-body & quot; >


{ % if assigned_tasks %}
< div


class =& quot;list-group & quot; >


{ %
for task in assigned_tasks %}
{ % if task.status != 'Done' %}
< a
href = & quot;
{{url_for('tasks.view_task', task_id=task.id)}} & quot; class = & quot;
list - group - item
list - group - item - action & quot; >
< div


class =& quot;d-flex w-100 justify-content-between & quot; >

< h5


class =& quot;mb-1 & quot; > {{task.title}} < / h5 >

< span


class =& quot;badge {% if task.status == 'To Do' %}bg-secondary{% elif task.status == 'In Progress' %}bg-primary{% else %}bg-success{%endif %} & quot; >


{{task.status}}
< / span >
< / div >
< p


class =& quot;mb-1 & quot; > {{task.description | truncate(100) if task.description else 'No description'}} < / p >

< small >
Project: {{task.project.name}}
{ % if task.due_date %}
| Due: {{task.due_date.strftime('%Y-%m-%d')}}
{ % endif %}
< / small >
< / a >
{ % endif %}
{ % endfor %}
< / div >
{ % else %}
< p


class =& quot;text-muted & quot; > You don't have any tasks assigned to you.</p>


{ % endif %}
< / div >
< div


class =& quot;card-footer & quot; >

< a
href = & quot;
{{url_for('tasks.list_tasks')}} & quot; class = & quot;
btn
btn - sm
btn - outline - primary & quot; >
View
All
Tasks
< / a >
< / div >
< / div >
< / div >
< / div >
:computer: View
my
work
Was
this
response
helpful?
9: 38
Let
's continue with the dashboard template:
html
< div


class =& quot;row & quot; >

< div


class =& quot;col-md-6 mb-4 & quot; >

< div


class =& quot;card shadow-sm & quot; >

< div


class =& quot;card-header bg-primary text-white & quot; >

< h5


class =& quot;mb-0 & quot; >

< i


class =& quot;fas fa-chart-line me-2 & quot; > < / i > Task Summary

< / h5 >
< / div >
< div


class =& quot;card-body & quot; >

< div


class =& quot;row text-center & quot; >

< div


class =& quot;col-4 & quot; >

< div


class =& quot;card bg-light mb-3 & quot; >

< div


class =& quot;card-body & quot; >

< h3


class =& quot;text-secondary & quot; > {{assigned_tasks | selectattr('status', 'equalto', 'To Do') | list | length}} < / h3 >

< p


class =& quot;mb-0 & quot; > To Do < / p >

< / div >
< / div >
< / div >
< div


class =& quot;col-4 & quot; >

< div


class =& quot;card bg-light mb-3 & quot; >

< div


class =& quot;card-body & quot; >

< h3


class =& quot;text-primary & quot; > {{assigned_tasks | selectattr('status', 'equalto', 'In Progress') | list | length}} < / h3 >

< p


class =& quot;mb-0 & quot; > In Progress < / p >

< / div >
< / div >
< / div >
< div


class =& quot;col-4 & quot; >

< div


class =& quot;card bg-light mb-3 & quot; >

< div


class =& quot;card-body & quot; >

< h3


class =& quot;text-success & quot; > {{assigned_tasks | selectattr('status', 'equalto', 'Done') | list | length}} < / h3 >

< p


class =& quot;mb-0 & quot; > Done < / p >

< / div >
< / div >
< / div >
< / div >
< / div >
< / div >
< / div >

< div


class =& quot;col-md-6 mb-4 & quot; >

< div


class =& quot;card shadow-sm & quot; >

< div


class =& quot;card-header bg-primary text-white & quot; >

< h5


class =& quot;mb-0 & quot; >

< i


class =& quot;fas fa-robot me-2 & quot; > < / i > Chatbot Assistant

< / h5 >
< / div >
< div


class =& quot;card-body & quot; >

< p > Need
a
quick
update? Ask
the
chatbot
assistant! < / p >
< div


class =& quot;d-grid gap-2 & quot; >

< a
href = & quot;
{{url_for('chatbot.chatbot')}} & quot; class = & quot;
btn
btn - outline - primary & quot; >
< i


class =& quot;fas fa-comments me-2 & quot; > < / i > Open Chatbot

< / a >
< / div >
< div


class =& quot;mt-3 & quot; >

< p


class =& quot;mb-1 & quot; > Try asking:<

    / p >
< ul


class =& quot;list-unstyled & quot; >

< li > < small > < i


class =& quot;fas fa-angle-right me-1 & quot; > < / i > "How many tasks do I have?" < / small > < / li >

< li > < small > < i


class =& quot;fas fa-angle-right me-1 & quot; > < / i > "What are my tasks?" < / small > < / li >

< li > < small > < i


class =& quot;fas fa-angle-right me-1 & quot; > < / i > "What projects am I working on?" < / small > < / li >

< / ul >
< / div >
< / div >
< / div >
< / div >
< / div >
{ % endblock %}
16.
templates / auth / login.html
Create
a
directory
named
auth
inside
the
templates
directory and create
a
file
named
login.html:
html
{ % extends
'base.html.html' %}

{ % block
title %}Login - Project
Portal
{ % endblock %}

{ % block
content %}
< div


class =& quot;row justify-content-center & quot; >

< div


class =& quot;col-lg-5 & quot; >

< div


class =& quot;card shadow-lg border-0 rounded-lg mt-5 & quot; >

< div


class =& quot;card-header bg-primary text-white & quot; >

< h3


class =& quot;text-center font-weight-light my-2 & quot; > Login < / h3 >

< / div >
< div


class =& quot;card-body & quot; >

< form
method = & quot;
POST & quot;
action = & quot;
{{url_for('auth.login')}} & quot; >
< div


class =& quot;mb-3 & quot; >

< label
for = & quot;email & quot; class = & quot;form-label & quot; > Email < / label >
< div


class =& quot;input-group & quot; >

< span


class =& quot;input-group-text & quot; > < i class = & quot;fas fa-envelope & quot; > < / i > < / span >

< input
type = & quot;
email & quot; class = & quot;
form - control & quot;
id = & quot;
email & quot;
name = & quot;
email & quot;
placeholder = & quot;
Enter
your
email & quot;
required >
< / div >
< / div >
< div


class =& quot;mb-3 & quot; >

< label
for = & quot;password & quot; class = & quot;form-label & quot; > Password < / label >
< div


class =& quot;input-group & quot; >

< span


class =& quot;input-group-text & quot; > < i class = & quot;fas fa-lock & quot; > < / i > < / span >

< input
type = & quot;
password & quot; class = & quot;
form - control & quot;
id = & quot;
password & quot;
name = & quot;
password & quot;
placeholder = & quot;
Enter
your
password & quot;
required >
< / div >
< / div >
< div


class =& quot;form-check mb-3 & quot; >

< input


class =& quot;form-check-input & quot; type= & quot;checkbox & quot; id= & quot;remember & quot; name= & quot;remember & quot; >

< label


class =& quot;form-check-label & quot; for = & quot;remember & quot; > Remember me < / label >

< / div >
< div


class =& quot;d-grid & quot; >

< button
type = & quot;
submit & quot; class = & quot;
btn
btn - primary & quot; >
< i


class =& quot;fas fa-sign- in -alt me-2 & quot; > < / i > Login

< / button >
< / div >
< / form >
< / div >
< div


class =& quot;card-footer text-center py-3 & quot; >

< div


class =& quot;small & quot; >

< a
href = & quot;
{{url_for('auth.register')}} & quot; > Need
an
account? Sign
up! < / a >
< / div >
< / div >
< / div >
< / div >
< / div >
{ % endblock %}
17.
templates / auth / register.html
Create
a
file
named
register.html in the
auth
directory:
html
{ % extends
'base.html.html' %}

{ % block
title %}Register - Project
Portal
{ % endblock %}

{ % block
content %}
< div


class =& quot;row justify-content-center & quot; >

< div


class =& quot;col-lg-6 & quot; >

< div


class =& quot;card shadow-lg border-0 rounded-lg mt-5 & quot; >

< div


class =& quot;card-header bg-primary text-white & quot; >

< h3


class =& quot;text-center font-weight-light my-2 & quot; > Create Account < / h3 >

< / div >
< div


class =& quot;card-body & quot; >

< form
method = & quot;
POST & quot;
action = & quot;
{{url_for('auth.register')}} & quot; >
< div


class =& quot;mb-3 & quot; >

< label
for = & quot;username & quot; class = & quot;form-label & quot; > Username < / label >
< div


class =& quot;input-group & quot; >

< span


class =& quot;input-group-text & quot; > < i class = & quot;fas fa-user & quot; > < / i > < / span >

< input
type = & quot;
text & quot; class = & quot;
form - control & quot;
id = & quot;
username & quot;
name = & quot;
username & quot;
placeholder = & quot;
Enter
a
username & quot;
required >
< / div >
< / div >
< div


class =& quot;mb-3 & quot; >

< label
for = & quot;email & quot; class = & quot;form-label & quot; > Email < / label >
< div


class =& quot;input-group & quot; >

< span


class =& quot;input-group-text & quot; > < i class = & quot;fas fa-envelope & quot; > < / i > < / span >

< input
type = & quot;
email & quot; class = & quot;
form - control & quot;
id = & quot;
email & quot;
name = & quot;
email & quot;
placeholder = & quot;
Enter
your
email & quot;
required >
< / div >
< / div >
< div


class =& quot;row mb-3 & quot; >

< div


class =& quot;col-md-6 & quot; >

< label
for = & quot;password & quot; class = & quot;form-label & quot; > Password < / label >
< div


class =& quot;input-group & quot; >

< span


class =& quot;input-group-text & quot; > < i class = & quot;fas fa-lock & quot; > < / i > < / span >

< input
type = & quot;
password & quot; class = & quot;
form - control & quot;
id = & quot;
password & quot;
name = & quot;
password & quot;
placeholder = & quot;
Enter
a
password & quot;
required >
< / div >
< / div >
< div


class =& quot;col-md-6 & quot; >

< label
for = & quot;confirm_password & quot; class = & quot;form-label & quot; > Confirm Password < / label >
< div


class =& quot;input-group & quot; >

< span


class =& quot;input-group-text & quot; > < i class = & quot;fas fa-lock & quot; > < / i > < / span >

< input
type = & quot;
password & quot; class = & quot;
form - control & quot;
id = & quot;
confirm_password & quot;
name = & quot;
confirm_password & quot;
placeholder = & quot;
Confirm
password & quot;
required >
< / div >
< / div >
< / div >
< div


class =& quot;d-grid & quot; >

< button
type = & quot;
submit & quot; class = & quot;
btn
btn - primary & quot; >
< i


class =& quot;fas fa-user-plus me-2 & quot; > < / i > Create Account

< / button >
< / div >
< / form >
< / div >
< div


class =& quot;card-footer text-center py-3 & quot; >

< div


class =& quot;small & quot; >

< a
href = & quot;
{{url_for('auth.login')}} & quot; > Have
an
account? Go
to
login < / a >
< / div >
< / div >
< / div >
< / div >
< / div >
{ % endblock %}
:computer: View
my
work
Was
this
response
helpful?
9: 39
18.
templates / projects / list.html
Create
a
directory
named
projects
inside
the
templates
directory and create
a
file
named
list.html:
html
{ % extends
'base.html.html' %}

{ % block
title %}My
Projects - Project
Portal
{ % endblock %}

{ % block
content %}
< div


class =& quot;row mb-4 & quot; >

< div


class =& quot;col-md-8 & quot; >

< h1


class =& quot;mb-4 & quot; > My Projects < / h1 >

< / div >
< div


class =& quot;col-md-4 text-end & quot; >

< a
href = & quot;
{{url_for('projects.create_project')}} & quot; class = & quot;
btn
btn - primary & quot; >
< i


class =& quot;fas fa-plus me-1 & quot; > < / i > New Project

< / a >
< / div >
< / div >

< div


class =& quot;row & quot; >


{ % if projects %}
{ %
for project in projects %}
< div


class =& quot;col-md-6 col-lg-4 mb-4 & quot; >

< div


class =& quot;card h-100 shadow-sm & quot; >

< div


class =& quot;card-header bg-primary text-white & quot; >

< h5


class =& quot;mb-0 & quot; > {{project.name}} < / h5 >

< / div >
< div


class =& quot;card-body & quot; >

< p


class =& quot;card-text & quot; > {{project.description | truncate(150) if project.description else 'No description'}} < / p >

< div


class =& quot;d-flex justify-content-between align-items-center & quot; >

< small


class =& quot;text-muted & quot; > Created: {{project.created_at.strftime('%Y-%m-%d')}} <

/ small >
< span


class =& quot;badge bg-info & quot; > {{project.tasks | length}} tasks < / span >

< / div >
< / div >
< div


class =& quot;card-footer & quot; >

< div


class =& quot;d-grid gap-2 & quot; >

< a
href = & quot;
{{url_for('projects.view_project', project_id=project.id)}} & quot; class = & quot;
btn
btn - outline - primary & quot; >
< i


class =& quot;fas fa-eye me-1 & quot; > < / i > View Project

< / a >
< / div >
< / div >
< / div >
< / div >
{ % endfor %}
{ % else %}
< div


class =& quot;col-12 & quot; >

< div


class =& quot;alert alert-info & quot; >

< i


class =& quot;fas fa-info-circle me-2 & quot; > < / i > You don't have any projects yet.

< / div >
< div


class =& quot;text-center mt-4 & quot; >

< a
href = & quot;
{{url_for('projects.create_project')}} & quot; class = & quot;
btn
btn - primary & quot; >
< i


class =& quot;fas fa-plus me-1 & quot; > < / i > Create Your First Project

< / a >
< / div >
< / div >
{ % endif %}
< / div >
{ % endblock %}
19.
templates / projects / create.html
Create
a
file
named
create.html in the
projects
directory:
html
{ % extends
'base.html.html' %}

{ % block
title %}Create
Project - Project
Portal
{ % endblock %}

{ % block
content %}
< div


class =& quot;row justify-content-center & quot; >

< div


class =& quot;col-lg-8 & quot; >

< div


class =& quot;card shadow-lg border-0 rounded-lg mt-4 & quot; >

< div


class =& quot;card-header bg-primary text-white & quot; >

< h3


class =& quot;text-center font-weight-light my-2 & quot; > Create New Project < / h3 >

< / div >
< div


class =& quot;card-body & quot; >

< form
method = & quot;
POST & quot;
action = & quot;
{{url_for('projects.create_project')}} & quot; >
< div


class =& quot;mb-3 & quot; >

< label
for = & quot;name & quot; class = & quot;form-label & quot; > Project Name < / label >
< div


class =& quot;input-group & quot; >

< span


class =& quot;input-group-text & quot; > < i class = & quot;fas fa-project-diagram & quot; > < / i > < / span >

< input
type = & quot;
text & quot; class = & quot;
form - control & quot;
id = & quot;
name & quot;
name = & quot;
name & quot;
placeholder = & quot;
Enter
project
name & quot;
required >
< / div >
< / div >
< div


class =& quot;mb-3 & quot; >

< label
for = & quot;description & quot; class = & quot;form-label & quot; > Description < / label >
< textarea


class =& quot;form-control & quot; id= & quot;description & quot; name= & quot;description & quot; rows= & quot;4 & quot; placeholder= & quot;Enter project description & quot; > < / textarea >

< / div >
< div


class =& quot;d-flex justify-content-between & quot; >

< a
href = & quot;
{{url_for('projects.list_projects')}} & quot; class = & quot;
btn
btn - outline - secondary & quot; >
< i


class =& quot;fas fa-arrow-left me-1 & quot; > < / i > Cancel

< / a >
< button
type = & quot;
submit & quot; class = & quot;
btn
btn - primary & quot; >
< i


class =& quot;fas fa-save me-1 & quot; > < / i > Create Project

< / button >
< / div >
< / form >
< / div >
< / div >
< / div >
< / div >
{ % endblock %}