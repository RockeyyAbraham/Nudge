import os

from dotenv import load_dotenv
from flask import Blueprint, jsonify, request
from supabase import Client, create_client

env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '.env'))
load_dotenv(env_path)

supabase_url = os.environ.get("SUPABASE_URL")
# Use SUPABASE_ANON_KEY as primary, fallback to SUPABASE_KEY
supabase_key = os.environ.get("SUPABASE_ANON_KEY") or os.environ.get("SUPABASE_KEY")

try:
    if supabase_url and supabase_key:
        supabase: Client = create_client(supabase_url, supabase_key)
        print("INFO: auth.py public client initialized successfully.")
    else:
        supabase = None
        print("WARNING: auth.py public client could not be initialized (missing config).")
except Exception as e:
    supabase = None
    print(f"ERROR: Failed to initialize auth.py public client: {e}")

auth_bp = Blueprint('auth', __name__)


def _auth_payload(response):
    user = getattr(response, "user", None)
    session = getattr(response, "session", None)

    if isinstance(response, dict):
        user = response.get("user")
        session = response.get("session")

    return user, session


def _value(obj, key, default=None):
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


def _session_token(session):
    return _value(session, "access_token")


def _json_error(message, status_code):
    return jsonify({"status": "error", "message": message}), status_code


def _safe_error_message(error):
    """Map unexpected/internal errors (DNS failures, timeouts, connection
    drops talking to Supabase) to a friendly message instead of leaking the
    raw exception text (e.g. "[Errno 11001] getaddrinfo failed") to the UI."""
    error_text = str(error).lower()
    network_markers = (
        "getaddrinfo failed",
        "errno 11001",
        "name or service not known",
        "connection refused",
        "connectionerror",
        "timed out",
        "timeout",
        "max retries exceeded",
        "network is unreachable",
    )
    if any(marker in error_text for marker in network_markers):
        print(f"ERROR: network failure talking to Supabase: {error}")
        return "Couldn't reach the server. Check your internet connection and try again."

    return str(error)


def _require_supabase():
    if not supabase:
        return _json_error("Supabase is not configured", 500)
    return None


def _is_duplicate_signup_error(error_message):
    duplicate_markers = [
        "already registered",
        "already exists",
        "user already registered",
        "email_exists",
        "conflict",
        "409",
    ]
    return any(marker in error_message for marker in duplicate_markers)


def _signup_response_is_existing_account(response):
    user, _ = _auth_payload(response)
    identities = _value(user, "identities")
    return isinstance(identities, list) and len(identities) == 0


def _service_supabase():
    supabase_url = os.environ.get("SUPABASE_URL")
    service_key = (
        os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        or os.environ.get("SUPABASE_SERVICE_KEY")
    )

    if not supabase_url or not service_key:
        return None

    return create_client(supabase_url, service_key)


def _email_exists(email):
    service_client = _service_supabase()
    if not service_client:
        return None

    try:
        page = 1
        per_page = 1000
        while True:
            users_response = service_client.auth.admin.list_users({
                "page": page,
                "per_page": per_page,
            })
            users = getattr(users_response, "users", None) or []

            for user in users:
                if (_value(user, "email") or "").lower() == email.lower():
                    return True

            if len(users) < per_page:
                return False

            page += 1
    except Exception:
        return None


@auth_bp.route('/signup', methods=['POST'])
def signup():
    try:
        config_error = _require_supabase()
        if config_error:
            return config_error

        data = request.get_json() or {}
        email = (data.get("email") or "").strip()
        password = data.get("password")

        if not email or not password:
            return _json_error("Email and password are required", 400)

        try:
            response = supabase.auth.sign_up({
                "email": email,
                "password": password,
            })

            if _signup_response_is_existing_account(response):
                return _json_error("Account already exists, please login", 409)

            return jsonify({
                "status": "success",
                "message": "OTP sent to your email",
            }), 201
        except Exception as auth_error:
            error_message = str(auth_error).lower()
            if _is_duplicate_signup_error(error_message):
                return _json_error("Account already exists, please login", 409)
            raise auth_error
    except Exception as error:
        return _json_error(_safe_error_message(error), 400)


@auth_bp.route('/verify-otp', methods=['POST'])
def verify_otp():
    try:
        config_error = _require_supabase()
        if config_error:
            return config_error

        data = request.get_json() or {}
        email = (data.get("email") or "").strip()
        token = (data.get("token") or data.get("otp") or "").strip()

        if not email or not token:
            return _json_error("Email and OTP are required", 400)

        response = supabase.auth.verify_otp({
            "email": email,
            "token": token,
            "type": "signup",
        })
        user, session = _auth_payload(response)

        if not user:
            return _json_error("Invalid or expired OTP", 401)

        user_id = _value(user, "id")
        session_token = _session_token(session)

        service_client = _service_supabase()
        client_to_use = service_client if service_client else supabase
        try:
            client_to_use.table("profiles").insert({
                "id": user_id,
                "profile_completed": False,
            }).execute()
        except Exception as profile_err:
            # If the database trigger already inserted the profile, we ignore the duplicate error
            err_msg = str(profile_err).lower()
            if "duplicate" not in err_msg and "already exists" not in err_msg and "23505" not in err_msg:
                raise profile_err

        return jsonify({
            "status": "success",
            "message": "OTP verified successfully",
            "redirect": "profilecompletion",
            "session_token": session_token,
            "user_id": user_id,
        }), 200
    except Exception as error:
        error_message = str(error).lower()
        if "duplicate" in error_message or "already exists" in error_message or "23505" in error_message:
            return _json_error("Profile already exists", 409)
        return _json_error(_safe_error_message(error), 400)


