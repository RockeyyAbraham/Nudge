import os
from flask import Flask, render_template, send_from_directory
from flask_cors import CORS
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables from backend/.env
env_path = os.path.join(os.path.dirname(__file__), '.env')
load_dotenv(env_path)

# Initialize Supabase client
supabase_url= os.environ.get("SUPABASE_URL")
# Use SUPABASE_ANON_KEY as primary, fallback to SUPABASE_KEY
supabase_key = os.environ.get("SUPABASE_ANON_KEY") or os.environ.get("SUPABASE_KEY")

if not supabase_url:
    print("WARNING: SUPABASE_URL environment variable is missing.")
if not supabase_key:
    print("WARNING: SUPABASE_ANON_KEY (or SUPABASE_KEY) environment variable is missing.")

try:
    if supabase_url and supabase_key:
        supabase: Client = create_client(supabase_url, supabase_key)
        print("INFO: Supabase public client initialized successfully.")
    else:
        supabase = None
        print("WARNING: Supabase public client could not be initialized (missing config).")
except Exception as e:
    supabase = None
    print(f"ERROR: Failed to initialize Supabase public client: {e}")

# Initialize Supabase service role client for logging/audit
service_key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") or os.environ.get("SUPABASE_SERVICE_KEY")
try:
    if supabase_url and service_key:
        service_client = create_client(supabase_url, service_key)
        print("INFO: Supabase service client initialized successfully.")
    else:
        print("WARNING: Supabase service client could not be initialized (missing service key).")
except Exception as e:
    print(f"ERROR: Failed to initialize Supabase service client: {e}")

# Define template and static files folder location
# The templates folder is located in the root directory (one level up from backend/)
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
template_dir = os.path.join(base_dir, 'templates')

app = Flask(
    __name__,
    template_folder=template_dir,
    static_folder=template_dir,
    static_url_path=''
)

# Enable CORS for all routes
CORS(app)

# Set Flask secret key
app.secret_key = os.environ.get("FLASK_SECRET_KEY")

# Register the Blueprint from routes/auth.py
from routes.auth import auth_bp
app.register_blueprint(auth_bp, url_prefix='/api/auth')

# Serve templates
@app.route('/')
def home():
    return render_template('home.html')

# Catch-all route to serve static files from templates folder
@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(template_dir, path)

if __name__ == '__main__':
    # Run on port 5000 in debug mode
    app.run(port=5000, debug=True)
