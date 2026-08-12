const predictBtn = document.getElementById("predictBtn");
const prediction = document.getElementById("prediction");

predictBtn.addEventListener("click", async () => {

    try {

        const response = await fetch("http://127.0.0.1:8000/test");

        const data = await response.json();

        if (data.prediction === 1) {
            prediction.innerHTML = "⚠️ Shipment Delay Expected";
            prediction.style.color = "red";
        }
        else {
            prediction.innerHTML = "✅ Shipment On Time";
            prediction.style.color = "green";
        }

    }

    catch (error) {

        prediction.innerHTML = "❌ Backend not running";
        prediction.style.color = "orange";

    }

});


const customBtn = document.getElementById("customPredictBtn");
const customPrediction = document.getElementById("customPrediction");

customBtn.addEventListener("click", async () => {

    const payload = {
        country: document.getElementById("country").value,
        shipmentMode: document.getElementById("shipmentMode").value,
        weight: document.getElementById("weight").value,
        freightCost: document.getElementById("freightCost").value,
    };

    try {

        const response = await fetch("http://127.0.0.1:8000/predict_custom", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });

        const data = await response.json();

        if (data.error) {
            customPrediction.innerHTML = "❌ " + data.error;
            customPrediction.style.color = "orange";
        }
        else if (data.prediction === 1) {
            customPrediction.innerHTML = "⚠️ Shipment Delay Expected";
            customPrediction.style.color = "red";
        }
        else {
            customPrediction.innerHTML = "✅ Shipment On Time";
            customPrediction.style.color = "green";
        }

    }

    catch (error) {

        customPrediction.innerHTML = "❌ Backend not running";
        customPrediction.style.color = "orange";

    }

});