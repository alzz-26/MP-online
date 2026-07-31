// State Management
let isEditMode = false;
let editTaskId = null;
let pollInterval = null;

// DOM Elements
const taskForm = document.getElementById('task-form');
const formTitle = document.getElementById('form-title');
const taskIdInput = document.getElementById('task-id');
const taskTitleInput = document.getElementById('task-title');
const taskDescriptionInput = document.getElementById('task-description');
const taskCompletedSelect = document.getElementById('task-completed');
const completedGroup = document.getElementById('completed-group');
const submitBtn = document.getElementById('submit-btn');
const resetBtn = document.getElementById('reset-btn');
const recordsCount = document.getElementById('records-count');
const tasksListContainer = document.getElementById('tasks-list');
const dbAlert = document.getElementById('db-alert');
const dbAlertMsg = document.getElementById('db-alert-msg');

// Initial Load & Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    // Hide completed status dropdown during task creation to keep it clean (like mobile apps)
    if (completedGroup) {
        completedGroup.style.display = 'none';
    }

    // Fetch immediately on load
    fetchTasks();
    
    // Start live polling every 2 seconds
    pollInterval = setInterval(fetchTasks, 2000);
    
    // Form submission
    taskForm.addEventListener('submit', handleFormSubmit);
    
    // Reset / Cancel Edit button click
    resetBtn.addEventListener('click', resetForm);
});

// Fetch tasks from API
async function fetchTasks() {
    try {
        const response = await fetch('/api/tasks');
        
        if (!response.ok) {
            const errData = await response.json();
            throw new Error(errData.message || 'Server error occurred');
        }
        
        const tasks = await response.json();
        
        // Hide connection alert if it was showing
        hideDBAlert();
        
        // Render tasks
        renderTasks(tasks);
    } catch (error) {
        console.error("Error fetching tasks:", error);
        showDBAlert(error.message);
        renderErrorState(error.message);
    }
}

// Render task list into checklist view
function renderTasks(tasks) {
    // Update record count badge
    recordsCount.textContent = `${tasks.length} Task${tasks.length === 1 ? '' : 's'}`;
    
    if (tasks.length === 0) {
        tasksListContainer.innerHTML = `
            <div class="empty-state">
                <p>No tasks yet. Fill in the form on the left to add a task!</p>
            </div>
        `;
        return;
    }
    
    let html = '';
    tasks.forEach(task => {
        const completedClass = task.completed ? 'completed' : '';
        const checkedClass = task.completed ? 'checked' : '';
        
        // Highlight background if currently editing
        const isEditingThis = isEditMode && editTaskId === task.id;
        const editingStyle = isEditingThis ? 'style="border-color: var(--accent-primary); background-color: #f0f7ff;"' : '';
        
        html += `
            <div class="task-item ${completedClass}" ${editingStyle}>
                <!-- Circular Checkbox -->
                <div class="checkbox-container">
                    <div class="task-checkbox ${checkedClass}" 
                         title="${task.completed ? 'Mark pending' : 'Mark completed'}"
                         onclick="toggleTaskComplete(${task.id}, '${escapeQuote(task.title)}', '${escapeQuote(task.description)}', ${task.completed})">
                    </div>
                </div>
                
                <!-- Content Area -->
                <div class="task-content">
                    <div class="task-title">${escapeHTML(task.title)}</div>
                    ${task.description ? `<div class="task-desc">${escapeHTML(task.description)}</div>` : ''}
                    <div class="task-time">Created / Updated: ${task.created_at}</div>
                </div>
                
                <!-- Actions Buttons -->
                <div class="task-actions">
                    <button class="action-btn" title="Edit Task" onclick='startEditTask(${JSON.stringify(task).replace(/'/g, "&#39;")})'>
                        ✏️
                    </button>
                    <button class="action-btn" title="Delete Task" onclick='deleteTask(${task.id})'>
                        🗑️
                    </button>
                </div>
            </div>
        `;
    });
    
    tasksListContainer.innerHTML = html;
}

