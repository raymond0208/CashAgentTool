from flask import Blueprint, render_template, request, jsonify, redirect, url_for, current_app
from .models import Transaction, db
from .services import CashFlowForecast

# Initialize blueprint with no URL prefix
cashflow_bp = Blueprint('cashflow', __name__, url_prefix='')

@cashflow_bp.route('/')
def index():
    """Render the homepage"""
    return render_template('index.html')

# Cash Flow Forecast routes
@cashflow_bp.route('/forecast', methods=['GET'])
def forecast_view():
    """Render the cash flow forecast UI"""
    return render_template('forecast.html')

@cashflow_bp.route('/api/forecast/<int:days>', methods=['GET'])
def generate_forecast(days):
    """API endpoint to generate a cash flow forecast for specified days"""
    # Validate days parameter
    if days not in [30, 90, 180]:
        return jsonify({"error": "Days parameter must be 30, 90, or 180"}), 400
        
    # Use a hardcoded user_id instead of current_user
    forecast_service = CashFlowForecast(user_id=1)
    
    # Generate forecast
    result = forecast_service.forecast(days=days)
    
    return jsonify(result)

@cashflow_bp.route('/api/forecast/all', methods=['GET'])
def generate_all_forecasts():
    """API endpoint to generate forecasts for 30, 90, and 180 days"""
    # Use a hardcoded user_id
    forecast_service = CashFlowForecast(user_id=1)
    
    # Generate all forecasts
    results = forecast_service.forecast_periods()
    
    return jsonify(results)

@cashflow_bp.route('/transactions')
def transactions():
    """Render the transactions page"""
    # Use a hardcoded user_id
    transactions = Transaction.query.filter_by(user_id=1).order_by(Transaction.date.desc()).all()
    return render_template('transactions.html', transactions=transactions)

# Simple test route
@cashflow_bp.route('/test')
def test():
    """Simple test route to verify routing is working"""
    return "Routing is working! This is a test page."

# Debug route to list all routes
@cashflow_bp.route('/debug-routes')
def debug_routes():
    """Debug endpoint to list all registered routes"""
    routes = []
    for rule in current_app.url_map.iter_rules():
        routes.append({
            'endpoint': rule.endpoint,
            'methods': list(rule.methods),
            'route': str(rule)
        })
    return jsonify(routes)

