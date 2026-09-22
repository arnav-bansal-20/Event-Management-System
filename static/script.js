const API_URL = "/api";

document.addEventListener('DOMContentLoaded', () => {
    fetchEvents();
    fetchNextEvent();

    document.getElementById('add-event-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const name = document.getElementById('event-name').value.trim();
        const priority = parseInt(document.getElementById('event-priority').value, 10);
        const date = document.getElementById('event-date').value;
        const desc = document.getElementById('event-desc').value.trim();

        const payload = { name, priority, description: desc, date };

        try {
            const res = await fetch(`${API_URL}/events`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });
            if (res.ok) {
                document.getElementById('add-event-form').reset();
                fetchEvents();
                fetchNextEvent();
            } else {
                const data = await res.json();
                alert(data.error || "Failed to add event");
            }
        } catch (err) {
            console.error("Error adding event:", err);
            alert("Network error or server down");
        }
    });

    document.querySelector('.close-modal').addEventListener('click', () => {
        document.getElementById('modal').classList.add('hidden');
    });

    document.getElementById('add-participant-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const eventName = document.getElementById('modal-event-name-input').value;
        const pName = document.getElementById('participant-name').value.trim();

        if (!pName) return;

        try {
            const res = await fetch(`${API_URL}/participants`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ eventName, participantName: pName })
            });
            if (res.ok) {
                document.getElementById('participant-name').value = '';
                openParticipantModal(eventName);
                fetchEvents();
            } else {
                const data = await res.json();
                alert(data.error || "Failed to add participant");
            }
        } catch (err) {
            console.error(err);
        }
    });
});

async function fetchEvents() {
    const grid = document.getElementById('events-grid');
    grid.innerHTML = '<div class="loading-spinner"></div>';

    try {
        const res = await fetch(`${API_URL}/events`);
        const events = await res.json();

        grid.innerHTML = '';
        if (!events || events.length === 0) {
            grid.innerHTML = '<p style="grid-column: 1/-1; text-align: center; color: var(--text-secondary);">No events found.</p>';
            return;
        }

        events.forEach(event => {
            const card = document.createElement('div');
            card.className = 'event-card';
            const participantCount = event.participants ? event.participants.length : 0;
            card.innerHTML = `
                <div class="event-header">
                    <h3>${escapeHtml(event.name)}</h3>
                    <span class="event-badge">Priority ${event.priority}</span>
                </div>
                <div style="font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 0.5rem;">
                    <i class="far fa-calendar-alt"></i> ${escapeHtml(event.date || 'No Date')}
                </div>
                <p class="event-desc">${escapeHtml(event.description || 'No description')}</p>
                <div class="participant-count-badge">
                    <i class="fas fa-users"></i> ${participantCount} Participant${participantCount === 1 ? '' : 's'}
                </div>
                <div class="event-actions">
                    <button class="btn btn-secondary btn-sm" onclick="openParticipantModal('${escapeJsString(event.name)}')">Participants</button>
                    <button class="btn btn-danger btn-sm" onclick="deleteEvent('${escapeJsString(event.name)}')">Delete</button>
                </div>
            `;
            grid.appendChild(card);
        });
    } catch (err) {
        console.error(err);
        grid.innerHTML = '<p style="grid-column: 1/-1; text-align: center; color: var(--danger);">Error loading events.</p>';
    }
}

async function fetchNextEvent() {
    const container = document.getElementById('next-event-content');
    const badge = document.getElementById('next-priority-badge');

    try {
        const res = await fetch(`${API_URL}/events/next`);
        const events = await res.json();

        if (events && events.length > 0) {
            badge.textContent = `Priority ${events[0].priority}`;

            container.innerHTML = '';
            events.forEach(event => {
                const div = document.createElement('div');
                div.style.marginBottom = '1.5rem';
                div.style.borderBottom = '1px solid rgba(255,255,255,0.1)';
                div.style.paddingBottom = '1rem';
                div.innerHTML = `
                    <h3 style="font-size: 1.8rem; margin-bottom: 0.5rem; color: var(--highlight);">
                        ${escapeHtml(event.name)}
                    </h3>
                    <p style="font-size: 0.9rem; color: var(--text-secondary); margin-bottom: 0.5rem;">
                        <i class="far fa-calendar-alt"></i> ${escapeHtml(event.date || 'No Date')}
                    </p>
                    <p>${escapeHtml(event.description || 'No description')}</p>
                    <div style="margin-top: 1rem;">
                        <span style="font-size: 0.8rem; color: var(--text-secondary);">Highest Priority Action Item</span>
                    </div>
                `;
                container.appendChild(div);
            });

            if (container.lastElementChild) {
                container.lastElementChild.style.borderBottom = 'none';
            }
        } else {
            badge.textContent = "Idle";
            container.innerHTML = `<p style="color: var(--text-secondary);">No upcoming events.</p>`;
        }
    } catch (err) {
        console.error(err);
        container.innerHTML = `<p style="color: var(--danger);">Error loading next event.</p>`;
    }
}

