from dotenv import load_dotenv
import os

# Get the absolute path of the current directory
base_dir = os.path.abspath(os.path.dirname(__file__))
# Load environment variables from .env file in the base directory
load_dotenv(os.path.join(base_dir, '.env'))

# Make sure environment has necessary variables
api_key = os.environ.get("ANTHROPIC_API_KEY")
if api_key:
    print(f"API key loaded successfully. Length: {len(api_key)}")
    print(f"First 5 characters: {api_key[:5]}...")
else:
    print("Warning: ANTHROPIC_API_KEY not found in environment variables.")
    print("AI features may not work correctly. Make sure to set up your .env file.")

from agent_app import app

if __name__ == "__main__":
    app.run(debug=True, port=5001)