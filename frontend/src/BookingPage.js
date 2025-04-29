// src/BookingPage.js

import React, { useState } from "react";
import axios from "axios";

const BookingPage = () => {
    const [customer, setCustomer] = useState("");
    const [email, setEmail] = useState("");
    const [slot, setSlot] = useState("");
    const [status, setStatus] = useState("");
    const [isSuccess, setIsSuccess] = useState(false);

    const handleBooking = async (e) => {
        e.preventDefault();
        const bookingData = { customer, email, slot, status };

        try {
            const response = await axios.post("http://127.0.0.1:8000/book", bookingData);
            if (response.status === 200) {
                setIsSuccess(true);
                // Optionally, reset the form
                setCustomer("");
                setEmail("");
                setSlot("");
                setStatus("");
            }
        } catch (error) {
            console.error("Error booking slot:", error);
        }
    };

    return (
        <div>
            <h1>Register and Book a Slot</h1>
            {isSuccess && <p>Your booking was successful!</p>}
            <form onSubmit={handleBooking}>
                <div>
                    <label>Name:</label>
                    <input
                        type="text"
                        value={customer}
                        onChange={(e) => setCustomer(e.target.value)}
                        required
                    />
                </div>
                <div>
                    <label>Email:</label>
                    <input
                        type="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        required
                    />
                </div>
                <div>
                    <label>Choose Slot:</label>
                    <select value={slot} onChange={(e) => setSlot(e.target.value)} required>
                        <option value="">Select a slot</option>
                        <option value="9:00 AM - 10:00 AM">9:00 AM - 10:00 AM</option>
                        <option value="10:00 AM - 11:00 AM">10:00 AM - 11:00 AM</option>
                        <option value="11:00 AM - 12:00 PM">11:00 AM - 12:00 PM</option>
                    </select>
                </div>
                <div>
                    <label>Status:</label>
                    <input
                        type="text"
                        value={status}
                        onChange={(e) => setStatus(e.target.value)}
                        placeholder="Enter Status (Optional)"
                    />
                </div>
                <button type="submit">Book Slot</button>
            </form>
        </div>
    );
};

export default BookingPage;
