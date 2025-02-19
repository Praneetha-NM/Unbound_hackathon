import { useEffect, useState } from "react";
import axios from "axios";

function ModelsList() {
  const [models, setModels] = useState([]);

  useEffect(() => {
    axios.get("http://127.0.0.1:5000/models")
      .then(response => setModels(response.data))
      .catch(error => console.error("Error fetching models:", error));
  }, []);

  return (
    <div>
      <h2>Supported Models</h2>
      <ul>
        {models.map((model, index) => (
          <li key={index}>{model}</li>
        ))}
      </ul>
    </div>
  );
}

export default ModelsList;
