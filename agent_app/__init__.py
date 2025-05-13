from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from .src.models import db
import os

def create_app(test_config=None):
    """Create and configure the Flask application instance"""
    app = Flask(__name__)
    
    if test_config is None:
        # Load production config
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.abspath('agent_app/instance/cash_flow.db')
    else:
        # Load test config
        app.config.update(test_config)
    
    # Initialize database
    db.init_app(app)
    
    # Initialize migration
    migrate = Migrate(app, db)
    
    # Register blueprints
    from .src.routes import cashflow_bp
    app.register_blueprint(cashflow_bp)
    
    return app

# Create an application instance for production
app = create_app()