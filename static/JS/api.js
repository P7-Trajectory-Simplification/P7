let dp_data = [];
let reckoning_data = [];
let squish_data = [];
let squish_e_data = [];
let our_data = [];
let raw_data = [];

async function algorithm_request() {
  selected = [];
  try {
    algorithms.forEach(alg => {
      if (alg.checked) {
        selected.push(alg.id);
      }
    });
    time = new Date(slider.value * 1000).toISOString().split('T')[1].split('.')[0];
    start_time = start_date.value;
    end_time = end_date.value + ' ' + time;
    

    const response = await fetch(`/algorithm?algs=${selected}&start_time=${start_time}&end_time=${end_time}`);
    const data = await response.json();
    squish_data = data.SQUISH?data.SQUISH:[];
    dp_data = data.DP?data.DP:[];
    reckoning_data = data.DR?data.DR:[];
    raw_data = data.raw?data.raw:[];
    clear_map();
    plot_to_map(squish_data, 'green');
    //plot_to_map(raw_data, 'blue');
    plot_to_map(dp_data, 'red');
    plot_to_map(reckoning_data, 'yellow');
    console.log(data);
  } catch (error) {
    console.error('Error fetching algorithm data:', error);
  }
} 