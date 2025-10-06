
var map = L.map('map').setView([57.04708, 9.924603], 12);

L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
}).addTo(map);


const algorithms = document.querySelectorAll(".checkbox input")
const slider = document.querySelector("#time_range")
const date_picker = document.querySelector("#date_picker")
let is_checked = false;

/*This event listener decides which button has been pressed, and should therefore
also be used to implement the algorithms*/
algorithms.forEach(algorithm => {
    algorithm.addEventListener("change", () => {
      check_checked();
      if (is_checked) {
        algorithm_request();
      }
    });
});

slider.addEventListener("input", () => {
  if (is_checked) {
    algorithm_request();
  }
});

date_picker.addEventListener("input", () => {
  if (is_checked) {
    algorithm_request();
  }
});


algorithm_request = async () => {
  selected = [];
  //Implement algorithm switching here
  try {
    algorithms.forEach(alg => {
      if (alg.checked == true) {
        selected.push(alg.id)
      }
    });
    time = new Date(slider.value * 1000).toISOString().split('T')[1].split('.')[0];
    start_time = date_picker.value + " " + time;
  
    console.log(`Selected algorithm(s): ${selected}`);
    const response = await fetch(`/algorithm?algs=${selected}&start_time=${start_time}`);
    const data = await response.json();
    console.log(data);
  } catch (error) {
    console.error('Error fetching algorithm data:', error);
  }
}


function updateSlider() {
  const val = slider.value;
  const min = slider.min || 0;
  const max = slider.max || 100;
  const percent = ((val - min) / (max - min)) * 100;
  
  var date_time = new Date(val * 1000);
  var time = date_time.toISOString().split('T')[1].split('.')[0];

  //First timestamp = 2024-01-01 00:00:01
  // Update output
  time_value.value = time;
  
  // Update fill style
  slider.style.background = `linear-gradient(to right, #d56c6c ${percent}%, #c9c9c9 ${percent}%)`;
}
updateSlider(); // init


function check_checked() {
  let count = 0;
  algorithms.forEach(alg => {
    if (alg.checked == true) {
      is_checked = true;
      count++;
    }
  });
  if (count == 0) {
    is_checked = false;
  }
}

function pass_time() {
  slider.value = parseInt(slider.value) + 1;
  if (slider.value == slider.max) {
    slider.value = slider.min;
    let date = new Date(date_picker.value);
    date.setDate(date.getDate() + 1);
    date_picker.value = date.toISOString().split('T')[0];
  }
  updateSlider();
  if (is_checked) {
    algorithm_request();
  }
}

let start_pass_time = () => {
  setInterval(pass_time, 1000);
}
let stop_pass_time = () => {
  clearInterval(pass_time);
}

start_pass_time()