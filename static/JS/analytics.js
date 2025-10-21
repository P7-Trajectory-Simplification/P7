

function create_table() {
    error_metrics = ['SED avg.', 'SED max', 'PED avg.', 'PED max']
    table = document.createElement('table');
    const tr = table.insertRow();
    const td = tr.insertCell();
    for(let i = 0; i <= 3; i++) {
        const th = document.createElement('th');
        tr.appendChild(th);
        th.textContent = error_metrics[i];
    }
    selected = get_selected_algorithms();
    let i = 0;
    selected.forEach(algorithm => {
        const tr = table.insertRow();
        const td = document.createElement('td');
        tr.appendChild(td);
        td.textContent = algorithm;
        console.log(all_error_metrics)
        const errors = all_error_metrics[i];
        console.log(errors);
        for (let j = 0; j < errors.length; j++) {
            const td = document.createElement('td');
            tr.appendChild(td);
            td.textContent = errors[j];
        }
        i++;
    });
    return table;
}



