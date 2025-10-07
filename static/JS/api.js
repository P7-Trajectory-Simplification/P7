async function algorithm_request() {
  selected = [];
  try {
    algorithms.forEach(alg => {
      if (alg.checked == true) {
        selected.push(alg.id)
      }
    });
    time = new Date(slider.value * 1000).toISOString().split('T')[1].split('.')[0];
    start_time = date_picker.value + " " + time;
  
    const response = await fetch(`/algorithm?algs=${selected}&start_time=${start_time}`);
    const data = await response.json();
    console.log(data);
  } catch (error) {
    console.error('Error fetching algorithm data:', error);
  }
}