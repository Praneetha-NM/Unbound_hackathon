import { useState, useEffect } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";
import "./AdminPanel.css";

function AdminPanel() {
  const navigate = useNavigate();
  const [regexRules, setRegexRules] = useState([]);
  const [newRule, setNewRule] = useState({pattern: "", originalModel: "", redirectModel: "" });

  useEffect(() => {
    fetchRules();
  }, []);
  
  const fetchRules = async () => {
    try {
      const res = await axios.get("http://localhost:5005/regex-rules");
      console.log("Fetched Rules (Before Processing):", res.data);
  
      if (Array.isArray(res.data)) {
        const formattedRules = res.data.map(rule => ({
          id: rule[0], 
          originalModel: rule[1], 
          pattern: rule[2], 
          redirectModel: rule[3]
        }));
        
        console.log("Formatted Rules:", formattedRules);
        setRegexRules(formattedRules);
      } else {
        console.error("Unexpected API response format:", res.data);
      }
    } catch (error) {
      console.error("Error fetching rules:", error);
    }
  };
  
  
  

  const handleAddRule = async () => {
    if (!newRule.pattern || !newRule.originalModel || !newRule.redirectModel) {
      console.warn("Missing fields:", newRule);
      return;
    }
  
    try {
      console.log("Sending Rule Data:", JSON.stringify(newRule));
  
      const res = await axios.post("http://localhost:5005/regex-rules", newRule, {
        headers: { "Content-Type": "application/json" },
      });
  
      console.log("Rule added successfully:", res.data);
      fetchRules();
      setNewRule({ pattern: "", originalModel: "", redirectModel: "" });
    } catch (error) {
      console.error("Error adding rule:", error.response?.data || error);
    }
  };
  
  

  const handleDeleteRule = async (id) => {
    try {
      await axios.delete(`http://localhost:5005/regex-rules/${id}`);
  
      fetchRules();
    } catch (error) {
      console.error("Error deleting rule:", error);
    }
  };
  

  return (
    <div className="admin-container">
      <h2>Admin Panel - Regex Policies</h2>

      <div className="add-rule-form">
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

      <div className="back-button">
        <button onClick={() => navigate("/")}>Back to Chat</button>
      </div>
    </div>
  );
}

export default AdminPanel;
