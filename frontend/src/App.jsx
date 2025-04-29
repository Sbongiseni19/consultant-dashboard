// src/App.js

import React from "react";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import ConsultantDashboard from "./ConsultantDashboard";
import BookingPage from "./BookingPage"; // Import BookingPage

function App() {
    return (
        <Router>
            <Routes>
                <Route path="/" element={<ConsultantDashboard />} />
                <Route path="/book-slot" element={<BookingPage />} />
            </Routes>
        </Router>
    );
}

export default App;
