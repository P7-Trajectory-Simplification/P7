function algorithm_request(callback = null) {
    const algorithms = get_enabled_algorithms();
    const start_date = get_start_date();
    const end_date = get_end_date();

    if (algorithms.length < 1) return;
    
    request("algorithm", {algorithms: JSON.stringify(algorithms), start_date: start_date, end_date: end_date}, (data) => {
        create_table({
            DP: data.DP_error_metrics,
            DR: data.DR_error_metrics,
            SQUISH: data.SQUISH_error_metrics
        });

        clear_map();
        plot_to_map(data.SQUISH, "green");
        plot_to_map(data.SQUISH_E, "cyan")
        plot_to_map(data.SQUISH_RECKONING, 'magenta')
        plot_to_map(data.raw, "blue");
        plot_to_map(data.DP, "red");
        plot_to_map(data.DR, "yellow");

        if (callback && callback instanceof Function) callback();
    });
}

function request(path, params, callback) {
    let body = {};
    for (const key in params) {
        body[key] = params[key];
    }
    fetch("/"+path, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: body
    })
        .then(response => response.json())
        .then(data => callback(data))
        .catch((error) => {
            console.error("Error:", error);
        });
}
