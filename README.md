# Unbound Hackathon Challenge - Chat UI with Secure Backend

This project implements a lightweight chat UI integrated with a secure backend server that dynamically routes user prompts to different simulated language model providers based on regex-based policies.

# Demo Video Link :

https://www.loom.com/share/c791cd75d6c74b92883801c4f7732a0c?sid=5fc08f7d-5b3f-48d4-9541-42e6021543a4

# Tech Stack

Frontend: React

Backend: Flask

Database: PostgreSQL

# Setup Instructions

# Prerequisites

Ensure you have the following installed:

Python 3.x
Node.js & npm
PostgreSQL
pip (Python package manager)
Backend Setup (Flask)

# Clone the repository:

git clone https://github.com/Praneetha-NM/Unbound_hackathon.git
cd Unbound_hackathon/backend

# Create a virtual environment:

python -m venv venv
source venv/bin/activate  # For macOS/Linux
venv\Scripts\activate  # For Windows

# Install dependencies:

pip install -r requirements.txt

# Configure database in .env:

DATABASE_URL=postgresql://username:password@localhost:5432/unbound_db

# Frontend Setup (React)

# Navigate to the frontend directory:
 
cd ../frontend
 
# Install dependencies:

npm install  
npm install axios react-router-dom react-do  

# Start the React development server:

npm start  

# Usage Details

1. Fetching Available Models
API: GET /models
Displays supported models in the chat UI.

2. Sending a Chat Prompt
API: POST /v1/chat/completions
Routes the request to the appropriate provider.
Applies regex rules before finalizing the model.

3. Admin Panel for Regex Rules
Admins can add, edit, delete regex routing rules.
Updates stored policies in the database.

4. File Upload & Special Routing
Users can upload PDFs.
Backend determines the provider for file processing based on admin settings.


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
