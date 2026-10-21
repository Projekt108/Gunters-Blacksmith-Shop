# Gunters-Blacksmith-Shop
Java Beans submission for Kansas University's High School Design Competition 2026 for Computer Science

Link to competition website: https://engr.ku.edu/high-school-design-competition 

A web-based blacksmith shop app built with Python, Flask, HTML, CSS, and Jinja2. Browse items, add products to a cart, and submit orders to the queue with the shop's ordering system. 

## Feature List 
- Staff page with login requirements
- Staff order management
- Client communications pathways to staff members
- Removing cart items and subtotals
- Live queue for customer orders
- About us page
- Additional shop items

## Prerequisites

Install the following before running the project:

- **Python 3.11 or newer:** [Download Python](https://www.python.org/downloads/)


## Installation

### 1. Clone the repository

Download the project as a ZIP by clicking Code -> Download ZIP, then extract the files. 



### 2. Install Python dependencies

Open a new terminal in the project directory and run:

```bash
python -m pip install -r requirements.txt
```

This installs Flask and the other Python packages listed in `requirements.txt`.


## Running the Application

### 1. Start the app

In a terminal in the project folder, run:

```bash
python app.py
```
On Windows, you can also use:
```bash
py app.py
```

Flask should display a local development address in the terminal, for example:

`http://127.0.0.1:5000`

Open that address in your web browser.

### 2. Stop the app

Return to the terminal running the app and press `Ctrl+C`.


## Troubleshooting

**Python is not recognized**

On Windows, try `py` instead of `python`. If neither works, install Python and ensure it is available from your terminal.

**Missing Flask or other packages**

Activate the virtual environment and install dependencies again:

```bash
python -m pip install -r requirements.txt
```
## Usage Guide

### Customers
- Clicking items bring customers to the buy page
- Configure amount and send the item(s) to the cart
- Checkout provides customers with the subtotal and asks for customer information
- Customers can check order progress in the live queue
- Customers can contact staff through comments

### Staff
- Staff members enter login credentials at the staff login page
- Staff password is 'staff@123'
- Staff members can advance orders or clear the queue
- Staff members can view and delete customer comments

## Meet the Team
### Aryan Bhadule
Lead Frontend Developer
- Developed CSS and HTML 
- Implemented user interface and user flows
- Designed staff page and login

### Jerry Liu
Lead Backend Developer
- Developed Python functions
- Programmed Flask decorators
- Configued database for user data

### Soham Mukherjee
Lead Graphic Designer, Presentation Designer
- Created key graphic elements
- Designed website theming 
- Organized presentation materials 

### Zane Schrage
Frontend Developer, Lead Infrastructure Engineer
- Set up the web server on Raspberry Pi 5
- Configured the web server for http and https
- HTML and CSS planning