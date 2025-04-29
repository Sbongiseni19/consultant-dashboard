document.getElementById('bookingForm').addEventListener('submit', function (event) {
    event.preventDefault(); // Prevent form from reloading the page

    const formData = {
        name: document.getElementById('name').value,
        id_number: document.getElementById('id_number').value,
        bank: document.getElementById("bank").value,
        email: document.getElementById("email").value,
        service: document.getElementById("service").value
    };

    // Send the data to the backend (POST request)
    fetch('http://localhost:8000/book', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
    })
        .then(response => response.json())
        .then(data => {
            alert('Booking successful!');
            // Optionally, clear the form
            document.getElementById('bookingForm').reset();
        })
        .catch(error => {
            alert('Error occurred while booking!');
            console.error('Error:', error);
        });
});
