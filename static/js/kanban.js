document.addEventListener('DOMContentLoaded', function() {
// Initialize Sortable for each column
const todoColumn = document.getElementById('todo-column');
const inProgressColumn = document.getElementById('in-progress-column');
const doneColumn = document.getElementById('done-column');
if (todoColumn && inProgressColumn && doneColumn) {
const columns = [todoColumn, inProgressColumn, doneColumn];
columns.forEach(column => {
new Sortable(column, {
group: 'tasks',
animation: 150,
ghostClass: 'bg-light',
onEnd: function(evt) {
const taskId = evt.item.dataset.taskId;
const newStatus = evt.to.dataset.status;
// Update task status via API
fetch(/tasks/${taskId}/status, {
method: 'POST',
headers: {
'Content-Type': 'application/json',
},
body: JSON.stringify({ status: newStatus }),
})
.then(response => {
if (!response.ok) {
throw new Error('Failed to update task status');
}
return response.json();
})
.then(data => {
console.log('Task status updated:', data);
})
.catch(error => {
console.error('Error updating task status:', error);
alert('Error updating task status. Please try again.');
// Revert the drag if there was an error
window.location.reload();
});
}
});
});
}
});