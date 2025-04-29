import requests

booking_data = {
    "customer": "John Doe",
    "service": "Loan Application",
    "status": "Pending"
}

response = requests.post("http://127.0.0.1:8000/book", json=booking_data)

print(response.json())  # Should print: {"message": "Booking created successfully"}
