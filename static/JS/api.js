let dp_data = [];
let squish_data = [];
let squish_e_data = [];
let our_data = [];
let raw_data = [];
let all_error_metrics = [[]]; // 2D array to hold error metrics for each algorithm

function get_selected_algorithms() {
  selected = [];
  algorithms.forEach(alg => {
      if (alg.checked) {
        selected.push(alg.id)
      }
    });
  return selected;
}

async function algorithm_request() {
  selected = [];
  try {
    selected = get_selected_algorithms();
    time = new Date(slider.value * 1000).toISOString().split('T')[1].split('.')[0];
    end_time = date_picker.value + " " + time;

    const response = await fetch(`/algorithm?algs=${selected}&end_time=${end_time}`);
    const data = await response.json();
    dp_data = data.DP;
    raw_data = data.raw;
    clear_map();
    plot_to_map(raw_data, 'blue');
    plot_to_map(dp_data, 'red');
    console.log(data);

    const error_response = await fetch(`/error-metrics?algs=${selected}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      raw_data: raw_data,
      simplified_data: dp_data
    })
    });

const error_data = await error_response.json();
all_error_metrics = error_data;


    //const error_response = await fetch(`/error-metrics?algs=${selected}&raw_data=${raw_data}&simplified_data=${dp_data}`);
    //const error_data = await error_response.json();
    all_error_metrics = error_data;
  } catch (error) {
    console.error('Error fetching algorithm data:', error);
  }
} 