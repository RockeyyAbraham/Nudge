from flask import Blueprint, request, jsonify
import sys
import os

# Import the supabase client from app.py as requested, with robust fallbacks
try:
    # Ensure backend directory is in the path
    backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    if backend_path not in sys.path:
        sys.path.insert(0, backend_path)
    from app import supabase
except ImportError:
    try:
        from nudge import supabase
    except ImportError:
        # Fallback inline initialization if nudge/app are not loaded or defined in sys.path
        from supabase import create_client, Client
        from dotenv import load_dotenv
        load_dotenv()
        supabase_url = os.environ.get("SUPABASE_URL")
        supabase_key = os.environ.get("SUPABASE_KEY")
        supabase: Client = create_client(supabase_url, supabase_key) if supabase_url and supabase_key else None

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/signup', methods=['POST'])
def signup():
    try:
        data = request.get_json() or {}
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return jsonify({"status": "error", "message": "Email and password are required"}), 400

        # Sign up the user in Supabase Auth
        try:
            res = supabase.auth.sign_up({
                "email": email,
                "password": password
            })
            
            # Retrieve the user ID
            if not res or not res.user:
                raise Exception("Failed to retrieve user ID from signup response.")
                
            user_id = res.user.id

            # Create standard profile record with profile_completed = False
            supabase.table("profiles").insert({
                "id": user_id,
                "profile_completed": False
            }).execute()

            return jsonify({
                "status": "success",
                "message": "User registered successfully",
                "redirect": "profilecompletion"
            }), 201

        except Exception as auth_err:
            err_msg = str(auth_err).lower()
            # Intercept standard duplicate email signup errors
            if "already registered" in err_msg or "already exists" in err_msg or "conflict" in err_msg or "409" in err_msg:
                return jsonify({
                    "status": "error",
                    "message": "Account already exists, please login"
                }), 409
            raise auth_err

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400


@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json() or {}
        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return jsonify({"status": "error", "message": "Email and password are required"}), 400

        try:
            res = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })

            if not res or not res.user or not res.session:
                raise Exception("Failed to retrieve user or session from sign in response.")

            user_id = res.user.id
            session_token = res.session.access_token

            # Check profile completion status from profiles table
            profile_res = supabase.table("profiles").select("profile_completed").eq("id", user_id).execute()
            
            profile_completed = False
            if profile_res.data and len(profile_res.data) > 0:
                profile_completed = profile_res.data[0].get("profile_completed", False)

            redirect_dest = "dashboard" if profile_completed else "profilecompletion"

            return jsonify({
                "status": "success",
                "message": "Login successful",
                "redirect": redirect_dest,
                "session_token": session_token,
                "user_id": user_id
            }), 200

        except Exception as auth_err:
            err_msg = str(auth_err).lower()
            # Distinguish user not found from wrong password
            if "not found" in err_msg or "no user" in err_msg or "no account" in err_msg or "user_not_found" in err_msg or "404" in err_msg:
                return jsonify({
                    "status": "error",
                    "message": "No account found, please sign up"
                }), 404
            elif "incorrect password" in err_msg or "invalid password" in err_msg or "wrong password" in err_msg or "invalid credentials" in err_msg or "invalid login credentials" in err_msg or "401" in err_msg:
                return jsonify({
                    "status": "error",
                    "message": "Incorrect password"
                }), 401
            raise auth_err

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400


@auth_bp.route('/logout', methods=['POST'])
def logout():
    try:
        supabase.auth.sign_out()
        return jsonify({
            "status": "success",
            "message": "Logged out successfully"
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400


@auth_bp.route('/me', methods=['GET'])
def me():
    try:
        auth_header = request.headers.get("Authorization")
        if not auth_header:
            return jsonify({
                "status": "error",
                "message": "Missing Authorization header"
            }), 401

        # Strip Bearer prefix if present
        if auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
        else:
            token = auth_header

        # Retrieve user details from Supabase using jwt token
        res = supabase.auth.get_user(token)
        if not res or not res.user:
            return jsonify({
                "status": "error",
                "message": "User not found or invalid session token"
            }), 401

        user = res.user
        return jsonify({
            "status": "success",
            "user": {
                "id": user.id,
                "email": user.email
            }
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Unauthorized: {str(e)}"
        }), 401
