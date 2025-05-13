import anthropic
import os
import json
import uuid
import base64
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
from .models import Transaction, InitialBalance, ReceiptDetail, ReceiptItem, db

class FinancialAnalysis:
    """Base class for all financial analysis agent functions"""

    def __init__(self, user_id, api_key=None): #Initialize the basic settings of LLM services
        self.user_id = user_id
        self.api_key = "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" or os.environ.get("ANTHROPIC_API_KEY")
        self.tools = {
            "get_transactions": self.get_transactions,
            "get_balance": self.get_balance,
            "calculate_monthly_averages": self.calculate_monthly_averages,
            "get_recurring_transactions": self.get_recurring_transactions
        }

        #Initialize Anthropic client if API key is provided
        if self.api_key:
            self.client = anthropic.Anthropic(api_key=self.api_key)
            self.model = "claude-3-haiku-20240307"

    #start writing for the agent tools
    #1st tool: get_transactions
    def get_transactions(self, start_date=None, end_date=None):
        """Get filtered transactions from the database for analysis"""
        query = Transaction.query.filter_by(user_id=self.user_id)

        if start_date:
            query = query.filter(Transaction.date >= start_date)
        if end_date:
            query = query.filter(Transaction.date <= end_date)

        transactions = query.all()

        # Convert to serializable format
        return [{
            "id": t.id,
            "date": t.date,
            "description": t.description,
            "amount": t.amount,
            "type": t.type
        } for t in transactions]

    def get_balance(self):
        """Get current balance for the user"""
        initial = InitialBalance.query.filter_by(user_id=self.user_id).first()
        balance = initial.balance if initial else 0.0

        #Add all income and subtract all expenses
        transactions = Transaction.query.filter_by(user_id=self.user_id).all()
        for tx in transactions:
            if tx.type == "income":
                balance += tx.amount
            elif tx.type == "expense":
                balance -= tx.amount

        return balance

    def calculate_monthly_averages(self, months=3):
        """Calculate average monthly income and expenses"""
        today = datetime.now()
        start_date = (today - timedelta(days=30 * months)).strftime("%Y-%m-%d")

        transactions = Transaction.query.filter_by(user_id=self.user_id).filter(
            Transaction.date >= start_date).all()
        
        total_income = 0
        total_expenses = 0

        for tx in transactions:
            if tx.type == "income":
                total_income += tx.amount
            elif tx.type == "expense":
                total_expenses += tx.amount
        #calculate monthly averages
        avg_income = total_income / months
        avg_expenses = total_expenses / months

        return {"avg_monthly_income": avg_income,
                "avg_monthly_expenses": avg_expenses,
                "avg_monthly_net": avg_income - avg_expenses
                }

    def get_recurring_transactions(self, min_occurrences=2):
        """Identify recurring transactions based on description and similar amount"""
        transactions = Transaction.query.filter_by(user_id=self.user_id).all()

        #Group by description
        tx_by_desc = {}
        for tx in transactions:
            if tx.description not in tx_by_desc:
                tx_by_desc[tx.description] = []
            tx_by_desc[tx.description].append({
                "id": tx.id,
                "date": tx.date,
                "amount": tx.amount,
                "type": tx.type
            })

        # Filter to recurring transactions (appear multiple times)
        recurring = {}
        for desc, txs in tx_by_desc.items():
            if len(txs) >= min_occurrences:
                recurring[desc] = txs

        return recurring

    def _call_llm(self, prompt, max_tokens=4000, tools=None):
        """Utility method for calling Claude with proper error handling"""
        if not self.api_key:
            return {"error": "API key not configured"}

        try:
            #Format messages based on whether tools are provided
            messages = [{"role": "user", "content": prompt}]

            if tools:
                #Convert the instance methods to tool schemas for Claude
                tool_schemas = []
                for tool_name, tool_fn in tools.items():
                    # Basic schema with name and description from docstring
                    schema = {
                        "name": tool_name,
                        "description": tool_fn.__doc__ or f"Call the {tool_name} function",
                        "input_schema": {
                            "type": "object",
                            "properties": {}
                        }
                    }
                    
                    # Add specific parameters for each tool based on function name
                    if tool_name == "get_transactions":
                        schema["input_schema"]["properties"] = {
                            "start_date": {"type": "string", "description": "Start date in YYYY-MM-DD format"},
                            "end_date": {"type": "string", "description": "End date in YYYY-MM-DD format"}
                        }
                    elif tool_name == "calculate_monthly_averages":
                        schema["input_schema"]["properties"] = {
                            "months": {"type": "integer", "description": "Number of months to analyze"}
                        }
                    elif tool_name == "get_recurring_transactions":
                        schema["input_schema"]["properties"] = {
                            "min_occurrences": {"type": "integer", "description": "Minimum number of occurrences to consider recurring"}
                        }
                    
                    tool_schemas.append(schema)
                
                # Initial response from Claude
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=max_tokens,
                    messages=messages,
                    tools=tool_schemas
                )
                
                # Handle tool use if Claude wants to use a tool
                if response.stop_reason == "tool_use":
                    # Find tool_use blocks in the response
                    tool_use_blocks = [block for block in response.content if block.type == "tool_use"]
                    
                    if tool_use_blocks:
                        # Process each tool use request
                        tool_results = []
                        for tool_block in tool_use_blocks:
                            # Get the tool function
                            tool_name = tool_block.name
                            tool_fn = tools.get(tool_name)
                            
                            if tool_fn:
                                # Execute the tool with the provided input
                                try:
                                    result = tool_fn(**tool_block.input)
                                    # Format the result
                                    tool_results.append({
                                        "type": "tool_result",
                                        "tool_use_id": tool_block.id,
                                        "content": str(result)
                                    })
                                except Exception as e:
                                    # Handle tool execution error
                                    tool_results.append({
                                        "type": "tool_result",
                                        "tool_use_id": tool_block.id,
                                        "content": f"Error executing tool: {str(e)}",
                                        "is_error": True
                                    })
                        
                        # Send the tool results back to Claude to get the final response
                        if tool_results:
                            final_messages = messages + [
                                {"role": "assistant", "content": response.content},
                                {"role": "user", "content": tool_results}
                            ]
                            
                            # Get final response with the tool results
                            final_response = self.client.messages.create(
                                model=self.model,
                                max_tokens=max_tokens,
                                messages=final_messages
                            )
                            
                            # Extract text from the final response
                            text_blocks = [block.text for block in final_response.content if block.type == "text"]
                            return {"result": "\n".join(text_blocks)}
                
                # If no tool was used or if tool processing is complete, return the text content
                text_blocks = [block.text for block in response.content if block.type == "text"]
                return {"result": "\n".join(text_blocks)}
            else:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=max_tokens,
                    messages=messages
                )
                
                # Extract text from the response
                text_blocks = [block.text for block in response.content if block.type == "text"]
                return {"result": "\n".join(text_blocks)}
        except Exception as e:
            import traceback
            return {"error": str(e), "traceback": traceback.format_exc()}

    def call_tool(self, tool_name, **kwargs):
        """Utility to call a tool by name with parameters"""
        if tool_name in self.tools:
            tool_fn = self.tools(tool_name)
            return tool_fn(**kwargs) # **kwargs allows passing arguments dynamically
        return {"error": f"Tool {tool_name} not found"}