// Quick toggle task completion status
window.toggleTaskComplete = async function(id, title, description, currentStatus) {
    const payload = {
        title: title,
        description: description,
        completed: !currentStatus
    };
    
    try {
        const response = await fetch(`/api/tasks/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        
        const result = await response.json();
        if (!response.ok) {
            throw new Error(result.message || 'Failed to update task state');
        }
        
        // If we are currently editing this task, keep the form values synced
        if (isEditMode && editTaskId === id) {
            taskCompletedSelect.value = (!currentStatus).toString();
        }
        
        // Refresh task list
        fetchTasks();
    } catch (error) {
        console.error("Error toggling completion:", error);
        alert(`Failed to update status: ${error.message}`);
    }
};

// Form Submission (Create or Update)
async function handleFormSubmit(e) {
    e.preventDefault();
    
    const title = taskTitleInput.value.trim();
    const description = taskDescriptionInput.value.trim();
    
    // Status defaults to false (Pending) unless editing and specified otherwise
    const completed = isEditMode ? (taskCompletedSelect.value === 'true') : false;
    
    if (!title) {
        alert("Please enter a task title.");
        return;
    }
    
    const payload = {
        title: title,
        description: description,
        completed: completed
    };
    
    try {
        let response;
        if (isEditMode) {
            response = await fetch(`/api/tasks/${editTaskId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
        } else {
            response = await fetch('/api/tasks', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
        }
        
        const result = await response.json();
        
        if (!response.ok) {
            throw new Error(result.message || 'Operation failed');
        }
        
        // Reset form and refetch tasks immediately
        resetForm();
        fetchTasks();
        
    } catch (error) {
        console.error("Error submitting form:", error);
        alert(`Failed to save task: ${error.message}`);
    }
}

// Enter edit mode
window.startEditTask = function(task) {
    isEditMode = true;
    editTaskId = task.id;
    
    // Update header
    formTitle.textContent = `Edit Task #${task.id}`;
    
    // Show status dropdown in edit mode
    if (completedGroup) {
        completedGroup.style.display = 'flex';
    }
    
    // Set inputs
    taskIdInput.value = task.id;
    taskTitleInput.value = task.title;
    taskDescriptionInput.value = task.description || '';
    taskCompletedSelect.value = task.completed ? 'true' : 'false';
    
    // Change buttons
    submitBtn.textContent = 'Save Task';
    resetBtn.classList.remove('hidden');
    
    // Scroll to form card
    document.querySelector('.form-card').scrollIntoView({ behavior: 'smooth' });
};

// Reset Form to Create state
function resetForm() {
    isEditMode = false;
    editTaskId = null;
    
    // Reset header
    formTitle.textContent = 'Add Task';
    
    // Hide status dropdown in create mode
    if (completedGroup) {
        completedGroup.style.display = 'none';
    }
    
    // Reset Form fields
    taskForm.reset();
    taskIdInput.value = '';
    
    // Reset buttons
    submitBtn.textContent = 'Add Task';
    resetBtn.classList.add('hidden');
}

// Delete Task
window.deleteTask = async function(id) {
    if (!confirm(`Are you sure you want to delete this task?`)) {
        return;
    }
    
    try {
        const response = await fetch(`/api/tasks/${id}`, {
            method: 'DELETE'
        });
        
        const result = await response.json();
        if (!response.ok) {
            throw new Error(result.message || 'Failed to delete task');
        }
        
        // If we deleted the task we were currently editing, reset the form
        if (isEditMode && editTaskId === id) {
            resetForm();
        }
        
        // Refresh task list
        fetchTasks();
    } catch (error) {
        console.error("Error deleting task:", error);
        alert(`Failed to delete task: ${error.message}`);
    }
};

// Show/Hide Database Connection Alert
function showDBAlert(message) {
    dbAlertMsg.textContent = message || "Could not connect to MySQL database.";
    dbAlert.classList.remove('hidden');
}

function hideDBAlert() {
    dbAlert.classList.add('hidden');
}

// Show error state inside task list
function renderErrorState(message) {
    recordsCount.textContent = '0 Tasks';
    tasksListContainer.innerHTML = `
        <div class="empty-state" style="color: var(--error-color);">
            <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">⚠️</div>
            <strong style="display: block; margin-bottom: 0.5rem;">Database Connection Failure</strong>
            <span style="font-size: 0.85rem; color: var(--text-secondary); max-width: 400px; display: inline-block;">
                ${escapeHTML(message)}. Please make sure your database server is running and credentials in <code>app.py</code> match your environment.
            </span>
        </div>
    `;
}

// Helper to escape HTML and prevent XSS
function escapeHTML(str) {
    if (!str) return '';
    return str
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#039;');
}

// Helper to escape quotes in onclick event string parameters
function escapeQuote(str) {
    if (!str) return '';
    return str
        .replace(/\\/g, '\\\\')
        .replace(/'/g, "\\'")
        .replace(/"/g, '&quot;')
        .replace(/\n/g, '\\n')
        .replace(/\r/g, '\\r');
}
