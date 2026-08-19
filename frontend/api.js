/* =========================================================
   NIRVAAN API LAYER

   Supports configurable backend URL for local development
   and production deployment (e.g. Vercel + Render).
========================================================= */


const API_BASE_URL =
    (typeof window !== "undefined" && window.NIRVAAN_API_URL)
    ? window.NIRVAAN_API_URL
    : "http://localhost:8000/api";


/* =========================================================
   GET LATEST DISASTER
========================================================= */

async function getLatestDisaster() {

    try {

        const response =
            await fetch(
                `${API_BASE_URL}/disaster/latest`
            );


        if (!response.ok) {

            throw new Error(
                `API request failed with status ${response.status}`
            );

        }


        const data =
            await response.json();


        return data;

    }

    catch (error) {

        console.log(
            "Backend API not connected or error occurred. Using demo fallback.",
            error
        );


        /*
            Fallback data matching NIRVAAN precomputed / static contract.
        */

        return {

            type: "Flood",

            location: "Emilia-Romagna, Italy",

            confidence: 94.7,

            severity: "LOW",

            affectedArea: "0.0 km²",

            beforeImage: "assets/before.jpg",

            afterImage: "assets/after.jpg",

            data_provenance: "SYNTHETIC_FALLBACK"

        };

    }

}



/* =========================================================
   GET DISASTER HISTORY
========================================================= */

async function getDisasterHistory() {

    try {

        const response =
            await fetch(
                `${API_BASE_URL}/disasters`
            );


        if (!response.ok) {

            throw new Error(
                `Unable to fetch disasters with status ${response.status}`
            );

        }


        return await response.json();

    }

    catch (error) {

        console.log(
            "Backend API not connected or error occurred. Using history fallback.",
            error
        );

        const list = (typeof nirvaanData !== "undefined" && nirvaanData.disasters)
            ? nirvaanData.disasters
            : [];
        return list.map(item => Object.assign({ data_provenance: "SYNTHETIC_FALLBACK" }, item));

    }

}



/* =========================================================
   GET SATELLITE IMAGES
========================================================= */

async function getSatelliteImages() {

    try {

        const response =
            await fetch(
                `${API_BASE_URL}/satellite/latest`
            );


        if (!response.ok) {

            throw new Error(
                `Satellite API unavailable with status ${response.status}`
            );

        }


        return await response.json();

    }

    catch (error) {

        console.log(
            "Backend API not connected or error occurred. Using satellite fallback.",
            error
        );

        return {

            beforeImage: "assets/before.jpg",

            afterImage: "assets/after.jpg",

            data_provenance: "SYNTHETIC_FALLBACK"

        };

    }

}