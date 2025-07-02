from flask_pymongo import PyMongo
from typing import Optional
from datetime import datetime
from dataclasses import dataclass,field,asdict
from bson.objectid import ObjectId
from enum import Enum
from datetime import datetime, timezone



mongo = PyMongo()

#Required schema
@dataclass
class WebhookEntry:
    request_id: str
    author: str
    action: str
    from_branch: str
    to_branch: str
    timestamp: str 
    _id: ObjectId = field(default_factory=ObjectId)



class ActionType(str, Enum):
    PUSH = "PUSH"
    PULL_REQUEST = "PULL_REQUEST"
    MERGE = "MERGE"



#responsible for parsing JSON response to Required Schema 
def parse_push_event(payload) -> WebhookEntry:
    branch = payload['ref'].split('/')[-1]
    head_commit = payload.get('head_commit')
    if not head_commit:
        return 

    pushed_timestamp = datetime.fromtimestamp(                      #converting it to ISO format from the format "1751369707"
        payload['repository']['pushed_at'], tz=timezone.utc
    ).isoformat()

    return WebhookEntry(
        request_id=head_commit['id'],
        author=payload['pusher']['name'],
        action=ActionType.PUSH,
        from_branch=branch,
        to_branch=branch,
        timestamp=pushed_timestamp
    )

def parse_pull_request_event(data) -> WebhookEntry:
    pr = data['pull_request']

    return WebhookEntry(
        request_id=str(pr['id']),
        author=pr['user']['login'],
        action=ActionType.PULL_REQUEST,
        from_branch=pr['head']['ref'],
        to_branch=pr['base']['ref'],
        timestamp=pr['closed_at'] if (data['action'] == 'closed') else pr['created_at']
    )


def parse_merge_event(data) -> WebhookEntry:
    pr = data['pull_request']

    return WebhookEntry(
        request_id=str(pr['id']),
        author=pr['user']['login'],
        action=ActionType.MERGE,
        from_branch=pr['head']['ref'],
        to_branch=pr['base']['ref'],
        timestamp=pr['merged_at'] 
    )


# inserts the data to database
def save_to_db(data: WebhookEntry):
    try:
        existing = mongo.db.actions.find_one({
            "request_id": data.request_id,
            "action": data.action  
        })
        if existing:
            print("Duplicate entry. Skipping insert.")
            return
        
        mongo.db.actions.insert_one(asdict(data)) #converting to dict for insertion
    except Exception as e:
        print("DB Save Error:", e)