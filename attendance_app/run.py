"""Application entry point."""
import os
from app import create_app

# Create application instance
config_name = os.environ.get('FLASK_ENV', 'development')
app = create_app(config_name)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = config_name != 'production'
    app.run(host='0.0.0.0', port=5001, debug=debug)
