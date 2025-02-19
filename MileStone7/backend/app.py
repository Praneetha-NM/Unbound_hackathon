from flask import Flask, jsonify, request
from flask_cors import CORS
import psycopg2
import re
import logging
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

remembered_provider = None
remembered_model = None
file_response=None
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
        cur = conn.cursor()
        if conn is None:
            logger.error("Database connection failed during model fetch")
            return jsonify({"error": "Database connection failed"}), 500

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
                provider_query = "SELECT name FROM models WHERE name LIKE %s;"
                cur.execute(provider_query, (f"%{redirect_model}%",))
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
        provider = request.form.get("provider")
        model = request.form.get("model")
        prompt = request.form.get("prompt")
        file = request.files.get("file") 

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
        logger.debug(f"Remembered model : {remembered_model}")
        logger.debug(f"Remembered Provider : {remembered_provider}")
        if (remembered_provider and remembered_model):
            file_response = get_provider_response(remembered_provider, remembered_model, prompt)
            response_data = {
                "response": response,
                "File Processed": bool(file),
                "File_response": file_response,
            }
        else:
            response_data = {
                "response": response,
                "File Processed": bool(file)
            }
        logger.debug(f"{response_data}")
        return jsonify(response_data)

    except Exception as e:
        logger.error(f"Error processing chat completion: {e}")
        return jsonify({"error": "Internal server error"}), 500
    
@app.route('/regex-rules', methods=['GET'])
def get_regex_rules():
    conn = connect_db()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id, model_name, regex_pattern, redirect_model FROM routing_policies;")
        rules = cursor.fetchall()
        return jsonify(rules)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# Add new regex rule (with validation)
@app.route('/regex-rules', methods=['POST'])
def add_regex_rule():
    data = request.json
    regex_pattern = data.get("pattern")
    model_name = data.get("originalModel")
    redirect_model = data.get("redirectModel")

    if not regex_pattern or not model_name or not redirect_model:
        return jsonify({"error": "All fields are required"}), 400

    # Extract model name after '/'
    redirect_name = redirect_model.split("/")[-1]  # Extract last part

    conn = connect_db()
    cursor = conn.cursor()

    try:
        # Check if redirect_model exists in models table
        cursor.execute("SELECT name FROM models")
        models= cursor.fetchall()

        # Extract the second part after '/'
        model_names = [name[0].split('/')[1] for name in models]

        if redirect_model not in model_names:
            return jsonify({"error": "Redirect model does not exist in models table"}), 400

        # Insert into routing_policies table
        cursor.execute(
            "INSERT INTO routing_policies (model_name, regex_pattern, redirect_model) VALUES (%s, %s, %s) RETURNING id;",
            (model_name, regex_pattern, redirect_model)
        )
        conn.commit()
        return jsonify({"message": "Rule added successfully", "id": cursor.fetchone()[0]})
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# Delete regex rule
@app.route('/regex-rules/<int:rule_id>', methods=['DELETE'])
def delete_regex_rule(rule_id):
    conn = connect_db()
    cursor = conn.cursor()

    try:
        cursor.execute("DELETE FROM routing_policies WHERE id = %s RETURNING id;", (rule_id,))
        deleted_rule = cursor.fetchone()

        if not deleted_rule:
            return jsonify({"error": "Rule not found"}), 404

        conn.commit()
        return jsonify({"message": "Rule deleted successfully"})
    except Exception as e:
        conn.rollback()
        return jsonify({"error": str(e)}), 500
    finally:
        cursor.close()
        conn.close()


# Endpoint to update the file upload routing model
@app.route("/file-upload-routing", methods=["POST"])
def update_file_upload_model():
    global remembered_model,remembered_provider
    data = request.get_json()
    new_model_name = data.get("model")
    conn = connect_db()
    cur = conn.cursor()
    # Validate if the model exists in the `models` table
    provider_query = "SELECT name FROM models;"
    cur.execute(provider_query)
    models = cur.fetchall()

    # Loop through all models and find the matching one
    for model_name in models:
            model_name = model_name[0]
            logger.debug(f"Checking model: {model_name}")
            if new_model_name in model_name:
                remembered_model = new_model_name
                remembered_provider = model_name.split("/")[0]
            logger.debug(f"Remembered model : {remembered_model}")
            logger.debug(f"Remembered Provider : {remembered_provider}")
    return jsonify({"message": "File upload model updated successfully!"})

if __name__ == '__main__':
    app.run(debug=True, port=5006)
