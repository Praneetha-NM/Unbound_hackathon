import { useState, useEffect } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import "./AdminPanel.css";

function AdminPanel() {
  const navigate = useNavigate();
  const [regexRules, setRegexRules] = useState([]);
  const [newRule, setNewRule] = useState({ pattern: "", originalModel: "", redirectModel: "" });
  const [fileUploadModel, setFileUploadModel] = useState(""); // State for file upload routing

  useEffect(() => {
    fetchRules();
    fetchFileUploadModel();
  }, []);

  // Fetch existing regex rules
  const fetchRules = async () => {
    try {
      const res = await axios.get("http://localhost:5006/regex-rules");
      if (Array.isArray(res.data)) {
        setRegexRules(res.data.map(rule => ({
          id: rule[0], 
          originalModel: rule[1], 
          pattern: rule[2], 
          redirectModel: rule[3]
        })));
      } else {
        console.error("Unexpected API response format:", res.data);
      }
    } catch (error) {
      console.error("Error fetching rules:", error);
    }
  };

  // Fetch file upload routing model
  const fetchFileUploadModel = async () => {
    try {
      const res = await axios.get("http://localhost:5006/file-upload-routing");
      setFileUploadModel(res.data?.model || "");
    } catch (error) {
      console.error("Error fetching file upload model:", error);
    }
  };

  // Add a new regex rule
  const handleAddRule = async () => {
    if (!newRule.pattern || !newRule.originalModel || !newRule.redirectModel) {
      console.warn("Missing fields:", newRule);
      return;
    }
    try {
      await axios.post("http://localhost:5006/regex-rules", newRule, {
        headers: { "Content-Type": "application/json" },
      });
      fetchRules();
      setNewRule({ pattern: "", originalModel: "", redirectModel: "" });
    } catch (error) {
      console.error("Error adding rule:", error.response?.data || error);
    }
  };

  // Delete a regex rule
  const handleDeleteRule = async (id) => {
    try {
      await axios.delete(`http://localhost:5006/regex-rules/${id}`);
      fetchRules();
    } catch (error) {
      console.error("Error deleting rule:", error);
    }
  };

  // Update file upload routing model
  const handleFileUploadModelChange = async () => {
    if (!fileUploadModel) {
      console.warn("File upload model is empty");
      return;
    }
    try {
      const res = await axios.post("http://localhost:5006/file-upload-routing", { model: fileUploadModel }, {
        headers: { "Content-Type": "application/json" },
      });
      alert(res.data.message);
    } catch (error) {
      alert(error.response?.data?.error || "Error updating file upload model");
      console.error("Error updating file upload model:", error.response?.data || error);
    }
  };

  return (
    <div className="admin-container">
      <h2>Admin Panel - Routing Policies</h2>

      {/* Regex Rules Section */}
      <div className="add-rule-form">
        <h3>Regex-Based Routing</h3>
        <input
          type="text"
          placeholder="Regex Pattern"
          value={newRule.pattern}
          onChange={(e) => setNewRule({ ...newRule, pattern: e.target.value })}
        />
        <input
          type="text"
          placeholder="Original Model"
          value={newRule.originalModel}
          onChange={(e) => setNewRule({ ...newRule, originalModel: e.target.value })}
        />
        <input
          type="text"
          placeholder="Redirect Model"
          value={newRule.redirectModel}
          onChange={(e) => setNewRule({ ...newRule, redirectModel: e.target.value })}
        />
        <button onClick={handleAddRule}>Add Rule</button>
      </div>

      <table>
        <thead>
          <tr>
            <th>Regex Pattern</th>
            <th>Original Model</th>
            <th>Redirect Model</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {regexRules.map((rule) => (
            <tr key={rule.id}>
              <td>{rule.pattern || "N/A" }</td>
              <td>{rule.originalModel}</td>
              <td>{rule.redirectModel}</td>
              <td>
                <button onClick={() => handleDeleteRule(rule.id)}>Delete</button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {/* File Upload Routing Section */}
      <div className="file-routing-form">
        <h3>File Upload Routing Policy</h3>
        <input
          type="text"
          placeholder="Enter Model for File Uploads"
          value={fileUploadModel}
          onChange={(e) => setFileUploadModel(e.target.value)}
        />
        <button onClick={handleFileUploadModelChange}>Update Routing</button>
      </div>

      <div className="back-button">
        <button onClick={() => navigate("/")}>Back to Chat</button>
      </div>
    </div>
  );
}

export default AdminPanel;
