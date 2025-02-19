import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import './App.css'; 
import ChatComponent from "./ChatComponent";
import AdminPanel from "./AdminPanel"

function App() {
  return (
    <Router>
      <div>
        <h1 className="heading">MileStone 5 : Admin Portal for Regex Policies</h1>
        <Routes>
          <Route path="/" element={<ChatComponent />} />
          <Route path="/admin" element={<AdminPanel />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
