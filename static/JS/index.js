
var map = L.map('map').setView([57.04708, 9.924603], 12);

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
algorithms.addEventListener("click", (event) => {
    switchSelectedButton(event);
    switchAlgorithm();
})



//Disables the new selected button
function switchSelectedButton(event) {
  if (event.target.tagName === "BUTTON" && event.target != selected) {
        selected.disabled = false;
        event.target.disabled = true;
        selected = event.target;
  }
}

switchAlgorithm = async () => {
  //Implement algorithm switching here
  try {
    console.log(`Selected algorithm: ${selected.id}`);
    const response = await fetch(`/algorithm?name=${selected.id}`);
    const data = await response.json();
    console.log(data);
  } catch (error) {
    console.error('Error fetching algorithm data:', error);
  }
}