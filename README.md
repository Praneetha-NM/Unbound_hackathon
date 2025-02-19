# Unbound Hackathon Challenge - Chat UI with Secure Backend

This project implements a lightweight chat UI integrated with a secure backend server that dynamically routes user prompts to different simulated language model providers based on regex-based policies.

# Tech Stack

Frontend: React
Backend: Flask
Database: PostgreSQL

# Milestones & Implementations

 # Milestone 1: Models Endpoint
 
Implemented a Flask endpoint (GET /models) to fetch the list of supported models stored in PostgreSQL.
The response returns a JSON array of model names.

# Milestone 2: Chat Completions Endpoint

Developed a POST /v1/chat/completions endpoint to validate the provider and model.
Implemented modular logic to return predefined static responses for each provider.

# Example:

OpenAI Response: "OpenAI: Processed your prompt with advanced language understanding."
Anthropic Response: "Anthropic: Your prompt has been interpreted with ethical AI principles."

# Milestone 3: Prompt Interference & Regex-Based Routing

Stored regex-based routing policies in PostgreSQL.
Implemented logic to check user prompts against regex rules before responding.
If a match is found, the request is redirected to the configured model.

# Example:

If a prompt contains "credit card" and was initially routed to gpt-4o, it gets redirected to gemini-alpha.

# Milestone 4: Simple Chat UI

Built a React-based chat UI with the following features:
Fetch and display available models using GET /models.
Dropdown to select provider and model.
Input field for user prompts.
Sends API request to POST /v1/chat/completions.
Displays the response in a chat format.
 
# Milestone 5: Admin Portal for Regex Policies

Developed an admin dashboard using React for managing regex rules.

# Features:

Add new regex rules.
Edit or delete existing rules.
Update routing policies in PostgreSQL in real-time.

# Milestone 6: File Upload Support in Chat Portal

Integrated Firebase for file storage.
Enabled file uploads in the chat UI.
Backend updates response to indicate successful file processing.

# Milestone 7: Special Routing for File Uploads

Added a configuration in PostgreSQL to define routing policies for file uploads.
If a file is uploaded, it is automatically routed to a specific provider/model.