async function deleteEvent(name) {
    if (!confirm(`Delete event '${name}'?`)) return;

    try {
        const res = await fetch(`${API_URL}/events?name=${encodeURIComponent(name)}`, { method: 'DELETE' });
        if (res.ok) {
            fetchEvents();
            fetchNextEvent();
        } else {
            const data = await res.json();
            alert(data.error || "Failed to delete");
        }
    } catch (err) {
        alert("Failed to delete (Network Error)");
    }
}

window.openParticipantModal = async (nameOrObj) => {
    const name = typeof nameOrObj === 'string' ? nameOrObj : (nameOrObj ? nameOrObj.name : '');

    document.getElementById('modal').classList.remove('hidden');
    document.getElementById('modal-event-name').textContent = name;
    document.getElementById('modal-event-name-input').value = name;

    const list = document.getElementById('modal-participants-list');
    list.innerHTML = '<div class="loading-spinner"></div>';

    try {
        const res = await fetch(`${API_URL}/events`);
        const events = await res.json();
        const event = events.find(e => e.name === name);

        list.innerHTML = '';
        if (event && event.participants && event.participants.length > 0) {
            event.participants.forEach(p => {
                const div = document.createElement('div');
                div.className = 'participant-item';
                div.textContent = `${p.name} (ID: ${p.id})`;
                list.appendChild(div);
            });
        } else {
            list.innerHTML = '<p style="color: var(--text-secondary); font-size: 0.9rem;">No participants yet.</p>';
        }
    } catch (e) {
        list.innerHTML = '<p style="color: var(--danger);">Error loading participants.</p>';
    }
};

window.deleteEvent = deleteEvent;
window.fetchEvents = fetchEvents;

async function searchEventByName() {
    const name = document.getElementById('search-name').value.trim();
    if (!name) {
        fetchEvents();
        return;
    }

    const grid = document.getElementById('events-grid');
    grid.innerHTML = '<div class="loading-spinner"></div>';

    try {
        const res = await fetch(`${API_URL}/events/search?name=${encodeURIComponent(name)}`);
        if (res.status === 404) {
            grid.innerHTML = '<p style="grid-column: 1/-1; text-align: center; color: var(--text-secondary);">Event not found.</p>';
            return;
        }
        const event = await res.json();

        grid.innerHTML = '';
        const card = document.createElement('div');
        card.className = 'event-card';
        card.style.border = '1px solid var(--highlight)';
        const participantCount = event.participants ? event.participants.length : 0;
        card.innerHTML = `
            <div class="event-header">
                <h3>${escapeHtml(event.name)} <small style="font-size: 0.75rem; color: var(--text-secondary);">(ID: ${event.id})</small></h3>
                <span class="event-badge">Priority ${event.priority}</span>
            </div>
            <div style="font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 0.5rem;">
                <i class="far fa-calendar-alt"></i> ${escapeHtml(event.date || 'No Date')}
            </div>
            <p class="event-desc">${escapeHtml(event.description || 'No description')}</p>
            <div class="participant-count-badge">
                <i class="fas fa-users"></i> ${participantCount} Participant${participantCount === 1 ? '' : 's'}
            </div>
            <div class="event-actions">
                <button class="btn btn-secondary btn-sm" onclick="openParticipantModal('${escapeJsString(event.name)}')">Participants</button>
                <button class="btn btn-danger btn-sm" onclick="deleteEvent('${escapeJsString(event.name)}')">Delete</button>
            </div>
        `;
        grid.appendChild(card);
    } catch (err) {
        console.error(err);
        grid.innerHTML = '<p style="grid-column: 1/-1; text-align: center; color: var(--danger);">Error searching.</p>';
    }
}
window.searchEventByName = searchEventByName;

function escapeHtml(str) {
    if (!str) return '';
    return String(str).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

function escapeJsString(str) {
    if (!str) return '';
    return String(str).replace(/'/g, "\\'").replace(/"/g, '\\"');
}
