const predictBtn = document.getElementById("predictBtn");
const prediction = document.getElementById("prediction");
const recommendedActions = document.getElementById("recommendedActions");

function renderRecommendations(baseFreightCost) {
    const airCost = baseFreightCost * 1.5;
    const secondaryCost = baseFreightCost * 1.1;
    const secondaryPercent = ((secondaryCost - baseFreightCost) / baseFreightCost) * 100;

    document.getElementById("airFreightCost").innerHTML =
        "$" + airCost.toLocaleString(undefined, { maximumFractionDigits: 0 });

    document.getElementById("secondarySupplierCost").innerHTML =
        "+" + secondaryPercent.toFixed(0) + "%";

    recommendedActions.style.display = "block";
}

predictBtn.addEventListener("click", async () => {

    prediction.innerHTML = "⏳ Predicting...";
    prediction.style.color = "#6b7280";

    try {

        const response = await fetch("http://127.0.0.1:8000/test");

        const data = await response.json();

        if (data.prediction === 1) {
            prediction.innerHTML = "⚠️ Shipment Delay Expected";
            prediction.style.color = "red";
            recommendedActions.style.display = "block";
        }
        else {
            prediction.innerHTML = "✅ Shipment On Time";
            prediction.style.color = "green";
            recommendedActions.style.display = "none";
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

    const weightVal = document.getElementById("weight").value;
    const freightVal = document.getElementById("freightCost").value;

    if (!weightVal || !freightVal) {
        customPrediction.innerHTML = "⚠️ Please fill in weight and freight cost";
        customPrediction.style.color = "orange";
        return;
    }

    if (Number(weightVal) <= 0 || Number(freightVal) <= 0) {
        customPrediction.innerHTML = "⚠️ Weight and freight cost must be positive numbers";
        customPrediction.style.color = "orange";
        return;
    }

    const payload = {
        country: document.getElementById("country").value,
        shipmentMode: document.getElementById("shipmentMode").value,
        weight: weightVal,
        freightCost: freightVal,
    };

    customPrediction.innerHTML = "⏳ Predicting...";
    customPrediction.style.color = "#6b7280";

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
            renderRecommendations(Number(freightVal));
        }
        else {
            customPrediction.innerHTML = "✅ Shipment On Time";
            customPrediction.style.color = "green";
            recommendedActions.style.display = "none";
        }

    }

    catch (error) {

        customPrediction.innerHTML = "❌ Backend not running";
        customPrediction.style.color = "orange";

    }

});