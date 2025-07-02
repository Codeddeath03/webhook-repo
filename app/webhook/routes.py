from flask import Blueprint, request, jsonify
from app.extensions import mongo,ActionType,parse_pull_request_event,parse_push_event,save_to_db,parse_merge_event


webhook = Blueprint('Webhook', __name__, url_prefix='/webhook')


#endpoint for handling github Actions
@webhook.route('/receiver', methods=["POST"])
def receiver():
    if request.content_type != 'application/json':
        return jsonify({"error": "Invalid content type"}), 400
    
    json_data = request.json
    event_type = request.headers.get('X-GitHub-Event', '').upper()   #type of action performed
                                      

    if event_type.upper() == ActionType.PULL_REQUEST.value:
        action = json_data.get('action')                        # type of pull request event
        pr = json_data.get('pull_request', {})
        
        if action == 'opened':                            #handles PR open case
            data = parse_pull_request_event(json_data)
            save_to_db(data)
            
        elif action == 'closed' and pr.get('merged'):     #handles Merge case
            data = parse_merge_event(json_data)
            save_to_db(data)            
        else:
            pass

    elif event_type == ActionType.PUSH.value:               #handles Push event case
        data = parse_push_event(json_data)
        save_to_db(data)

    return jsonify({"status": "success"}), 201


#endpoint to fetch actions stored in DB
@webhook.route('/latest_db')
def latest_db():
    try:
        cursor = mongo.db.actions.find().sort("timestamp", -1)
        actions = []
        for doc in cursor:
            doc["_id"] = str(doc["_id"])
            actions.append(doc)
        return jsonify(actions)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    


