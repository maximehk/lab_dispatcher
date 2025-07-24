import firebase_admin
from firebase_admin import auth
import functions_framework
from google.cloud import pubsub_v1
from flask import request
import json
from functools import wraps
from google.auth import default

def cors_headers(
    origin="*",
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    headers=["Content-Type", "Authorization"],
):
    """
    Decorator to add CORS headers to a Flask response for HTTP Cloud Functions.
    Handles preflight (OPTIONS) requests.
    """

    def decorator(f):
        @wraps(f)
        def wrapper(request):
            # Set CORS headers for the preflight request
            if request.method == "OPTIONS":
                response_headers = {
                    "Access-Control-Allow-Origin": origin,
                    "Access-Control-Allow-Methods": ",".join(methods),
                    "Access-Control-Allow-Headers": ",".join(headers),
                    "Access-Control-Max-Age": "3600",  # Cache preflight for 1 hour
                }
                return ("", 204, response_headers)  # 204 No Content for OPTIONS

            # Set CORS headers for the actual request
            # This is important even for non-OPTIONS requests to allow the browser
            # to process the response.
            response = f(request)
            if isinstance(response, tuple) and len(response) == 3:
                data, status_code, current_headers = response
                current_headers["Access-Control-Allow-Origin"] = origin
                return (data, status_code, current_headers)
            elif isinstance(response, tuple) and len(response) == 2:
                data, status_code = response
                return (data, status_code, {"Access-Control-Allow-Origin": origin})
            else:
                response.headers["Access-Control-Allow-Origin"] = origin
                return response

        return wrapper

    return decorator

def get_user(request):
    """
    Middleware to extract user information from the Authorization header.
    This function assumes the header is in the format "Bearer <id_token>".
    It verifies the token and returns the user information.
    If the token is missing or invalid, it returns an error response.
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise ValueError("Missing or invalid Authorization header")
    id_token = auth_header.split("Bearer ")[1].strip()
    user = auth.verify_id_token(id_token)
    _, project_id = default()
    if user.get("iss") != f"https://securetoken.google.com/{project_id}":
        raise ValueError(f"Invalid token issuer - not {project_id} project")
    return user

firebase_admin.initialize_app()


@cors_headers(origin="*", headers=["Content-Type", "Authorization"])
@functions_framework.http
def dispatch(request):

    # Allow preflight requests (no authentication required)
    if request.method == "OPTIONS":
        return "OK", 200

    if request.method != "POST":
        return "Method Not Allowed", 405

    try:
        # Get user information from the request's Authorization header
        user = get_user(request)
    except ValueError:
        return "Unauthorized", 401
    
    data = request.get_json()
    if "action" not in data:
        return "Bad Request: 'action' field is required", 400


    _, project_id = default()
    publisher = pubsub_v1.PublisherClient()
    # TODO: move topic name to an environment variable
    topic_path = publisher.topic_path(project_id, "homelab")

    source_ip = request.headers.get("X-Forwarded-For", request.remote_addr)
    # standardized payload structure
    payload = {
        "source_ip": source_ip,
        "user": {
            "email": user.get("email", ""),
            "uid": user["uid"],
            "display_name": user.get("name", ""),
        },
        "action": data.get("action"),
        "params": data.get("params", {}),
    }
    publisher.publish(topic_path, json.dumps(payload).encode("utf-8"))
    return f"Payload {payload} has been sent for processing", 200