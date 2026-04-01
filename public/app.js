// DOM Elements
const tableBody = document.getElementById('tableBody');
const selectAllCheckbox = document.getElementById('selectAllCheckbox');
const markDeletedBtn = document.getElementById('markDeletedBtn');
const restoreBtn = document.getElementById('restoreBtn');
const copyActiveBtn = document.getElementById('copyActiveBtn');
const loadingSpinner = document.getElementById('loadingSpinner');
const copyMessage = document.getElementById('copyMessage');
const noDataMessage = document.getElementById('noDataMessage');

let allRows = [];

// Format timestamp to YYYY/MM/DD HH:mm:ss
function formatDate(timestamp) {
  const date = new Date(timestamp);
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  const hours = String(date.getHours()).padStart(2, '0');
  const minutes = String(date.getMinutes()).padStart(2, '0');
  const seconds = String(date.getSeconds()).padStart(2, '0');
  
  return `${year}/${month}/${day} ${hours}:${minutes}:${seconds}`;
}

// Fetch and display YouTube links
async function loadData() {
  showLoading(true);
  try {
    const response = await fetch('/api/youtube-links');
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    
    if (data.length === 0) {
      tableBody.innerHTML = '';
      noDataMessage.style.display = 'block';
    } else {
      noDataMessage.style.display = 'none';
      displayData(data);
    }
    
    updateButtonStates();
  } catch (error) {
    console.error('Error loading data:', error);
    alert('Failed to load data. Please refresh the page.');
  } finally {
    showLoading(false);
  }
}

// Display data in table
function displayData(data) {
  allRows = data;
  tableBody.innerHTML = '';
  selectAllCheckbox.checked = false;

  data.forEach((row) => {
    const tr = document.createElement('tr');
    const statusClass = row.deleted ? 'status-deleted' : 'status-active';
    const statusText = row.deleted ? 'Deleted' : 'Active';

    tr.innerHTML = `
      <td>
        <input type="checkbox" class="row-checkbox" data-id="${row.id}">
      </td>
      <td>${escapeHtml(row.videoId)}</td>
      <td>
        <a href="${escapeHtml(row.youtubeLink)}" target="_blank">
          ${escapeHtml(row.youtubeLink)}
        </a>
      </td>
      <td>${formatDate(row.createdAt)}</td>
      <td>
        <span class="status ${statusClass}">${statusText}</span>
      </td>
    `;

    tableBody.appendChild(tr);
  });

  attachCheckboxListeners();
}

// Update button states based on selection
function updateButtonStates() {
  const selectedCheckboxes = document.querySelectorAll('.row-checkbox:checked');
  const hasSelection = selectedCheckboxes.length > 0;

  markDeletedBtn.disabled = !hasSelection;
  restoreBtn.disabled = !hasSelection;
}

// Get selected IDs
function getSelectedIds() {
  const checkboxes = document.querySelectorAll('.row-checkbox:checked');
  return Array.from(checkboxes).map((cb) => cb.dataset.id);
}

// Update deleted status
async function updateDeletedStatus(deleted) {
  const ids = getSelectedIds();
  
  if (ids.length === 0) {
    alert('Please select at least one row');
    return;
  }

  showLoading(true);
  try {
    const response = await fetch('/api/update-deleted', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ ids, deleted }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    // Update UI without reloading
    updateUIAfterDelete(ids, deleted);
    updateButtonStates();
    
  } catch (error) {
    console.error('Error updating records:', error);
    alert('Failed to update records. Please try again.');
  } finally {
    showLoading(false);
  }
}

// Update UI after delete/restore
function updateUIAfterDelete(ids, deleted) {
  ids.forEach((id) => {
    const row = allRows.find((r) => r.id === id);
    if (row) {
      row.deleted = deleted;
    }
  });

  // Refresh table display
  displayData(allRows);
}

// Show/Hide loading spinner
function showLoading(show) {
  loadingSpinner.style.display = show ? 'inline-block' : 'none';
}

// Escape HTML to prevent XSS
function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

// Attach checkbox event listeners
function attachCheckboxListeners() {
  document.querySelectorAll('.row-checkbox').forEach((checkbox) => {
    checkbox.addEventListener('change', updateButtonStates);
  });
}

// Select All checkbox
selectAllCheckbox.addEventListener('change', () => {
  document.querySelectorAll('.row-checkbox').forEach((checkbox) => {
    checkbox.checked = selectAllCheckbox.checked;
  });
  updateButtonStates();
});

// Mark as Deleted button
markDeletedBtn.addEventListener('click', () => {
  if (confirm('Mark selected items as deleted?')) {
    updateDeletedStatus(1);
  }
});

// Restore button
restoreBtn.addEventListener('click', () => {
  if (confirm('Restore selected items?')) {
    updateDeletedStatus(0);
  }
});

// Filter and display only active records
function filterTableActive() {
  const activeRows = allRows.filter((row) => row.deleted === 0);
  displayData(activeRows);
}

// Copy Active IDs button
copyActiveBtn.addEventListener('click', () => {
  // First, filter and display only active records
  filterTableActive();
  
  const activeRows = allRows.filter((row) => row.deleted === 0);
  
  if (activeRows.length === 0) {
    alert('No active items to copy');
    return;
  }
  
  // Check all active row checkboxes
  const activeIds = activeRows.map((row) => row.videoId);
  const activeRowIds = activeRows.map((row) => row.id);
  
  document.querySelectorAll('.row-checkbox').forEach((checkbox) => {
    checkbox.checked = activeRowIds.includes(checkbox.dataset.id);
  });
  
  // Copy to clipboard
  const videoIds = activeIds.join('\n');
  navigator.clipboard.writeText(videoIds).then(() => {
    showCopyMessage();
    updateButtonStates();
  }).catch((err) => {
    console.error('Failed to copy:', err);
    alert('Failed to copy to clipboard');
  });
});

// Show copy message
function showCopyMessage() {
  copyMessage.style.display = 'inline-block';
  setTimeout(() => {
    copyMessage.style.display = 'none';
  }, 2000);
}

// Load data on page load
document.addEventListener('DOMContentLoaded', loadData);
