from flask import Flask, request, jsonify, render_template
from backend.models import EventCalendar, TodoCalendar

app = Flask(__name__)
event_calendar = EventCalendar()
todo_calendar = TodoCalendar()

@app.route('/events', methods=['POST'])
def add_event():
    data = request.get_json()
    user_id = data.get('user_id')
    event_name = data.get('name')
    event_date = data.get('date')

    if not event_name or not event_date:
        return jsonify({"status": "error", "message": "Missing event name or event date!"}), 400

    event_calendar.save_event(user_id, event_name, event_date)
    return jsonify({"status": "success", "message": "Event added successfully!"}), 201


@app.route('/todos', methods=['POST'])
def add_todo():
    data = request.get_json()
    user_id = data.get('user_id')
    todo_name = data.get('name')
    todo_date = data.get('date')
    
    if not todo_name or not todo_date:
        return jsonify({"status": "error", "message": "Missing todo name or todo date!"}), 400

    todo_calendar.save_todo(user_id, todo_name, todo_date)
    return jsonify({"status": "success", "message": "To-Do added successfully!"}), 201

@app.route('/events/by_date', methods=['GET']) 
def get_data_from_date():
    
    data = request.get_json()
    date = data.get('date')
    user_id = data.get('user_id')

    if not date:
        return jsonify({"status": "error", "message": "Missing date!"}), 400
    
    todo_events = todo_calendar.get_date_events(user_id, date)
    calendar_events = event_calendar.get_date_events(user_id, date)
    events = [{"name": name} for (name,) in (todo_events + calendar_events)]
    return jsonify(events)

@app.route('/events', methods=['GET'])
def get_all_events():
    data = request.get_json()
    user_id = data.get('user_id')
    if not user_id:
        return jsonify({"status": "error", "message": "Missing user_id!"}), 400

    events = event_calendar.get_events(user_id)
    return jsonify(events)


@app.route('/todos', methods=['GET'])
def get_all_todos():
    data = request.get_json()
    user_id = data.get('user_id')
    if not user_id:
        return jsonify({"status": "error", "message": "Missing user_id!"}), 400

    todos = todo_calendar.get_todos(user_id)
    return jsonify(todos)


@app.route('/events/delete', methods=['POST']) 
def delete_event():
    data = request.get_json()

    date = data.get('date')
    user_id = data.get('user_id')
    name = data.get('name')

    if not date or not name:
        return jsonify({"status": "error", "message": "Missing date or event name!"}), 400
    
    app.logger.info(f"Attempting to delete event '{name}' on {date}")
    
    deleted_from_events = event_calendar.delete_event(user_id, name, date)
    deleted_from_todos = todo_calendar.delete_event(user_id, name, date)

    app.logger.info(f"Deleted from events: {deleted_from_events}, Deleted from todos: {deleted_from_todos}")
    
    if deleted_from_events or deleted_from_todos:
        app.logger.info(f"Event deleted: {name} on {date}")
        return jsonify({"status": "success", "message": "Event deleted successfully!"}), 200
    else:
        app.logger.error(f"Event not found: {name} on {date}")
        return jsonify({"status": "error", "message": "Event not found!"}), 404
    

@app.route('/calendar')
def calendar():
    user_id = request.args.get('user_id')
    return render_template('calendar.html', user_id=user_id)
