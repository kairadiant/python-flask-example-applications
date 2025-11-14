import os
import json
from flask import Flask, session, redirect, render_template, request, url_for, jsonify
import workos

# --- FIX FOR APIError IMPORT ISSUE ---
# We use a try/except block because the location of APIError changes across WorkOS SDK versions.
try:
    # Attempt 1: Check the new location (top-level workos)
    from workos import APIError 
except ImportError:
    try:
        # Attempt 2: Check the legacy location (workos.exceptions)
        from workos.exceptions import APIError
    except ImportError:
        # Fallback: Create a placeholder class if the import still fails. 
        # This prevents the app from crashing on startup, though API calls will still fail later.
        class APIError(Exception):
            def __init__(self, message="WorkOS SDK APIError class could not be imported."):
                self.message = message
# --- END FIX ---


# Flask Setup
app = Flask(__name__)
app.secret_key = os.getenv("APP_SECRET_KEY")
base_api_url = os.getenv("WORKOS_BASE_API_URL")

# WorkOS Setup
# NOTE: WORKOS_API_KEY and WORKOS_CLIENT_ID must be set in your environment variables.
workos_client = workos.WorkOSClient(
    api_key=os.getenv("WORKOS_API_KEY"),
    client_id=os.getenv("WORKOS_CLIENT_ID"),
    base_url=base_api_url,
)

# --- Configuration ---
# SSO Connection ID for the SAML flow
CUSTOMER_CONNECTION_ID = "conn_01KA0AJA6PH9WJ712ZT343351V"

# Directory ID for Directory Sync API calls (REQUIRED to list users/groups)
CUSTOMER_DIRECTORY_ID = "directory_01KA0TMS6SBQT60XMRGFG9367V"


# Helper function for pretty JSON printing in templates
def to_pretty_json(value):
    """
    Converts a Python value (including Pydantic models used by WorkOS) into a 
    pretty-printed JSON string.
    """
    # Check if the object has a model_dump method (Pydantic models)
    if hasattr(value, 'model_dump'):
        # Convert the Pydantic model to a standard dictionary for JSON serialization
        value = value.model_dump()
    # Also handle legacy .dict() method if model_dump isn't available
    elif hasattr(value, 'dict'):
        value = value.dict()
        
    return json.dumps(value, sort_keys=True, indent=4)


app.jinja_env.filters["tojson_pretty"] = to_pretty_json


@app.route("/")
def login():
    # Safely check if essential session variables exist before rendering success page.
    if session.get("first_name") and session.get("raw_profile"):
        try:
            return render_template(
                "login_successful.html",
                first_name=session["first_name"],
                raw_profile=session["raw_profile"],
            )
        except Exception:
            # Fallback for rendering errors
            return render_template("login.html")
    else:
        # Show the login form.
        return render_template("login.html")

@app.route("/auth", methods=["POST"])
def auth():

    login_type = request.form.get("login_method")
    if login_type not in (
        "saml",
        "GoogleOAuth",
        "MicrosoftOAuth",
    ):
        return redirect("/")

    redirect_uri = url_for("auth_callback", _external=True)

    if login_type == "saml":
        authorization_url = workos_client.sso.get_authorization_url(
            redirect_uri=redirect_uri, 
            connection_id=CUSTOMER_CONNECTION_ID 
        )
    else:
        authorization_url = workos_client.sso.get_authorization_url(
            redirect_uri=redirect_uri, 
            provider=login_type
        )

    return redirect(authorization_url)


@app.route("/auth/callback")
def auth_callback():

    code = request.args.get("code")
    if code is None:
        return redirect("/")
    
    # Retrieves profile and token based on the authorization code
    profile_and_token = workos_client.sso.get_profile_and_token(code)
    
    profile = profile_and_token.profile
    # Use .dict() for consistency in serializing to a standard dictionary
    session["first_name"] = profile.first_name
    session["raw_profile"] = profile.dict() 
    session["session_id"] = profile.id
    return redirect("/")


@app.route("/logout")
def logout():
    session.clear()
    session["raw_profile"] = ""
    return redirect("/")


# --- DIRECTORY SYNC ROUTES (Data Fetching via API) ---

@app.route("/users")
def users():
    """Lists users from the configured directory using the WorkOS API."""
    if not CUSTOMER_DIRECTORY_ID:
        # Uses the custom error template for config issues
        return render_template("dsync_error.html", message="CUSTOMER_DIRECTORY_ID is not configured.")

    try:
        # Use directory_id to list the synced users
        response = workos_client.directory_sync.list_users(
            directory_id=CUSTOMER_DIRECTORY_ID,
            limit=50,
        )
        return render_template(
            "users.html", 
            directory_users=response.data, 
            directory_id=CUSTOMER_DIRECTORY_ID
        )
    except APIError as e:
        print(f"WorkOS API Error listing DSync users: {e.message}")
        return render_template("dsync_error.html", message=f"WorkOS API Error: {e.message}")
    except Exception as e:
        print(f"Unexpected error listing DSync users: {e}")
        return render_template("dsync_error.html", message=f"Error retrieving users: {e}")


@app.route("/groups")
def groups():
    """Lists groups from the configured directory using the WorkOS API."""
    if not CUSTOMER_DIRECTORY_ID:
        return render_template("dsync_error.html", message="CUSTOMER_DIRECTORY_ID is not configured.")

    try:
        # Use directory_id to list the synced groups
        response = workos_client.directory_sync.list_groups(
            directory_id=CUSTOMER_DIRECTORY_ID,
            limit=50,
        )
        return render_template(
            "groups.html", 
            directory_groups=response.data, 
            directory_id=CUSTOMER_DIRECTORY_ID
        )
    except APIError as e:
        print(f"WorkOS API Error listing DSync groups: {e.message}")
        return render_template("dsync_error.html", message=f"WorkOS API Error: {e.message}")
    except Exception as e:
        print(f"Unexpected error listing DSync groups: {e}")
        return render_template("dsync_error.html", message=f"Error retrieving groups: {e}")


@app.route("/webhooks/workos", methods=["POST"])
def workos_webhook():
    """
    Receives webhooks from WorkOS.
    NOTE: Signature verification is omitted, as this route is assumed to be 
    non-functional in a purely local setup, matching the simplified example.
    """
    payload = request.data.decode("utf-8")
    signature = request.headers.get("Workos-Signature")
    
    # We are not verifying the signature, but we check for the header presence
    if not signature:
        print("Webhook received without signature. Ignoring payload.")
        return "Success (No Signature)", 200

    try:
        # Manually decode and log the event data
        event = json.loads(payload)
        
        print(f"--- Received Webhook Event: {event['event']} ---")
        
        # Log event details to console
        if event['event'].startswith("dsync.user."):
            print(f"DSync User Event ({event['event']}): User ID {event['data'].get('id')}")
        elif event['event'].startswith("dsync.group."):
            print(f"DSync Group Event ({event['event']}): Group ID {event['data'].get('id')}")
        else:
            print(f"Unhandled Event Type: {event['event']}")
            
        return "Success", 200

    except Exception as e:
        print(f"An unexpected error occurred during webhook processing: {e}")
        return "Internal Error", 500


if __name__ == "__main__":
    app.run(port=5000, debug=True)