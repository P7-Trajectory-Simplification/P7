

function create_table() {
    error_metrics = ['SED avg.', 'SED max', 'PED avg.', 'PED max']
    table = document.createElement('table');
    const tr = table.insertRow();
    const td = tr.insertCell();
    for(let i = 0; i <= 3; i++) {
        const td = document.createElement('th');
        tr.appendChild(td);
        td.textContent = error_metrics[i];
    }
    selected = get_selected_algorithms();
    selected.forEach(algorithm => {
        const tr = table.insertRow();
        tr.textContent = algorithm;
    });
    return table;
}