@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        config_error = _require_supabase()
        if config_error:
            return config_error

        data = request.get_json() or {}
        email = (data.get("email") or "").strip()
        password = data.get("password")

        if not email or not password:
            return _json_error("Email and password are required", 400)

        try:
            response = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password,
            })
        except Exception as auth_error:
            error_message = str(auth_error).lower()
            if "email not confirmed" in error_message or "email_not_confirmed" in error_message:
                return _json_error("Email not confirmed. Please verify your email with the OTP first.", 401)

            if (
                "invalid login credentials" in error_message
                or "invalid credentials" in error_message
                or "401" in error_message
            ):
                email_exists = _email_exists(email)
                if email_exists is False:
                    return _json_error("No account found, please sign up", 404)
                return _json_error("Incorrect password", 401)

            if "not found" in error_message or "user_not_found" in error_message or "404" in error_message:
                return _json_error("No account found, please sign up", 404)

            raise auth_error

        user, session = _auth_payload(response)

        if not user or not session:
            return _json_error("Incorrect password", 401)

        user_id = _value(user, "id")
        session_token = _session_token(session)

        profile_response = (
            supabase.table("profiles")
            .select("profile_completed")
            .eq("id", user_id)
            .execute()
        )
        profile_data = getattr(profile_response, "data", None) or []
        profile_completed = False

        if profile_data:
            profile_completed = bool(profile_data[0].get("profile_completed", False))

        redirect = "dashboard" if profile_completed else "profilecompletion"

        return jsonify({
            "status": "success",
            "message": "Login successful",
            "redirect": redirect,
            "session_token": session_token,
            "user_id": user_id,
        }), 200
    except Exception as error:
        return _json_error(_safe_error_message(error), 400)


@auth_bp.route('/logout', methods=['POST'])
def logout():
    try:
        config_error = _require_supabase()
        if config_error:
            return config_error

        supabase.auth.sign_out()
        return jsonify({
            "status": "success",
            "message": "Logged out successfully",
        }), 200
    except Exception as error:
        return _json_error(_safe_error_message(error), 400)


@auth_bp.route('/me', methods=['GET'])
def me():
    try:
        config_error = _require_supabase()
        if config_error:
            return config_error

        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return _json_error("Missing Authorization header", 401)

        token = auth_header.removeprefix("Bearer ").strip()
        if not token:
            return _json_error("Missing session token", 401)

        response = supabase.auth.get_user(token)
        user = getattr(response, "user", None)

        if not user:
            return _json_error("Invalid session token", 401)

        user_id = _value(user, "id")

        service_client = _service_supabase()
        client_to_use = service_client if service_client else supabase
        profile_response = (
            client_to_use.table("profiles")
            .select("full_name, university, semester, profile_completed")
            .eq("id", user_id)
            .execute()
        )
        profile_data = getattr(profile_response, "data", None) or []
        profile = profile_data[0] if profile_data else {}

        return jsonify({
            "status": "success",
            "user": {
                "id": user_id,
                "email": _value(user, "email"),
            },
            "profile": {
                "full_name": profile.get("full_name"),
                "university": profile.get("university"),
                "semester": profile.get("semester"),
                "profile_completed": bool(profile.get("profile_completed", False)),
            },
        }), 200
    except Exception as error:
        return _json_error(f"Unauthorized: {str(error)}", 401)


@auth_bp.route('/complete-profile', methods=['POST'])
def complete_profile():
    try:
        config_error = _require_supabase()
        if config_error:
            return config_error

        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return _json_error("Missing Authorization header", 401)

        token = auth_header.removeprefix("Bearer ").strip()
        if not token:
            return _json_error("Missing session token", 401)

        response = supabase.auth.get_user(token)
        user = getattr(response, "user", None)

        if not user:
            return _json_error("Invalid session token", 401)

        user_id = _value(user, "id")

        data = request.get_json() or {}
        full_name = data.get("full_name", "").strip()
        university = data.get("university", "").strip()

        # Parse semester as int or leave as null if not specified/invalid
        semester_val = data.get("semester")
        try:
            semester = int(semester_val) if semester_val is not None else None
        except ValueError:
            semester = None

        service_client = _service_supabase()
        client_to_use = service_client if service_client else supabase

        # Update the profiles table
        client_to_use.table("profiles").update({
            "full_name": full_name,
            "university": university,
            "semester": semester,
            "profile_completed": True
        }).eq("id", user_id).execute()

        return jsonify({
            "status": "success",
            "message": "Profile completed successfully"
        }), 200
    except Exception as error:
        return _json_error(_safe_error_message(error), 400)
