//Sets up the Express server
//We use this to handle requests, routing, etc
//Needed to handle user inputs and interactions with the page
const express = require('express');
const app = express();
const PORT = 3000;

app.use(express.static('public'));

app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});