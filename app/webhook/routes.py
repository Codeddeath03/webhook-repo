from flask import Blueprint, request,json, render_template, jsonify
from app.extensions import mongo,WebhookEntry,ActionType,parse_pull_request_event,parse_push_event,save_to_db,parse_merge_event
webhook = Blueprint('Webhook', __name__, url_prefix='/webhook')

@webhook.route('/receiver', methods=["POST"])
def receiver():
    if request.content_type != 'application/json':
        return jsonify({"error": "Invalid content type"}), 400
    json_data = request.json
    print("ok1")
   # print(json_data)
    event_type = request.headers.get('X-GitHub-Event', '').upper()
    action = json_data.get('action')
    #print(event_type)
    if event_type.upper() == ActionType.PULL_REQUEST.value:
        pr = json_data.get('pull_request', {})
        
        if action == 'opened':
            data = parse_pull_request_event(json_data)
            save_to_db(data)
            '''author = pr['user']['login']
            from_branch = pr['head']['ref']
            to_branch = pr['base']['ref']
            timestamp = pr['created_at']
            log_string = f'"{author}" submitted a pull request from "{from_branch}" to "{to_branch}" on {timestamp}'
            print(log_string)'''
        elif action == 'closed' and pr.get('merged'):
            data = parse_merge_event(json_data)
            save_to_db(data)
            '''pr =json_data["pull_request"]
            author = pr['merged_by']['login']
            from_branch = pr['head']['ref']
            to_branch = pr['base']['ref']
            timestamp = pr['merged_at']
            log_string = f'"{author}" merged a pull request from "{from_branch}" to "{to_branch}" on {timestamp}'
            print(log_string)'''
        else:
            """author = pr['user']['login']
            from_branch = pr['head']['ref']
            to_branch = pr['base']['ref']
            timestamp = pr['created_at']
            log_string = f'"{author}" closed a pull request from "{from_branch}" to "{to_branch}" on {timestamp}'
            print(log_string)"""
            pass
    elif event_type == ActionType.PUSH.value:
        data = parse_push_event(json_data)
        save_to_db(data)
        #save_to_db(data)
      #  print(data)
     #   print("pushed")
    
    else:
        return jsonify({"error": f"Unhandled event: {event_type}"}), 200

   
    return jsonify({"status": "success"}), 201


@webhook.route('/latest_db')
def latest_db():
    try:
        cursor = mongo.db.actions.find().sort("timestamp", -1)
        webhooks = []
        for doc in cursor:
            doc["_id"] = str(doc["_id"])
            webhooks.append(doc)
        return jsonify(webhooks)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    


