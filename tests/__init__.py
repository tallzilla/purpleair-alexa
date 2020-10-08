import uuid
from datetime import datetime

context = {}


def new_request(name, slots={}):
    req_env = {
        "session": {
            "sessionId": f"amzn1.echo-api.session.{uuid.uuid1()}",
            "application": {
                "applicationId": f"amzn1.echo-sdk-ams.app.{uuid.uuid1()}"
            },
            "user": {
                "userId": f"amzn1.ask.account.{uuid.uuid1()}"
            },
            "new": False,
        },
        "request": {
            "requestId": f"amzn1.echo-api.request.{uuid.uuid1()}",
            "timestamp": f"{datetime.now().replace(second=0, microsecond=0).isoformat()}",
            "locale": "en-US",
            "type": "IntentRequest" if name.endswith('Intent') else name,
        }
    }

    if name.endswith('Intent'):
        req_env['request']['intent'] = {
            'name': name,
            'slots': {k: {'name': k, 'value': v} for k, v in slots.items()}
        }

    return req_env