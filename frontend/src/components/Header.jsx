import React from "react";

const Header = ({ onToggleLiveMode }) => {
  return (
    <header id="app-header">
      <h1 id="header-title">Monitor de Rutas Logísticas</h1>
      <div id="header-controls">
        <button className="header-button" onClick={onToggleLiveMode}>
          ⏯️ Simulación
        </button>
      </div>
    </header>
  );
};

export default Header;
