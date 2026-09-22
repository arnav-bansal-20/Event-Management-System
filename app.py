import os
import ctypes
import random
from flask import Flask, jsonify, request, send_from_directory

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, 'static')

app = Flask(__name__, static_folder=STATIC_DIR)

TABLE_SIZE = 100
HEAP_SIZE = 100
MAX_NAME = 100
MAX_DESC = 256

class Participant(ctypes.Structure):
    pass
Participant._fields_ = [
    ("id", ctypes.c_int),
    ("name", ctypes.c_char * MAX_NAME),
    ("next", ctypes.POINTER(Participant))
]

class Event(ctypes.Structure):
    pass
Event._fields_ = [
    ("id", ctypes.c_int),
    ("name", ctypes.c_char * MAX_NAME),
    ("priority", ctypes.c_int),
    ("description", ctypes.c_char * MAX_DESC),
    ("date", ctypes.c_char * 20),
    ("participants", ctypes.POINTER(Participant)),
    ("nextHash", ctypes.POINTER(Event))
]

class System(ctypes.Structure):
    _fields_ = [
        ("eventHashTable", ctypes.POINTER(Event) * TABLE_SIZE),
        ("eventHeap", ctypes.POINTER(Event) * HEAP_SIZE),
        ("heapSize", ctypes.c_int)
    ]

# Find and load the shared library
lib = None
possible_lib_names = [
    os.path.join(BASE_DIR, "event_system.dylib"),
    os.path.join(BASE_DIR, "event_system.so"),
    os.path.join(BASE_DIR, "event_system.dll"),
    "./event_system.dylib",
    "./event_system.so",
    "./event_system.dll"
]

for candidate in possible_lib_names:
    if os.path.exists(candidate):
        try:
            lib = ctypes.CDLL(candidate)
            print(f"Loaded library: {candidate}")
            break
        except OSError as e:
            print(f"Could not load {candidate}: {e}")

if not lib:
    # Try compiling if not present
    print("Compiled library not found. Attempting to compile automatically...")
    if os.name == 'nt':
        os.system(f'gcc -shared -o "{os.path.join(BASE_DIR, "event_system.dll")}" "{os.path.join(BASE_DIR, "functions.c")}"')
        dll_file = os.path.join(BASE_DIR, "event_system.dll")
    else:
        os.system(f'gcc -shared -fPIC -o "{os.path.join(BASE_DIR, "event_system.dylib")}" "{os.path.join(BASE_DIR, "functions.c")}"')
        dll_file = os.path.join(BASE_DIR, "event_system.dylib")
    
    if os.path.exists(dll_file):
        try:
            lib = ctypes.CDLL(dll_file)
            print(f"Successfully compiled and loaded {dll_file}")
        except OSError as e:
            print(f"Failed to load newly compiled library: {e}")

if lib:
    lib.initSystem.argtypes = [ctypes.POINTER(System)]
    lib.clearSystem.argtypes = [ctypes.POINTER(System)]
    lib.addEvent.argtypes = [ctypes.POINTER(System), ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_char_p]
    lib.addEvent.restype = ctypes.c_int
    lib.searchEvent.argtypes = [ctypes.POINTER(System), ctypes.c_char_p]
    lib.searchEvent.restype = ctypes.POINTER(Event)
    lib.deleteEventByName.argtypes = [ctypes.POINTER(System), ctypes.c_char_p]
    lib.deleteEventByName.restype = ctypes.c_int
    lib.getNextEvent.argtypes = [ctypes.POINTER(System)]
    lib.getNextEvent.restype = ctypes.POINTER(Event)
    lib.getNextHighPriorityEvents.argtypes = [ctypes.POINTER(System), ctypes.POINTER(ctypes.POINTER(Event)), ctypes.POINTER(ctypes.c_int)]
    lib.addParticipant.argtypes = [ctypes.POINTER(System), ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p]
    lib.saveSystemToFile.argtypes = [ctypes.POINTER(System), ctypes.c_char_p]
    lib.loadSystemFromFile.argtypes = [ctypes.POINTER(System), ctypes.c_char_p]

    sys_instance = System()
    lib.initSystem(ctypes.byref(sys_instance))

    DB_FILE = os.path.join(BASE_DIR, "events.db").encode('utf-8')
    lib.loadSystemFromFile(ctypes.byref(sys_instance), DB_FILE)
else:
    print("WARNING: C Library not loaded. Functionality will fail.")

current_id = 0
def update_max_id():
    global current_id
    if not lib: return
    current_id = 0
    for i in range(TABLE_SIZE):
        curr = sys_instance.eventHashTable[i]
        while curr:
            try:
                e = curr.contents
                if e.id > current_id:
                    current_id = e.id
                curr = e.nextHash
            except (ValueError, ctypes.ArgumentError):
                break

if lib:
    update_max_id()

@app.before_request
def reload_data():
    if lib:
        lib.clearSystem(ctypes.byref(sys_instance))
        lib.loadSystemFromFile(ctypes.byref(sys_instance), DB_FILE)
        update_max_id()

@app.route('/')
def index():
    return send_from_directory(BASE_DIR, 'index.html')

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory(STATIC_DIR, filename)

