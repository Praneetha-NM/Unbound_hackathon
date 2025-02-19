import React, { useState, useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom"; // Import useNavigate
import axios from "axios";
import './Chatcompletion.css'; // Assuming you have a separate CSS file

function ChatCompletion() {
  const [providers, setProviders] = useState([]);
  const [models, setModels] = useState([]);
  const [selectedProvider, setSelectedProvider] = useState("");
  const [selectedModel, setSelectedModel] = useState("");
  const [prompt, setPrompt] = useState("");
  const [file, setFile] = useState(null); // Added file state
  const [response, setResponse] = useState("");
  const [messages, setMessages] = useState([]); // For chat history

  const navigate = useNavigate(); // Initialize useNavigate

  // Fetch models from the /models endpoint
  useEffect(() => {
    const fetchModels = async () => {
      try {
        const res = await axios.get("http://localhost:5006/models");
        const availableModels = res.data;
        setModels(availableModels);

        // Extract providers from the models
        const uniqueProviders = [...new Set(availableModels.map((model) => model.provider))];
        setProviders(uniqueProviders);
      } catch (error) {
        console.error("Error fetching models:", error);
      }
    };

    fetchModels();
  }, []); // Empty dependency array to fetch data once on component mount

  const handleSubmit = async (e) => {
    e.preventDefault(); // Prevent page reload
    console.log("Submitting with:", { selectedProvider, selectedModel, prompt, file });

    const formData = new FormData();
    formData.append("provider", selectedProvider);
    formData.append("model", selectedModel);
    formData.append("prompt", prompt);
    if (file) {
        formData.append("file", file);
    }

    // Add user message to chat history
    setMessages((prevMessages) => [
        ...prevMessages,
        { sender: "user", message: prompt, file: file?.name },
    ]);

    try {
        const res = await axios.post("http://localhost:5006/v1/chat/completions", formData, {
            headers: { "Content-Type": "multipart/form-data" },
        });

        console.log("Response:", res.data);
        
        let botResponse = res.data.response.response || "No response from model.";
        if (res.data.File_response) {
          botResponse += `\n\n  \t File Response: ${res.data.File_response.response}`;
      }
        setResponse(botResponse);

        // Add bot message to chat history
        setMessages((prevMessages) => [
            ...prevMessages,
            { sender: "bot", message: botResponse },
        ]);
    } catch (error) {
        console.error("Error:", error);
        setResponse("Error: Unable to fetch response.");
    }
};


  return (
    <div className="chat-container">
      <h2>Chat with AI</h2>
      <div className="chat-history">
        {messages.map((msg, index) => (
          <div key={index} className={`chat-message ${msg.sender === "user" ? "user-message" : "bot-message"}`}>
            <p>{msg.message}</p>
            {msg.file && <p className="file-text">📂 File: {msg.file}</p>}
          </div>
        ))}
      </div>
      <form onSubmit={handleSubmit} className="chat-form">
        <div className="input-group">
          <label>Provider:</label>
          <select value={selectedProvider} onChange={(e) => setSelectedProvider(e.target.value)} required className="input-field">
            <option value="">Select Provider</option>
            {providers.map((provider) => (
              <option key={provider} value={provider}>{provider}</option>
            ))}
          </select>
        </div>
        <div className="input-group">
          <label>Model:</label>
          <select value={selectedModel} onChange={(e) => setSelectedModel(e.target.value)} required className="input-field">
            <option value="">Select Model</option>
            {models.map((model, index) => (
              <option key={index} value={model.model}>{model.model}</option>
            ))}
          </select>
        </div>
        <div className="input-group">
          <label>Prompt:</label>
          <input type="text" value={prompt} onChange={(e) => setPrompt(e.target.value)} required className="input-field" />
        </div>
        <div className="input-group">
          <label>Upload File:</label>
          <input type="file" onChange={(e) => setFile(e.target.files[0])} className="input-field" />
        </div>
        <button type="submit" className="submit-btn">Send</button>
        <button className="adm-button" onClick={() => navigate("/admin")}>Go to Admin Panel</button>
      </form>
      {response && <p className="response-text"><strong>Response:</strong> {response}</p>}
    </div>
  );
}

export default ChatCompletion;