#CashFlowForecast class which inherits from FinancialAnalysis, using tools from FinancialAnalysis
class CashFlowForecast(FinancialAnalysis):
    """Service for forecasting future cash flow"""

    #generate_forecast_prompt method for the later tool to use for the LLM generated results
    def generate_forecast_prompt(self, days=30):
        """Generate a prompt for cash flow forecasting"""
        balance = self.get_balance()
        monthly_avgs = self.calculate_monthly_averages()
        recurring = self.get_recurring_transactions()

        #Convert dates to a consistent format for the prompt
        today = datetime.now()
        forecast_end = today + timedelta(days=days)

        prompt = f"""
        You are a financial analyst agent tasked with forecasting cash flow.

        Current Information:
        - Current Balance: ${balance:.2f}
        - Average Monthly Income: ${monthly_avgs['avg_monthly_income']:.2f}
        - Average Monthly Expenses: ${monthly_avgs['avg_monthly_expenses']:.2f}
        - Net Monthly Cash Flow: ${monthly_avgs['avg_monthly_net']:.2f}

        Forecasting Task:
        Forecast the cash flow for the next {days} days (until {forecast_end.strftime("%Y-%m-%d")}).

        Consider:
        1. Recurring transactions identified from historical data
        2. Expected changes in income or expenses
        3. Seasonal variations if applicable

        Generate a day-by-day forecast showing:
        - Date
        - Expected income
        - Expected expenses
        - Net daily cash flow
        - Running balance

        Then provide:
        1. A summary of total expected income over this period
        2. Total expected expenses
        3. Net cash flow
        4. Final projected balance
        5. Key insights about the forecasted period

        Use the available tools to analyze transaction history and identify patterns.
        """

        return prompt

    #
    def forecast(self, days=30):
        """Generate a cash flow forecast for the specified number of days"""
        try:
            # Generate the prompt
            prompt = self.generate_forecast_prompt(days)

            # Call Claude with tools
            forecast_tools = {
                "get_transactions": self.get_transactions,
                "get_balance": self.get_balance,
                "calculate_monthly_averages": self.calculate_monthly_averages,
                "get_recurring_transactions": self.get_recurring_transactions
            }

            # Call the LLM with the prompt and tools
            result = self._call_llm(prompt, max_tokens=4000, tools=forecast_tools)  # Increased token limit

            if "error" in result:
                return {"error": result["error"]}

            # Process the raw forecast result
            return self._process_forecast_result(result["result"], days)
        except Exception as e:
            import traceback
            return {"error": str(e), "traceback": traceback.format_exc()}

    def _process_forecast_result(self, raw_forecast, days):
        """Process the raw forecast to add structure if needed"""
        try:
            # Get current balance for reference
            current_balance = self.get_balance()

            # Get time information
            today = datetime.now()
            forecast_end = today + timedelta(days=days)
            
            return {
                "forecast_text": raw_forecast,
                "metadata": {
                    "user_id": self.user_id,
                    "forecast_start": today.strftime("%Y-%m-%d"),
                    "forecast_end": forecast_end.strftime("%Y-%m-%d"),
                    "current_balance": current_balance,
                    "forecast_days": days
                }
            }
        except Exception as e:
            import traceback
            return {
                "forecast_text": raw_forecast,
                "metadata": {
                    "error": str(e),
                    "traceback": traceback.format_exc()
                }
            }

    def forecast_periods(self):
        """Generate forecasts for 30, 90, and 180 day periods"""
        return {
            "30d": self.forecast(days=30),
            "90d": self.forecast(days=90),
            "180d": self.forecast(days=180)
        }

