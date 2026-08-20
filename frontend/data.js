/* =========================================================
   NIRVAAN FRONTEND STATE CONTAINER (frontend/data.js)

   Clean initial state container. No fake, hardcoded or mock datasets.
========================================================= */

const nirvaanData = {
    disasters: [],
    alerts: [],
    satellites: [],
    statistics: {
        activeDisasters: 0,
        affectedArea: "0.0 km²",
        populationAtRisk: "0",
        detectionAccuracy: "0.0%"
    }
};