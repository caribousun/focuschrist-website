/* Shared terrain background. Leaflet continues to own pins, routes and controls. */
(function () {
  'use strict';
  var script = document.currentScript;
  var styleUrl = new URL('timeline-terrain-style.json?v=20261004-english-terrain-1', script.src).href;
  var credit = '<a href="https://openfreemap.org/" target="_blank" rel="noopener noreferrer">OpenFreeMap</a> · <a href="https://www.openmaptiles.org/" target="_blank" rel="noopener noreferrer">© OpenMapTiles</a> · <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener noreferrer">OpenStreetMap</a> · <a href="https://mapterhorn.com/attribution/" target="_blank" rel="noopener noreferrer">Mapterhorn terrain</a>';
  window.FCTerrainLayer = function () {
    var handlers = {}, layer, gl, terrainReady = false;
    var failedSources = Object.create(null), unknownFailure = false;
    function emit(name) { if (handlers[name]) handlers[name](); }
    function unavailable(event) {
      terrainReady = false;
      if (event && event.sourceId) failedSources[event.sourceId] = false;
      else unknownFailure = true;
      if (window.console) console.warn('Terrain map unavailable', event && event.error ? event.error.message : event && event.message ? event.message : 'Tile provider unavailable');
      for (var i = 0; i < 3; i++) emit('tileerror');
    }
    return {
      on: function (name, callback) { handlers[name] = callback; return this; },
      addTo: function (map) {
        if (map.attributionControl) map.attributionControl.addAttribution(credit);
        try {
          if (!window.maplibregl || !window.MaplibreGLLeaflet) throw new Error('Terrain renderer unavailable');
          layer = MaplibreGLLeaflet.maplibreGL({style: styleUrl, attributionControl: false, interactive: false, maxZoom: 19});
          layer.addTo(map);
          gl = layer.getMaplibreMap();
          gl.on('sourcedata', function (event) {
            if (event.sourceId === 'terrain-dem' && event.sourceDataType === 'content') terrainReady = true;
            if (event.sourceDataType === 'content' && Object.prototype.hasOwnProperty.call(failedSources, event.sourceId)) {
              failedSources[event.sourceId] = true;
            }
          });
          gl.on('idle', function () {
            // A settled renderer can include failed tiles. Each failed source must
            // supply fresh content and settle before the fallback can be removed.
            Object.keys(failedSources).forEach(function (id) {
              if (failedSources[id] && gl.isSourceLoaded(id)) delete failedSources[id];
            });
            if (!unknownFailure && !Object.keys(failedSources).length && terrainReady && gl.loaded() && gl.isSourceLoaded('terrain-dem')) emit('tileload');
          });
          gl.on('error', unavailable);
        } catch (error) { unavailable(error); }
        return this;
      }
    };
  };
})();
