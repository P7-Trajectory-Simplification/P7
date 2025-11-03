const algorithms = document.querySelectorAll('.algorithms .checkbox input');
const slider = document.getElementById('time_range');
const start_date = document.getElementById('start_date');
const end_date = document.getElementById('end_date');
const play_btn = document.getElementById('play_button');
const time_value = document.getElementById('time_value');
const show_errors = document.getElementById('show_errors');
const analytics_info = document.getElementById('analytics_info');
const parameter_inputs = document.querySelectorAll('.alg_params input')
const alg_input_needed = {
    "SQUISH":["buff_size"], 
    "DP":["epsilon"], 
    "DR":["tolerance"],
    "SQUISH_E": ["low_comp", "max_sed"],
    "UNIFORM_SAMPLING": ["sampling_rate"],
    "SQUISH_RECKONING": ["buff_size"]
};
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

function get_params_for_algs() {
    let values = {};
    parameter_inputs.forEach(input => {
        const min = parseInt(input.min);
        const max = parseInt(input.max);
        const value = parseInt(input.value);
        if (input.hasAttribute("min") && min > value) {
            input.value = input.min;
        };
        if (input.hasAttribute("max") && max < value) {
            input.value = input.max;
        };
        values[input.name] = parseInt(input.value);
    });
    return values;
}

function show_help(desc) {
    const existing = document.querySelector('.help-box');
    if (existing) existing.remove();

    // Create help box
    const div = document.createElement('div');
    div.className = 'help-box';
    
    const text = document.createElement('p');
    text.textContent = desc;

    // Create close button
    const closeBtn = document.createElement('button');
    closeBtn.className = 'close-btn';
    closeBtn.innerHTML = `<svg viewBox="0 0 24 24"> <line x1="18" y1="6" x2="6" y2="18" /> <line x1="6" y1="6" x2="18" y2="18" /></svg>`;
    closeBtn.onclick = () => div.remove();

    // Append button and box to DOM
    div.appendChild(text);
    div.appendChild(closeBtn);
    document.body.appendChild(div);
}

function updateSlider() {
    const val = slider.value;
    const min = slider.min || 0;
    const max = slider.max || 100;
    const percent = ((val - min) / (max - min)) * 100;
    const date = new Date(end_date.value).toISOString().split('T')[0].split('-');
    const time = new Date(val * 1000).toISOString().split('T')[1].split('.')[0];
    const date_time_string = date[2] + '-' + date[1] + '-' + date[0] + ' ' + time;

    //const split_date_time = date_time.toISOString().split('T');
    time_value.value = date_time_string;

    slider.style.background = `linear-gradient(to right, #d56c6c ${percent}%, #c9c9c9 ${percent}%)`;
}


function pass_time() {
    slider.value = parseInt(slider.value) + 3600; // 1 hour interval
    if (parseInt(slider.value) === 3600 * 23) {
        slider.value = slider.min;
        let date = new Date(end_date.value);
        date.setDate(date.getDate() + 1);
        end_date.value = date.toISOString().split('T')[0];
    }
    updateSlider();
}

function start_pass_time() {
    algorithm_request(() => {
        pass_time();
        if (running) setTimeout(start_pass_time, 1000);
    });
}

function toggle_buttons() {
    enabled = get_enabled_algorithms();
    if (enabled.length === 0) {
        show_errors.disabled = true;
        play_btn.disabled = true;
    } else {
        show_errors.disabled = false;
        play_btn.disabled = false;
    }
    toggle_params(enabled)
}

function toggle_params(enabled) {
    parameter_inputs.forEach(input => {
        input.disabled = true;
    })
    enabled.forEach(alg_id => {
        params = alg_input_needed[alg_id];
        params.forEach(param => {
            document.getElementById(param).disabled = false;
        })
    });
}

algorithms.forEach(alg => {
    alg.addEventListener('change', toggle_buttons);
});

show_errors.addEventListener('click', () => {
  if (get_enabled_algorithms().length === 0) return;
  show_errors.classList.toggle('active');
  analytics_info.classList.toggle('active');
});

play_btn.addEventListener('click',() => {
    if (get_enabled_algorithms().length === 0) return;
    play_btn.classList.toggle('play');
    play_btn.classList.toggle('pause');
    if (play_btn.classList.contains('pause')) {
        running = true;
        start_pass_time();
    } else {
        running = false;
    }
})




toggle_buttons();
updateSlider(); // init
