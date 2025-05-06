from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from .src.models import db
import os


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.abspath('agent_app/instance/cash_flow.db')

#Initialize database
db.init_app(app)

#Register blueprints
from .src.routes import cashflow_bp
app.register_blueprint(cashflow_bp)