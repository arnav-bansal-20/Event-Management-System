const API_URL = "/api";

document.addEventListener('DOMContentLoaded', () => {
    fetchEvents();
    fetchNextEvent();

    fetchNextEvent();
    document.getElementById('add-event-form').addEventListener('submit', async (e) => {
        e.preventDefault();
        const name = document.getElementById('event-name').value;
        const priority = document.getElementById('event-priority').value;
        const date = document.getElementById('event-date').value;
        const desc = document.getElementById('event-desc').value;

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
        const pName = document.getElementById('participant-name').value;

        try {
            const res = await fetch(`${API_URL}/participants`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ eventName, participantName: pName })
            });
            if (res.ok) {
                document.getElementById('participant-name').value = '';
                document.getElementById('participant-name').value = '';
                openParticipantModal({ name: eventName });
                fetchEvents();
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
        if (events.length === 0) {
            grid.innerHTML = '<p style="grid-column: 1/-1; text-align: center;">No events found.</p>';
            return;
        }

        events.forEach(event => {
            const card = document.createElement('div');
            card.className = 'event-card';
            card.innerHTML = `
                <div class="event-header">
                    <h3>${event.name}</h3>
                    <span class="event-badge">P-${event.priority}</span>
                </div>
                <div style="font-size: 0.8rem; color: var(--text-secondary); margin-bottom: 0.5rem;">
                    <i class="far fa-calendar-alt"></i> ${event.date || 'No Date'}
                </div>
                <p class="event-desc">${event.description || 'No description'}</p>
                <div class="participant-count-badge">
                    <i class="fas fa-users"></i> ${event.participants.length}
                </div>
                <div class="event-actions">
                    <button class="btn btn-secondary btn-sm" onclick="openParticipantModal('${event.name}')">Participants</button>
                    <button class="btn btn-danger btn-sm" onclick="deleteEvent('${event.name}')">Delete</button>
                </div>
            `;
            grid.appendChild(card);
        });
    } catch (err) {
        grid.innerHTML = '<p>Error loading events.</p>';
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
                        ${event.name}
                    </h3>
                    <p style="font-size: 0.9rem; color: var(--text-secondary); margin-bottom: 0.5rem;">
                        <i class="far fa-calendar-alt"></i> ${event.date || 'No Date'}
                    </p>
                    <p>${event.description}</p>
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
            container.innerHTML = `<p>No upcoming events.</p>`;
        }
    } catch (err) {
        console.error(err);
        container.innerHTML = `<p>Error loading.</p>`;
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
            alert("Failed to delete (Backend Error)");
        }
    } catch (err) {
        alert("Failed to delete (Network Error)");
    }
}


window.openParticipantModal = async (nameOrObj) => {
    const name = typeof nameOrObj === 'string' ? nameOrObj : nameOrObj.name;

    document.getElementById('modal').classList.remove('hidden');
    document.getElementById('modal-event-name').textContent = name;
    document.getElementById('modal-event-name-input').value = name;

    document.getElementById('modal-event-name-input').value = name;

    const res = await fetch(`${API_URL}/events`);
    const events = await res.json();
    const event = events.find(e => e.name === name);

    const list = document.getElementById('modal-participants-list');
    list.innerHTML = '';

    if (event && event.participants) {
        event.participants.forEach(p => {
            const div = document.createElement('div');
            div.className = 'participant-item';
            div.textContent = `${p.name} (ID: ${p.id})`;
            list.appendChild(div);
        });
    }
}

window.deleteEvent = deleteEvent;
window.fetchEvents = fetchEvents;

async function searchEventByName() {
    const name = document.getElementById('search-name').value;
    if (!name) {
        alert("Please enter a name");
        return;
    }

    const grid = document.getElementById('events-grid');
    grid.innerHTML = '<div class="loading-spinner"></div>';

    try {
        const res = await fetch(`${API_URL}/events/search?name=${encodeURIComponent(name)}`);
        if (res.status === 404) {
            grid.innerHTML = '<p style="grid-column: 1/-1; text-align: center;">Event not found.</p>';
            return;
        }
        const event = await res.json();

        grid.innerHTML = '';
        const card = document.createElement('div');
        card.className = 'event-card';
        card.style.border = '1px solid var(--highlight)';
        card.innerHTML = `
            <div class="event-header">
                <h3>${event.name} <small>(ID: ${event.id})</small></h3>
                <span class="event-badge">P-${event.priority}</span>
            </div>
            <div style="font-size: 0.8rem; color: var(--text-secondary); margin-bottom: 0.5rem;">
                <i class="far fa-calendar-alt"></i> ${event.date || 'No Date'}
            </div>
            <p class="event-desc">${event.description || 'No description'}</p>
            <div class="participant-count-badge">
                <i class="fas fa-users"></i> ${event.participants.length}
            </div>
            <div class="event-actions">
                <button class="btn btn-secondary btn-sm" onclick="openParticipantModal('${event.name}')">Participants</button>
                <button class="btn btn-danger btn-sm" onclick="deleteEvent('${event.name}')">Delete</button>
            </div>
        `;
        grid.appendChild(card);
    } catch (err) {
        console.error(err);
        grid.innerHTML = '<p>Error searching.</p>';
    }
}
window.searchEventByName = searchEventByName;
