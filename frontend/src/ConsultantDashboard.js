// src/ConsultantDashboard.js (Frontend)

import React, { useEffect, useState } from "react";
import { io } from "socket.io-client";

const socket = io("http://127.0.0.1:8000/ws");

const ConsultantDashboard = () => {
    const [bookings, setBookings] = useState([]);

    useEffect(() => {
        socket.on("new-booking", (data) => {
            setBookings((prevBookings) => [...prevBookings, data]);
        });

        return () => socket.off("new-booking");
    }, []);

    return (
        <div>
            <h1>Consultant Dashboard</h1>
            <h2>New Bookings</h2>
            <ul>
                {bookings.map((booking, index) => (
                    <li key={index}>
                        {booking.customer} - {booking.slot}
                    </li>
                ))}
            </ul>
        </div>
    );
};

export default ConsultantDashboard;
