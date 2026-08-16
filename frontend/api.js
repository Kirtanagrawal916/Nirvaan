/* =========================================================
   NIRVAAN API LAYER

   IMPORTANT:

   Your backend teammate can later replace
   the placeholder URL below with the actual
   backend API.

========================================================= */


const API_BASE_URL =
    "http://localhost:5000/api";


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
                "API request failed"
            );

        }


        const data =
            await response.json();


        return data;


    }

    catch (error) {

        console.log(
            "Backend API not connected yet."
        );


        /*
            Temporary prototype data.

            Once backend is ready,
            this fallback won't be needed.
        */

        return {

            type: "Flood",

            location:
                "Surat, Gujarat",

            confidence: 94.7,

            severity: "HIGH",

            affectedArea:
                "31.8 km²",

            beforeImage:
                null,

            afterImage:
                null

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
                "Unable to fetch disasters"
            );

        }


        return await response.json();

    }

    catch (error) {

        return nirvaanData.disasters;

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
                "Satellite API unavailable"
            );

        }


        return await response.json();

    }

    catch (error) {

        return {

            beforeImage: null,

            afterImage: null

        };

    }

}