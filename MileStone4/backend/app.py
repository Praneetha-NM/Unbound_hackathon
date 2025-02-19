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

# Function to get available models and providers
@app.route('/models', methods=['GET'])
def get_models():
    try:
        conn = connect_db()
        if conn is None:
            logger.error("Database connection failed during model fetch")
            return jsonify({"error": "Database connection failed"}), 500

        cur = conn.cursor()

        # Query to fetch all models from the models table
        query = """
            SELECT name FROM models;
        """
        cur.execute(query)
        models = cur.fetchall()

        if not models:
            logger.info("No models found")
            return jsonify({"error": "No models found"}), 404

        # Query to fetch models that are part of routing policies (model_name)
        rerouted_query = """
            SELECT model_name FROM routing_policies;
        """
        cur.execute(rerouted_query)
        rerouted_models = cur.fetchall()

        # Prepare the result with provider and models (name[0] for provider, name[1] for model)
        result = []

        for model in models:
            provider = model[0].split('/')[0]  # Extract provider from the name
            model_name = model[0].split('/')[1]  # Extract model from the name
            result.append({"provider": provider, "model": model_name})

        # Add rerouted models to the list
        for rerouted_model in rerouted_models:
            result.append({"model": rerouted_model[0]})

        return jsonify(result)
    
    except Exception as e:
        logger.error(f"Error fetching models: {e}")
        return jsonify({"error": "Internal server error"}), 500
    finally:
        if conn:
            conn.close()

# Function to check if prompt matches any regex pattern
def match_prompt_with_policy(model, prompt):
    conn = connect_db()
    if conn is None:
        logger.error("Database connection failed during regex match check")
        return None, None

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
            logger.debug(f"Checking prompt: {prompt} against regex pattern: {regex_pattern}")
            
            if re.search(regex_pattern, prompt):
                logger.debug(f"Prompt matched regex pattern: {regex_pattern}")
                
                # Fetch all models that match the redirect_model
                provider_query = "SELECT name FROM models;"
                cur.execute(provider_query)
                models = cur.fetchall()

                # Loop through all models and find the matching one
                for model_name in models:
                    model_name = model_name[0]
                    logger.debug(f"Checking model: {model_name}")
                    if redirect_model in model_name:
                        provider = model_name.split("/")[0]  # Extract provider from model name
                        logger.debug(f"Redirecting to model: {redirect_model} with provider: {provider}")
                        return redirect_model, provider  # Return redirect model and its provider
                        
        logger.debug("No matching routing policy found.")
        return None, None  # No match found
    except psycopg2.Error as e:
        logger.error(f"Error checking regex match: {e}")
        return None, None
    finally:
        conn.close()

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

# Function to get provider's response
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
        
        # Check if prompt matches any routing policies
        redirect_model, redirect_provider = match_prompt_with_policy(model, prompt)
        
        if redirect_model:
            logger.info(f"Prompt matched a regex pattern. Redirecting request to model: {redirect_model}")
            model = redirect_model  # Reroute to the new model
            provider = redirect_provider
            
        # Now validate the provider and model after rerouting
        if not validate_provider_and_model(provider, model):
            logger.warning(f"Invalid provider/model combination: {provider}/{model}")
            return jsonify({"error": "Invalid provider/model combination"}), 400
        
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
    app.run(debug=True, port=5003)
