document.getElementById('sudokuForm').addEventListener('submit', function(event) {
    event.preventDefault();

    let solution = '';
    for (let row = 0; row < 9; row++) {
        for (let col = 0; col < 9; col++) {
            let value = document.getElementById(`cell_${row}_${col}`).value;
            solution += value ? value : '0';  // Use '0' for empty cells
        }
    }

    console.log('Solution:', solution);  // Debugging log

    fetch('/check_solution', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: `solution=${solution}&puzzle_id={{ puzzle_id }}`
    })
    .then(response => response.json())
    .then(data => {
        const result = document.getElementById('result');
        if (data.status === 'success') {
            result.textContent = data.message;
            result.style.color = 'green';
        } else {
            result.textContent = data.message;
            result.style.color = 'red';
        }
    })
    .catch(error => {
        console.error('Error:', error);  // Log any errors that occur during the request
    });
});
