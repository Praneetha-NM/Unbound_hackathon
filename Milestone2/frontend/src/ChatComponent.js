import { useState } from "react";
import axios from "axios";
import './Chatcompletion.css'; // Assuming you have a separate CSS file

function ChatCompletion() {
  const [provider, setProvider] = useState("");
  const [model, setModel] = useState("");
  const [prompt, setPrompt] = useState("");
  const [response, setResponse] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();  // Prevent page reload
  console.log("Submitting with:", { provider, model, prompt });  // Debugging log

  try {
    // Send POST request
    const res = await axios.post("http://localhost:5001/v1/chat/completions", {
      provider,
      model,
      prompt,
    });
    console.log("Response:", res.data);  // Log response
    setResponse(res.data.response);  // Set response in state
  } catch (error) {
    console.error("Error:", error);  // Log error if request fails
    setResponse("Error: Unable to fetch response.");
    }
  };

  return (
    <div className="chat-container">
      <h2>Chat Completion</h2>
      <form onSubmit={handleSubmit} className="chat-form">
        <div className="input-group">
          <label>Provider:</label>
          <input
            type="text"
            value={provider}
            onChange={(e) => setProvider(e.target.value)}
            required
            className="input-field"
          />
        </div>
        <div className="input-group">
          <label>Model:</label>
          <input
            type="text"
            value={model}
            onChange={(e) => setModel(e.target.value)}
            required
            className="input-field"
          />
        </div>
        <div className="input-group">
          <label>Prompt:</label>
          <input
            type="text"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            required
            className="input-field"
          />
        </div>
        <button type="submit" className="submit-btn">Submit</button>
      </form>
      {response && <p className="response-text"><strong>Response:</strong> {response}</p>}
    </div>
  );
}

export default ChatCompletion;
