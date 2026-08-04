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