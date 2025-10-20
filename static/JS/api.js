function algorithm_request(callback=null) {
    const algorithms = get_enabled_algorithms();
    const start_date = get_start_date();
    const end_date = get_end_date();

    if (algorithms.length < 1) return;
    
    request('algorithm', {algorithms: algorithms.join(','), start_date: start_date, end_date: end_date}, (data) => {
        let squish_data = data.SQUISH;
        let dp_data = data.DP;
        let dr_data = data.DR;
        let raw_data = data.raw;
        let all_error_metrics = data.error_metrics;
        
        clear_map();
        plot_to_map(squish_data, 'green');
        //plot_to_map(raw_data, 'blue');
        plot_to_map(dp_data, 'red');
        plot_to_map(dr_data, 'yellow');

        if (callback && callback instanceof Function) callback();
    });
}

function request(path, params, callback) {
    let parameters = '?';
    for (const key in params) {
        parameters += key + '=' + params[key] + '&';
    }
    parameters = parameters.slice(0, -1);
    fetch('/'+path + parameters)
        .then(response => response.json())
        .then(data => callback(data))
        .catch((error) => {
            console.error('Error:', error);
        });
}