class ReceiptExtraction:
    """Service class for extracting data from receipt images using AI"""
    
    def __init__(self, user_id=1):
        self.user_id = user_id
        self.api_key = "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" or os.environ.get("ANTHROPIC_API_KEY")
        self.model = "claude-3-opus-20240229"
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.allowed_extensions = {'jpg', 'jpeg', 'png'}
        self.upload_folder = os.path.join('agent_app', 'static', 'image', 'receipts')
        
        # Create upload folder if it doesn't exist
        os.makedirs(self.upload_folder, exist_ok=True)
    
    def allowed_file(self, filename):
        """Check if the file has an allowed extension"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in self.allowed_extensions
    
    def extract_receipt_details(self, image_file):
        """Extract details from a receipt image using AI"""
        # Check if file is allowed
        if not image_file or not self.allowed_file(image_file.filename):
            return {"status": "error", "message": "Invalid file type. Only JPG, JPEG, and PNG files are allowed."}
        
        try:
            # Save the image file
            file_path, image_url = self._save_image(image_file)
            
            # Convert image to base64 for the AI model
            with open(file_path, "rb") as img_file:
                base64_image = base64.b64encode(img_file.read()).decode("utf-8")
            
            # Call the AI model
            ai_response = self._call_ai_model(file_path, base64_image)
            
            # Parse the JSON response
            try:
                extracted_data = json.loads(ai_response)
                
                # Provide default values for any missing required fields
                default_values = {
                    'date': datetime.now().strftime('%Y-%m-%d'),
                    'currency': 'USD',
                    'vendor_name': 'Unknown Vendor',
                    'receipt_items': [],
                    'tax': 0.0,
                    'total': 0.0
                }
                
                # Apply defaults for missing fields
                for field, default_value in default_values.items():
                    if field not in extracted_data:
                        print(f"Warning: Missing field '{field}' in AI response. Using default value.")
                        extracted_data[field] = default_value
                
                # Make sure receipt_items is a list, even if empty
                if not isinstance(extracted_data['receipt_items'], list):
                    extracted_data['receipt_items'] = []
                
                # Ensure numeric fields are numbers
                for field in ['tax', 'total']:
                    if not isinstance(extracted_data[field], (int, float)):
                        try:
                            extracted_data[field] = float(extracted_data[field])
                        except (ValueError, TypeError):
                            extracted_data[field] = 0.0
                
                # Process each receipt item to ensure it has the required fields
                for item in extracted_data['receipt_items']:
                    if 'item_name' not in item:
                        item['item_name'] = 'Unnamed Item'
                    if 'item_cost' not in item:
                        item['item_cost'] = 0.0
                    elif not isinstance(item['item_cost'], (int, float)):
                        try:
                            item['item_cost'] = float(item['item_cost'])
                        except (ValueError, TypeError):
                            item['item_cost'] = 0.0
                
                # Save to database
                receipt = ReceiptDetail(
                    user_id=self.user_id,
                    date=extracted_data['date'],
                    currency=extracted_data['currency'],
                    vendor_name=extracted_data['vendor_name'],
                    tax=extracted_data['tax'],
                    total=extracted_data['total'],
                    image_url=image_url
                )
                
                db.session.add(receipt)
                db.session.flush()  # To get the receipt ID before committing
                
                # Add receipt items
                for item_data in extracted_data['receipt_items']:
                    item = ReceiptItem(
                        receipt_id=receipt.id,
                        item_name=item_data['item_name'],
                        item_cost=item_data['item_cost']
                    )
                    db.session.add(item)
                
                db.session.commit()
                
                # Return the saved receipt data
                return {
                    "status": "success",
                    "data": receipt.to_dict()
                }
                
            except json.JSONDecodeError:
                return {"status": "error", "message": "Invalid JSON response from AI model"}
            
        except Exception as e:
            db.session.rollback()
            return {"status": "error", "message": f"Error processing receipt: {str(e)}"}

    # Add this method to your ReceiptExtraction class in services.py
    def _save_image(self, image_file):
        """Save the image file and return the paths"""
        filename = secure_filename(f"{uuid.uuid4()}_{image_file.filename}")
        file_path = os.path.join(self.upload_folder, filename)
        image_file.save(file_path)
        image_url = f"/static/image/receipts/{filename}"
        return file_path, image_url

    # Add this method to your ReceiptExtraction class in services.py
    def _call_ai_model(self, file_path, base64_image):
        """Call the AI model with the image"""
        # Create prompt for AI extraction
        prompt = """
        You are an expert receipt scanner. I'll provide you with an image of a receipt.
        Extract and return ONLY the following information in valid JSON format:
        
        1. Date (in YYYY-MM-DD format)
        2. Currency (3-character currency code like USD, CAD, EUR)
        3. Vendor name (company/store name)
        4. Receipt items (array of objects with item_name and item_cost as a number)
        5. GST/tax amount (for the entire receipt, as a number) - This MUST be returned as "tax" in your JSON
        6. Total amount (as a number)
        
        If any information is not visible or unclear, provide a reasonable default value.
        If you can't determine the currency, use "USD".
        If tax/GST is not visible, set it to 0.
        
        Your response MUST be in this exact format:
        
        {
            "date": "YYYY-MM-DD",
            "currency": "USD",
            "vendor_name": "Store Name",
            "receipt_items": [
                {
                    "item_name": "Item 1",
                    "item_cost": 11.11
                },
                {
                    "item_name": "Item 2",
                    "item_cost": 22.22
                }
            ],
            "tax": 12.34,
            "total": 567.89
        }
        
        Return ONLY the extracted JSON data without any explanation or additional text.
        """
        
        # Call Claude Vision API
        response = self.client.messages.create(
            model=self.model,
            max_tokens=4000,
            temperature=0,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": base64_image
                            }
                        }
                    ]
                }
            ]
        )
        
        # Extract content from the response
        return response.content[0].text