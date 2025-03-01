from flask import Flask
from flask_session import Session
from routes import bp
from utils import MAX_CONTENT_LENGTH, create_directories
import os
import secrets
import tempfile

# Create Flask application
app = Flask(__name__)

# Create necessary directories
create_directories()

# Configure file upload settings
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH  # 16MB max upload size

# Configure session
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or secrets.token_hex(16)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_FILE_DIR'] = os.path.join(tempfile.gettempdir(), 'flask_session')
Session(app)

# Register blueprint
app.register_blueprint(bp)

if __name__ == '__main__':
    app.run(debug=True, port=5003)
