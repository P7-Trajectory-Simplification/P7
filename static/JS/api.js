let dp_data = [];
let squish_data = [];
let squish_e_data = [];
let our_data = [];
let raw_data = [];

async function algorithm_request() {
  selected = [];
  try {
    algorithms.forEach(alg => {
      if (alg.checked) {
        selected.push(alg.id)
      }
    });
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
  } catch (error) {
    console.error('Error fetching algorithm data:', error);
  }
} 