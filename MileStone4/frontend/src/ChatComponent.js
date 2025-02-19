import { useState, useEffect } from "react";
import axios from "axios";
import './Chatcompletion.css'; // Assuming you have a separate CSS file

function ChatCompletion() {
  const [providers, setProviders] = useState([]);
  const [models, setModels] = useState([]);
  const [selectedProvider, setSelectedProvider] = useState("");
  const [selectedModel, setSelectedModel] = useState("");
  const [prompt, setPrompt] = useState("");
  const [response, setResponse] = useState("");
  const [messages, setMessages] = useState([]); // For chat history

  // Fetch models from the /models endpoint
  useEffect(() => {
    const fetchModels = async () => {
      try {
        const res = await axios.get("http://localhost:5003/models");
        const availableModels = res.data; // Assuming the response is an array of model objects
        setModels(availableModels);
        // Extract providers from the models
        const uniqueProviders = [
          ...new Set(availableModels.map((model) => model.provider)),
        ];
        setProviders(uniqueProviders);
      } catch (error) {
        console.error("Error fetching models:", error);
      }
    };

    fetchModels();
  }, []); // Empty dependency array to fetch data once on component mount

  const handleSubmit = async (e) => {
    e.preventDefault(); // Prevent page reload
    console.log("Submitting with:", { selectedProvider, selectedModel, prompt });

    // Add user message to chat history
    setMessages((prevMessages) => [
      ...prevMessages,
      { sender: "user", message: prompt },
    ]);

    try {
      // Send POST request
      const res = await axios.post("http://localhost:5003/v1/chat/completions", {
        provider: selectedProvider,
        model: selectedModel,
        prompt,
      });
      console.log("Response:", res.data); // Log response
      setResponse(res.data.response); // Set response in state

      // Add bot message to chat history
      setMessages((prevMessages) => [
        ...prevMessages,
        { sender: "bot", message: res.data.response },
      ]);
    } catch (error) {
      console.error("Error:", error); // Log error if request fails
      setResponse("Error: Unable to fetch response.");
    }
  };

  return (
    <div className="chat-container">
      <h2>Chat with AI</h2>
      <div className="chat-history">
        {messages.map((msg, index) => (
          <div
            key={index}
            className={`chat-message ${msg.sender === "user" ? "user-message" : "bot-message"}`}
          >
            <p>{msg.message}</p>
          </div>
        ))}
      </div>
      <form onSubmit={handleSubmit} className="chat-form">
        <div className="input-group">
          <label>Provider:</label>
          <select
            value={selectedProvider}
            onChange={(e) => setSelectedProvider(e.target.value)}
            required
            className="input-field"
          >
            <option value="">Select Provider</option>
            {providers.map((provider) => (
              <option key={provider} value={provider}>
                {provider}
              </option>
            ))}
          </select>
        </div>
        <div className="input-group">
          <label>Model:</label>
          <select
            value={selectedModel}
            onChange={(e) => setSelectedModel(e.target.value)}
            required
            className="input-field"
          >
            <option value="">Select Model</option>
            {models
              .filter((model) => model.provider === selectedProvider)
              .map((model) => (
                <option key={model.name} value={model.name}>
                  {model.model}
                </option>
              ))}
          </select>
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
        <button type="submit" className="submit-btn">Send</button>
      </form>
      {response && <p className="response-text"><strong>Response:</strong> {response}</p>}
    </div>
  );
}

export default ChatCompletion;
