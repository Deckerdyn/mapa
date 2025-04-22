import React, { useEffect, useRef, useState } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

// Fix para íconos rotos
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: require("leaflet/dist/images/marker-icon-2x.png").default,
  iconUrl: require("leaflet/dist/images/marker-icon.png").default,
  shadowUrl: require("leaflet/dist/images/marker-shadow.png").default,
});

const MapView = ({ routeCoordinates }) => {
  const mapRef = useRef(null);
  const mapInstance = useRef(null);
  const layerRef = useRef(null);
  const markerRef = useRef(null);

  // Inicialización del mapa (solo una vez)
  useEffect(() => {
    if (!mapInstance.current && mapRef.current) {
      // Crear nueva instancia solo si no existe
      mapInstance.current = L.map(mapRef.current, {
        preferCanvas: true,
      }).setView([-41.4682, -72.9441], 10);

      L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        attribution: "© OpenStreetMap contributors",
      }).addTo(mapInstance.current);

      // Configurar ícono personalizado
      const truckIcon = L.icon({
        iconUrl: "/camion.png",
        iconSize: [40, 40],
        iconAnchor: [20, 40],
      });

      markerRef.current = L.marker([-41.4682, -72.9441], {
        icon: truckIcon,
      }).addTo(mapInstance.current);

      layerRef.current = L.layerGroup().addTo(mapInstance.current);
    }

    // Limpieza al desmontar
    return () => {
      if (mapInstance.current) {
        mapInstance.current.remove();
        mapInstance.current = null;
      }
    };
  }, []);

  // Actualizar ruta cuando cambian las coordenadas
  useEffect(() => {
    if (!mapInstance.current || !routeCoordinates) return;

    // Limpiar capa anterior
    layerRef.current.clearLayers();

    // Dibujar nueva ruta
    if (routeCoordinates.length > 0) {
      const polyline = L.polyline(routeCoordinates, { color: "blue" });
      layerRef.current.addLayer(polyline);
      mapInstance.current.fitBounds(polyline.getBounds());
      markerRef.current.setLatLng(routeCoordinates[0]);
    }
  }, [routeCoordinates]);

  return (
    <div
      ref={mapRef}
      style={{
        height: "100vh",
        width: "100%",
        zIndex: 0,
      }}
    />
  );
};

export default MapView;
