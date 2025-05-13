from flask import Blueprint, render_template, request, jsonify, redirect, url_for, current_app
from .models import Transaction, db
from .services import CashFlowForecast, ReceiptExtraction

# Initialize blueprint with no URL prefix
cashflow_bp = Blueprint('cashflow', __name__, url_prefix='')

@cashflow_bp.route('/')
def index():
    """Render the homepage"""
    # Calculate total revenue (sum of all income transactions)
    total_revenue = db.session.query(db.func.sum(Transaction.amount))\
        .filter(Transaction.user_id == 1, Transaction.type == 'income')\
        .scalar() or 0.0
    
    # Calculate previous month's revenue for comparison
    from datetime import datetime, timedelta
    last_month = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
    prev_month_revenue = db.session.query(db.func.sum(Transaction.amount))\
        .filter(Transaction.user_id == 1, 
                Transaction.type == 'income',
                Transaction.date < last_month)\
        .scalar() or 0.0
    
    # Calculate percentage change
    if prev_month_revenue > 0:
        percent_change = ((total_revenue - prev_month_revenue) / prev_month_revenue) * 100
    else:
        percent_change = 0
    
    return render_template('index.html', 
                         total_revenue=total_revenue,
                         percent_change=percent_change)

# Receipt Extractor route
@cashflow_bp.route('/receipt-extractor')
def receipt_extractor():
    """Render the receipt extractor page"""
    return render_template('receipt_extractor.html')

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

# Receipt extraction endpoint
@cashflow_bp.route('/api/extract-receipt-details', methods=['POST'])
def extract_receipt_details():
    """API endpoint to extract details from a receipt image using AI"""
    # Check if the request has a file
    if 'file' not in request.files:
        return jsonify({"status": "error", "message": "No file part in the request"}), 400
    
    image_file = request.files['file']
    
    # Check if file was actually selected
    if image_file.filename == '':
        return jsonify({"status": "error", "message": "No file selected"}), 400
    
    # Process the receipt
    receipt_service = ReceiptExtraction(user_id=1)  # Hardcoded user_id for now
    result = receipt_service.extract_receipt_details(image_file)
    
    if result["status"] == "success":
        return jsonify(result), 200
    else:
        return jsonify(result), 500

