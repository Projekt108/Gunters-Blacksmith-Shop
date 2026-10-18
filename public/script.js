let selectedItemId = null;

//You guys can adjust any of these values, I just added temporary ones for testing
const ITEM_DATA = {
    "sword": {
        name: "Sword",
        price: 10,
        time: 15
    },

    "armor": {
        name: "Armor",
        price: 20,
        time: 30
    },

    "chainmail": {
        name: "Chainmail",
        price: 30,
        time: 45
    },

    "cooking-pot": {
        name: "Cooking Pot",
        price: 40,
        time: 60
    }
};

//Gets all the dialog elements and buttons on the page
//Lets us know what was interacted with
const dialog = document.getElementById('item-dialog');
const dialogTitle = document.getElementById('dialog-title');
const dialogPrice = document.getElementById('dialog-price');
const dialogTime = document.getElementById('dialog-time');
const closeDialogBtn = document.getElementById('close-dialog-btn');
const confirmOrderBtn = document.getElementById('confirm-order-btn');
const customerNameInput = document.getElementById('customer-name');
const itemButtons = document.querySelectorAll('.item');

//Loops through every single clickable item button on page
itemButtons.forEach(button => {
    button.addEventListener('click', () => {
        //Gets the id of the item
        const itemId = button.dataset.item;
        selectedItemId = itemId;
        //Finds the item in the ITEM_DATA object at the top
        const itemInfo = ITEM_DATA[itemId];
        
        //Updates the dialog text with the real info
        dialogTitle.textContent = itemInfo.name;
        dialogPrice.textContent = "Price: $" + itemInfo.price;
        dialogTime.textContent = "Time: " + itemInfo.time + " mins";
        
        //Actually shows the dialog
        dialog.classList.remove('dialog-hidden');
    });
});

//Runs when the cancel button is pressed
closeDialogBtn.addEventListener('click', () => {
    dialog.classList.add('dialog-hidden'); // Hides the thing
    customerNameInput.value = ''; // Clear the name input field
});


//This runs after clicking place order in the popup dialog
confirmOrderBtn.addEventListener('click', async () => {
    //Gets the name from the input
    const customerName = customerNameInput.value.trim();

    //Handles edge case in case they didn't type their name
    if (customerName === "") {
        alert("Please enter your name!");
        return;
    }

    //Gets the name of the item from the ITEM_DATA object up top
    const itemName = ITEM_DATA[selectedItemId].name;

    //Formats the data to send properly to the backend server.js
    const orderData = {
        customerName: customerName,
        items: [itemName]
    };

    //Sends the POST request
    const response = await fetch('/api/orders', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(orderData)
    });

    if (response.ok) {
        //Hides the dialog and clear the input if all is well
        dialog.classList.add('dialog-hidden');
        customerNameInput.value = '';
        
        //Refreshes the queue so that the new order shows up and is actually visible
        fetchOrders(); 
    } else {
        //Welp something went wrong
        alert("Failed to place order.");
    }
});

//Need to make this function
function fetchOrders() {

}