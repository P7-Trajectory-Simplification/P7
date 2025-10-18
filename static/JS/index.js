const algorithms = document.querySelectorAll('.algorithms .checkbox input');
const slider = document.getElementById('time_range');
const start_date = document.getElementById('start_date');
const end_date = document.getElementById('end_date');
const play_btn = document.getElementById('play_button');
const time_value = document.getElementById('time_value');
let running = false;

function get_enabled_algorithms() {
    let enabled = [];
    algorithms.forEach(alg => {
      if (alg.checked) {
        enabled.push(alg.id);
      }
    });
    return enabled;
}

function get_start_date() {
    return start_date.value;
}

function get_end_date() {
    const time = new Date(slider.value * 1000).toISOString().split('T')[1].split('.')[0];
    return end_date.value + ' ' + time;
}

function updateSlider() {
  const val = slider.value;
  const min = slider.min || 0;
  const max = slider.max || 100;
  const percent = ((val - min) / (max - min)) * 100;
  
  const date_time = new Date(val * 1000);
  time_value.value = date_time.toISOString().split('T')[1].split('.')[0];

  slider.style.background = `linear-gradient(to right, #d56c6c ${percent}%, #c9c9c9 ${percent}%)`;
}


function pass_time() {
  slider.value = parseInt(slider.value) + 3600; // 1 hour interval
  if (slider.value === slider.max) {
    slider.value = slider.min;
    let date = new Date(end_date.value);
    date.setDate(date.getDate() + 1);
    end_date.value = date.toISOString().split('T')[0];
  }
  updateSlider();
}

function start_pass_time() {
    pass_time();
    algorithm_request(() => {
        if (running) setTimeout(start_pass_time, 1000);
    });
}


// Event listeners 
algorithms.forEach(algorithm => algorithm.addEventListener('change', algorithm_request));
slider.addEventListener('input', algorithm_request);
start_date.addEventListener('input', algorithm_request);
end_date.addEventListener('input', algorithm_request);

play_btn.addEventListener('click',() => {
  play_btn.classList.toggle('play');
  play_btn.classList.toggle('pause');
  if (play_btn.classList.contains('pause')) {
      running = true;
    start_pass_time();
  } else {
    running = false;
  }
})

updateSlider(); // init