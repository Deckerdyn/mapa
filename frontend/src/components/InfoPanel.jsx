import React, { useState } from "react";

const InfoPanel = () => {
  const [searchTerm, setSearchTerm] = useState("");

  return (
    <div id="info-panel">
      <h2>Localizaciones</h2>
      <input
        type="text"
        placeholder="Buscar por ID, calle, ciudad o estado"
        value={searchTerm}
        onChange={(e) => setSearchTerm(e.target.value)}
      />
      <div id="info-content">{/* Los datos se cargarán aquí */}</div>
    </div>
  );
};

export default InfoPanel;
