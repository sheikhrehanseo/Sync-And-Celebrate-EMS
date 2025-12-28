from flask import Blueprint, jsonify, request
from app import mysql
from app.models.event_model import EventModel

api_bp = Blueprint('api', __name__)

# 1. READ ALL Resources (GET)
@api_bp.route('/api/events/all', methods=['GET'])
def api_get_all_events():
    cursor = mysql.connection.cursor()
    cursor.execute("SELECT * FROM event")
    events = cursor.fetchall()
    cursor.close()

    # Convert Date objects to Strings for JSON
    for event in events:
        if event.get('edate'):
            event['edate'] = str(event['edate']) 

    return jsonify(events), 200

# 2. CREATE Resource (POST)
@api_bp.route('/api/event/create', methods=['POST'])
def api_create_event():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
    
    data = request.get_json()
    
    etype = data.get('etype')
    edate = data.get('edate')
    evenue = data.get('evenue')
    ecost = data.get('ecost')
    visibility = data.get('visibility', 'private')
    etier = data.get('etier', 0) 
    emax_people = data.get('emax_people', 100)
    especial = data.get('especial', 'API Created Event')
    extras = data.get('extras', 'None')

    try:
        eid = EventModel.create_event(etype, edate, etier, ecost, evenue, emax_people, especial, visibility, extras)
        return jsonify({"message": "Event created successfully", "id": eid}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 3. READ SINGLE Resource (GET)
@api_bp.route('/api/event/<int:id>', methods=['GET'])
def api_get_single_event(id):
    event = EventModel.get_by_id(id)

    if event:
        if event.get('edate'):
            event['edate'] = str(event['edate'])
        return jsonify(event), 200
    else:
        return jsonify({"error": "Event not found"}), 404

# 4. UPDATE Resource (PUT)
@api_bp.route('/api/event/update/<int:id>', methods=['PUT'])
def api_update_event(id):
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400
        
    data = request.get_json()
    new_venue = data.get('evenue')
    
    event = EventModel.get_by_id(id)
    if not event:
        return jsonify({"error": "Event not found"}), 404
        
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("UPDATE event SET evenue = %s WHERE eid = %s", (new_venue, id))
        mysql.connection.commit()
        cursor.close()
        return jsonify({"message": "Event updated successfully", "eid": id}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 5. DELETE Resource (DELETE)
@api_bp.route('/api/event/delete/<int:id>', methods=['DELETE'])
def api_delete_event(id):
    event = EventModel.get_by_id(id)
    if not event:
        return jsonify({"error": "Event not found"}), 404
        
    try:
        EventModel.delete_event(id)
        return jsonify({"message": "Event deleted successfully", "eid": id}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
