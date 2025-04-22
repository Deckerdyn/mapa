import React, { useState, useEffect } from "react";

const HistoryPanel = ({ onRouteSelect }) => {
  const [history, setHistory] = useState([]);
  const [searchTerm, setSearchTerm] = useState("");

  useEffect(() => {
    // Simular carga de datos
    fetch("/history")
      .then((res) => res.json())
      .then((data) => setHistory(data.history));
  }, []);

  const filteredHistory = history.filter((route) =>
    route.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div id="history">
      <h2>Historial</h2>
      <input
        type="text"
        placeholder="Buscar"
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
      />
      <div id="history-list">
        {filteredHistory.map((route, index) => (
          <button
            key={index}
            className="route-button"
            onClick={() => onRouteSelect(route)}
          >
            {route}
          </button>
        ))}
      </div>
    </div>
  );
};

export default HistoryPanel;
