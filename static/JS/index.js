
var map = L.map('map').setView([51.505, -0.09], 13);

L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
}).addTo(map);

//Shows which button/algorithm is initially selected
document.getElementById("Ours").setAttribute("disabled", true);

const algorithms = document.querySelector(".algorithms");
var selected = algorithms.querySelector("button[disabled]");

/*This event listener decides which button has been pressed, and should therefore
also be used to implement the algorithms*/
algorithms.addEventListener("click", (event)=>{
    //Disbales the new selected button
    if (event.target.tagName === "BUTTON" && event.target != selected) {
        selected.disabled = false;
        event.target.disabled = true;
        selected = event.target;
    }
})

