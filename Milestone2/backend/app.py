from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2
import re
import logging
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

# Set up logging
logging.basicConfig(level=logging.DEBUG)
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
        cur.execute(query, (model,))
        result = cur.fetchone()
        logger.debug(f"Validation query: {query} | Result: {result}")
        cur.close()
        return result is not None
    except psycopg2.Error as e:
        logger.error(f"Error validating provider/model: {e}")
        return False
    finally:
        conn.close()

# Function to check if prompt matches any regex pattern
def match_prompt_with_policy(model, prompt):
    conn = connect_db()
    if conn is None:
        logger.error("Database connection failed during regex match check")
        return None

    try:
        cur = conn.cursor()
        query = "SELECT regex_pattern, redirect_model FROM routing_policies WHERE model_name = %s;"
        cur.execute(query, (model,))
        policies = cur.fetchall()
        logger.debug(f"Retrieved routing policies for model {model}: {policies}")
        
        # Check each policy if the prompt matches
        for policy in policies:
            regex_pattern = policy[0]
            redirect_model = policy[1]
            if re.search(regex_pattern, prompt):
                logger.debug(f"Prompt matched regex pattern: {regex_pattern}")
                return redirect_model
        
        return None  # No match found
    except psycopg2.Error as e:
        logger.error(f"Error checking regex match: {e}")
        return None
    finally:
        conn.close()

# Function to get the provider's response
def get_provider_response(provider, model, prompt):
    provider_stubs = {
        "openai": lambda prompt: {
            "provider": "openai",
            "model": "gpt-3.5",
            "response": f"OpenAI: Processed your prompt with advanced language understanding. Response ID: openai_response_001"
        },
        "anthropic": lambda prompt: {
            "provider": "anthropic",
            "model": "claude-v1",
            "response": f"Anthropic: Your prompt has been interpreted with ethical AI principles. Response ID: anthropic_response_002"
        },
        "gemini": lambda prompt: {
            "provider": "gemini",
            "model": "gemini-alpha",
            "response": f"Gemini: Your prompt has been processed with cutting-edge AI capabilities. Response ID: gemini_response_003"
        }
    }

    logger.debug(f"Received provider: {provider}, model: {model}, prompt: {prompt}")

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
        
        # Validate provider and model
        if not validate_provider_and_model(provider, model):
            logger.warning(f"Invalid provider/model combination: {provider}/{model}")
            return jsonify({"error": "Invalid provider/model combination"}), 400
        
        # Check if prompt matches any routing policies
        redirect_model = match_prompt_with_policy(model, prompt)
        if redirect_model:
            logger.info(f"Prompt matched a regex pattern. Redirecting request to model: {redirect_model}")
            model = redirect_model  # Reroute to the new model
        
        # Get provider's response
        response = get_provider_response(provider, model, prompt)

        if response is None:
            logger.warning("No response generated")
            return jsonify({"error": "Unsupported provider/model combination"}), 400
        
        return jsonify(response)

    except Exception as e:
        logger.error(f"Error processing chat completion: {e}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    app.run(debug=True)
