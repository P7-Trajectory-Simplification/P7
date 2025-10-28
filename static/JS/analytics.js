function get_metrics(algorithm, all_error_metrics) {
    switch(algorithm) {
        case 'DP':
            return all_error_metrics.DP;
        case 'DR':
            return all_error_metrics.DR;
        case 'SQUISH':
            return all_error_metrics.SQUISH;
        case 'SQUISH_E':
            return all_error_metrics.SQUISH_E;
        case 'SQUISH_RECKONING':
            return all_error_metrics.SQUISH_RECKONING;
        default:
            return null;
    }
}

function create_table(all_error_metrics) {
    let error_metrics = ['SED avg.', 'SED max', 'PED avg.', 'PED max', 'Compression Ratio'];
    table = document.createElement('table');
    const tr = table.insertRow();
    const td = tr.insertCell();
    error_metrics.forEach(metric => {
        const th = document.createElement('th');
        tr.appendChild(th);
        th.textContent = error_metrics[i];
    });
    selected = get_enabled_algorithms();
    let i = 0
    selected.forEach(algorithm => {
        const errors = get_metrics(algorithm, all_error_metrics);
        const tr = table.insertRow();
        const td = document.createElement('td');
        tr.appendChild(td);
        td.textContent = algorithm;
        for (let j = 0; j < errors.length; j++) {
            const td = document.createElement('td');
            tr.appendChild(td);
            td.textContent = errors[j];
        }
        i++;
    });
    analytics_info.querySelector('table').remove();
    analytics_info.append(table);
}



