import React, { useState } from "react";
import Header from "./components/Header";
import HistoryPanel from "./components/HistoryPanel";
import InfoPanel from "./components/InfoPanel";
import MapView from "./components/MapView";
import "./App.css";

function App() {
  const [liveMode, setLiveMode] = useState(false);
  const [selectedRoute, setSelectedRoute] = useState(null);

  const handleToggleLiveMode = () => {
    setLiveMode(!liveMode);
  };

  const handleRouteSelect = (routeName) => {
    setSelectedRoute(routeName);
    // Aquí podrías cargar las coordenadas de la ruta seleccionada
  };

  return (
    <div className="app-container">
      <Header onToggleLiveMode={handleToggleLiveMode} />
      <HistoryPanel onRouteSelect={handleRouteSelect} />
      <MapView routeCoordinates={selectedRoute?.coordinates} />
      <InfoPanel />
    </div>
  );
}

export default App;
