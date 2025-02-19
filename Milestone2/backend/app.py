from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2
import logging
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

# Set up logging
logging.basicConfig(level=logging.DEBUG)  # DEBUG logs
logger = logging.getLogger(__name__)

# Database connection
def connect_db():
    try:
        logger.debug("Attempting to connect to the database...")
        return psycopg2.connect(Config.SQLALCHEMY_DATABASE_URI)
    except psycopg2.Error as e:
        logger.error(f"Database connection error: {e}")
        return None

# Function to validate the provider and model
def validate_provider_and_model(provider, model):
    conn = connect_db()
    if conn is None:
        logger.error("Database connection failed during validation")
        return False

    try:
        cur = conn.cursor()
        query = "SELECT name FROM models WHERE name = %s;"
        cur.execute(query, (f"{provider}/{model}",))
        result = cur.fetchone()
        logger.debug(f"Validation query: {query} | Result: {result}")
        cur.close()
        return result is not None
    except psycopg2.Error as e:
        logger.error(f"Error validating provider/model: {e}")
        return False
    finally:
        conn.close()

# Response generation logic for different providers
def get_provider_response(provider, model, prompt):
    provider_stubs = {
        "openai": lambda prompt: {
            "provider": "openai",
            "model": "gpt-3.5",
            "response": f"OpenAI: Processed your prompt with advanced language understanding."
        },
        "anthropic": lambda prompt: {
            "provider": "anthropic",
            "model": "claude-v1",
            "response": f"Anthropic: Your prompt has been interpreted with ethical AI principles."
        },
        "gemini": lambda prompt: {
            "provider": "gemini",
            "model": "gemini-alpha",
            "response": f"Gemini: Your prompt has been processed with cutting-edge AI capabilities."
        }
    }

    if provider in provider_stubs:
        response = provider_stubs[provider](prompt)
        logger.debug(f"Generated response: {response}")
        return response
    else:
        logger.error(f"Unsupported provider/model combination: {provider}/{model}")
        return None

@app.route('/v1/chat/completions', methods=['POST'])
def chat_completions():
    try:
        # Parse the JSON request body
        data = request.get_json()
        provider = data.get("provider")
        model = data.get("model")
        prompt = data.get("prompt")

        # Log the incoming request
        logger.debug(f"Request received: provider={provider}, model={model}, prompt={prompt}")

        # Validate input parameters
        if not provider or not model or not prompt:
            logger.warning("Missing required parameters")
            return jsonify({"error": "Missing required parameters"}), 400
        
        # Validate the provider and model in the database
        if not validate_provider_and_model(provider, model):
            logger.warning(f"Invalid provider/model combination: {provider}/{model}")
            return jsonify({"error": "Invalid provider/model combination"}), 400
        
        # Route to corresponding provider response generation
        response = get_provider_response(provider, model, prompt)

        if response is None:
            logger.warning("No response generated")
            return jsonify({"error": "Unsupported provider/model combination"}), 400
        
        return jsonify(response)

    except Exception as e:
        logger.error(f"Error processing chat completion: {e}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    app.run(debug=True,port=5001)
