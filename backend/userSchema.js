const mongoose = require('mongoose');

// Define the user schema
const userSchema = new mongoose.Schema({
    username: {
        type: String,
        required: true,
        unique: true, // Ensures no two users have the same username
    },
    email: {
        type: String,
        required: true,
        unique: true, // Ensures no two users have the same email
    },
    password: {
        type: String,
        required: true,
    },
});

// Create the User model using the schema
const User = mongoose.model('User', userSchema);

// Export the model for use in other parts of the app
module.exports = User;