@app.route('/api/events', methods=['GET'])
def get_events():
    events = []
    if not lib: return jsonify([])
    for i in range(TABLE_SIZE):
        curr = sys_instance.eventHashTable[i]
        while curr:
            try:
                e = curr.contents
                parts = []
                p = e.participants
                while p:
                    pd = p.contents
                    parts.append({"id": pd.id, "name": pd.name.decode('utf-8', errors='ignore')})
                    p = pd.next
                events.append({
                    "id": e.id,
                    "name": e.name.decode('utf-8', errors='ignore'),
                    "priority": e.priority,
                    "description": e.description.decode('utf-8', errors='ignore'),
                    "date": e.date.decode('utf-8', errors='ignore'),
                    "participants": parts
                })
                curr = e.nextHash
            except (ValueError, ctypes.ArgumentError):
                break
    return jsonify(events)

@app.route('/api/events/next', methods=['GET'])
def get_next():
    if not lib: return jsonify([])
    
    buffer_type = ctypes.POINTER(Event) * 100
    events_buffer = buffer_type()
    count = ctypes.c_int(0)
    
    lib.getNextHighPriorityEvents(ctypes.byref(sys_instance), events_buffer, ctypes.byref(count))
    
    result = []
    try:
        for i in range(count.value):
            e_ptr = events_buffer[i]
            if not e_ptr: continue
            
            e = e_ptr.contents
            result.append({
                "id": e.id,
                "name": e.name.decode('utf-8', errors='ignore'),
                "priority": e.priority,
                "description": e.description.decode('utf-8', errors='ignore'),
                "date": e.date.decode('utf-8', errors='ignore')
            })
        return jsonify(result)
    except Exception as e:
        print(f"Error fetching next events: {e}")
        return jsonify([])

@app.route('/api/events/search', methods=['GET'])
def search_event_by_name():
    if not lib: return jsonify({"error": "Lib missing"}), 500
    name = request.args.get('name')
    if not name:
        return jsonify({"error": "Name query parameter required"}), 400
    
    name_b = name.encode('utf-8')
    e_ptr = lib.searchEvent(ctypes.byref(sys_instance), name_b)
    
    try:
        if not e_ptr:
            return jsonify(None), 404
        
        e = e_ptr.contents
        parts = []
        p = e.participants
        while p:
            pd = p.contents
            parts.append({"id": pd.id, "name": pd.name.decode('utf-8', errors='ignore')})
            p = pd.next
            
        return jsonify({
            "id": e.id,
            "name": e.name.decode('utf-8', errors='ignore'),
            "priority": e.priority,
            "description": e.description.decode('utf-8', errors='ignore'),
            "date": e.date.decode('utf-8', errors='ignore'),
            "participants": parts
        })
    except Exception:
        return jsonify(None), 404

@app.route('/api/events', methods=['POST'])
def add_event():
    global current_id
    if not lib: return jsonify({"error": "Lib missing"}), 500
    
    data = request.json or {}
    name = data.get('name')
    try:
        priority = int(data.get('priority', 50))
    except (ValueError, TypeError):
        priority = 50
    desc = data.get('description', "")
    date_str = data.get('date', "")
    
    new_id = current_id + 1
    current_id = new_id

    if not name:
        return jsonify({"error": "Event name is required"}), 400
        
    name_b = name.encode('utf-8')
    desc_b = desc.encode('utf-8')
    date_b = date_str.encode('utf-8')
    
    result = lib.addEvent(ctypes.byref(sys_instance), new_id, name_b, priority, desc_b, date_b)
    if result == 1:
        lib.saveSystemToFile(ctypes.byref(sys_instance), DB_FILE)
        return jsonify({"success": True, "id": new_id})
    else:
        return jsonify({"error": "Event name already exists"}), 400

@app.route('/api/events', methods=['DELETE'])
def delete_event():
    if not lib: return jsonify({"error": "Lib missing"}), 500
    name = request.args.get('name')
    if not name:
        return jsonify({"error": "Event name is required"}), 400
        
    name_b = name.encode('utf-8')
    res = lib.deleteEventByName(ctypes.byref(sys_instance), name_b)
    if res == 1:
        lib.saveSystemToFile(ctypes.byref(sys_instance), DB_FILE)
        return jsonify({"success": True})
    else:
        return jsonify({"error": "Event not found"}), 404

@app.route('/api/participants', methods=['POST'])
def add_participant():
    if not lib: return jsonify({"error": "Lib missing"}), 500
    data = request.json or {}
    event_name = data.get('eventName')
    p_name = data.get('participantName')

    p_id = data.get('id', random.randint(1000, 9999)) 
    
    if not event_name or not p_name:
        return jsonify({"error": "Event name and participant name are required"}), 400
    
    lib.addParticipant(ctypes.byref(sys_instance), event_name.encode('utf-8'), p_id, p_name.encode('utf-8'))
    lib.saveSystemToFile(ctypes.byref(sys_instance), DB_FILE)
    return jsonify({"success": True})

if __name__ == '__main__':
    print("Starting Event Management System server on http://127.0.0.1:5000 ...")
    app.run(debug=True, host='127.0.0.1', port=5000)
