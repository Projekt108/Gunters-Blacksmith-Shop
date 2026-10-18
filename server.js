//Sets up the Express server
//We use this to handle requests, routing, etc
//Needed to handle user inputs and interactions with the page

//Setting up constants and imports
const express = require('express');
const app = express();
const PORT = 3000;
const cors = require('cors');
const fs = require('fs');
const path = require('path');

//Finds the path to the orders.json file
const ORDERS_FILE = path.join(__dirname, 'data/orders.json');

//Makes sure the server can see the whole file structure and use everything
app.use(cors());
app.use(express.json()); //Converts the json string order to JS object
app.use(express.static('public'));


//-----All the helper functions-----


//Reads the json file and parses it into an array
function readOrders() {
    try {
        //Actually goes and reads the data file
        const data = fs.readFileSync(ORDERS_FILE, 'utf-8');
        return JSON.parse(data); //Turns the text string back into JS array
    }
    catch (error) {
        //The try catch handles edge cases where the file doesn't exist for example
        return [];
    }
}

//Takes in the order as an argument and uses that to write to the file
function writeOrders(orders) {
    fs.writeFileSync(ORDERS_FILE, JSON.stringify(orders, null, 2));
}



//-----All the routes-----
//(There's three; GET, POST, PUT)


//GETs all the orders
app.get('/api/orders', (req, res) => {
    const orders = readOrders();
    res.json(orders);
});

//POSTs a new order to the orders.json
app.post('/api/orders', (req, res) => {
    //Creates a new order with these parameters
    const {customerName, items} = req.body;

    //Handles the edge cases in case some of these don't exist
    if (!customerName || !Array.isArray(items) || items.length === 0) {
        return res.status(400).json({error: 'Missing the customer name or items'});
    }
    
    const orders = readOrders(); //Calls the helper function above

    //Default constructor for the new orders
    const newOrder = {
        id: Date.now(), //Assigns a unique id based on the time sent
        customerName: customerName,
        items: items,
        status: "Getting Materials",
        timestamp: new Date().toISOString()
    };

    orders.push(newOrder);
    writeOrders(orders);

    res.status(201).json(newOrder);
});

//PUTs (Basically advances) the status of an order
app.put('/api/orders/:id', (req, res) => {
    const orders = readOrders();
    const orderId = parseInt(req.params.id);
    const order = orders.find(order => order.id === orderId);

    //Handles edge case where if the order wasn't found
    if (!order) {
        return res.status(404).json({error: 'Order was not found'});
    }

    //Moves the order to the next stage
    //There's probably a better way to do this but it works ig
    if (order.status === "Getting Materials") {
        order.status = "Forging";
    }
    else if (order.status === "Forging") {
        order.status = "Packing";
    }
    else if (order.status === "Packing") {
        order.status = "Done";
    }

    writeOrders(orders);
    res.json(order);
})



//Sets up the actual Express server
//We prob will need to change the () to 0.0.0.0 later when using the Pi
//Took waaay too long to figure out it has to be placed at the end of the file
app.listen(PORT, () => {
    console.log(`Server running on port ${PORT}`);
});