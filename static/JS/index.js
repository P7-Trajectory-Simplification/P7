const algorithms = document.querySelectorAll(".checkbox input")
const slider = document.querySelector("#time_range")
const date_picker = document.querySelector("#date_picker")
const play_btn = document.querySelector('#play_button');
const forward_btn = document.querySelector('#forward');
const rewind_btn = document.querySelector('#rewind');
const speeds = [1, 5, 10, 30, 60, 300, 600, 1800, 3600]; // seconds per step

let speed_state = 0;
let is_checked = false;
let time_step = 1;
let interval;


//Functions
function request_if_checked() {
  if (is_checked) {
    algorithm_request();
  }
}

function updateSlider() {
  const val = slider.value;
  const min = slider.min || 0;
  const max = slider.max || 100;
  const percent = ((val - min) / (max - min)) * 100;
  
  var date_time = new Date(val * 1000);
  var time = date_time.toISOString().split('T')[1].split('.')[0];
  time_value.value = time;

  slider.style.background = `linear-gradient(to right, #d56c6c ${percent}%, #c9c9c9 ${percent}%)`;
}



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
  slider.value = parseInt(slider.value) + time_step;
  if (slider.value == slider.max) {
    slider.value = slider.min;
    let date = new Date(date_picker.value);
    date.setDate(date.getDate() + 1);
    date_picker.value = date.toISOString().split('T')[0];
  }
  updateSlider();
  request_if_checked();
}

function start_pass_time() {
  interval = setInterval(pass_time, 1000);
}
function stop_pass_time() {
  clearInterval(interval);
}


// Event listeners 
algorithms.forEach(algorithm => algorithm.addEventListener("change", () => {
  check_checked();
  request_if_checked();
}));
slider.addEventListener("input", request_if_checked);
date_picker.addEventListener("input", request_if_checked);

play_btn.addEventListener('click',() => {
  play_btn.classList.toggle('play')
  play_btn.classList.toggle('pause')
  if (play_btn.classList.contains('pause')) {
    start_pass_time()
  } else {
    stop_pass_time()
  }
})

forward_btn.addEventListener('click', () => {
  speed_state = Math.min(speeds.length - 1, speed_state + 1);
  time_step = speeds[speed_state];
})

rewind_btn.addEventListener('click', () => {
  speed_state = Math.max(0, speed_state - 1);
  time_step = speeds[speed_state];
})


updateSlider(); // init