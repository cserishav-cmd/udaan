# **Udaan \- Campus Wellness Companion: Setup Guide**

This guide provides step-by-step instructions to set up and run the Udaan web application on a local machine for the HackOverflow 9.0 hackathon.

## **Prerequisites**

Before you begin, ensure you have the following software installed:

1. **XAMPP**: This will be used as the local server environment for Apache and MySQL.  
   * [Download XAMPP](https://www.apachefriends.org/index.html)  
2. **Python**: The application is built using Python.  
   * [Download Python](https://www.python.org/downloads/) (Ensure Python and Pip are added to your system's PATH during installation).

## **Step 1: Place the Project Files**

1. **Extract Project**: Unzip the provided project file.  
2. **File Destination**: Move the extracted folder into your XAMPP htdocs directory. The final path for your project should be:  
   * **Main Project Folder**: C:\\xampp\\htdocs\\HackOverFlow9.0  
   * This means your app.py file should be located at C:\\xampp\\htdocs\\HackOverFlow9.0\\app.py.

## **Step 2: Set Up the Database with XAMPP**

1. **Start XAMPP**: Open the XAMPP Control Panel and start the **Apache** and **MySQL** modules. They should both turn green.  
2. **Create the Database**:  
   * Open your web browser and go to http://localhost/phpmyadmin/.  
   * Click on **New** in the left sidebar.  
   * Enter the database name as udaan\_db and click **Create**.  
3. **Import the Database**:  
   * After creating the database, select udaan\_db from the list on the left.  
   * Click on the **Import** tab at the top of the page.  
   * Click "Choose File" and select the udaan\_db.sql file provided in the project zip.  
   * Click the **Go** button at the bottom of the page to start the import.

## **Step 3: Configure the Project Environment**

1. **Install Python Libraries**:  
   * Open a command prompt (cmd) or terminal.  
   * Navigate to your project directory using the cd command:  
     cd C:\\xampp\\htdocs\\HackOverFlow9.0

   * Install all required Python libraries by running this command:  
     pip install \-r requirements.txt

2. **Configure Environment Variables (API Keys)**:  
   * In the project folder (C:\\xampp\\htdocs\\HackOverFlow9.0), create a new file named .env.  
   * Open this .env file with a text editor and add the following lines. You must replace "YOUR\_API\_KEY\_HERE" with your actual API keys.  
     \# Google Gemini API Key for AI Chatbot  
     GEMINI\_API\_KEY="YOUR\_GEMINI\_API\_KEY\_HERE"

     \# Pinecone API Key (if used for vector storage)  
     PINECONE\_API\_KEY="YOUR\_PINECONE\_API\_KEY\_HERE"

     \# Twilio Credentials for Emergency Calls  
     TWILIO\_ACCOUNT\_SID="YOUR\_TWILIO\_ACCOUNT\_SID\_HERE"  
     TWILIO\_AUTH\_TOKEN="YOUR\_TWILIO\_AUTH\_TOKEN\_HERE"  
     TWILIO\_PHONE\_NUMBER="YOUR\_TWILIO\_PHONE\_NUMBER\_HERE"  
     EMERGENCY\_PHONE\_NUMBER="THE\_PHONE\_NUMBER\_TO\_CALL\_IN\_EMERGENCY"

## **Step 4: Run the Application**

1. **Ensure XAMPP is still running** (Apache and MySQL).  
2. In your command prompt or terminal, make sure you are in the project directory:  
   cd C:\\xampp\\htdocs\\HackOverFlow9.0

3. Run the main application file with Python:  
   python app.py

4. The terminal will show that the server is running, likely on http://127.0.0.1:8080.  
5. Access the Application: Open your web browser and go to:  
   http://127.0.0.1:8080

## **Login Credentials**

You can use these pre-defined accounts to test the application:

* **Student Login**:  
  * **Email**: swarnil@gmail.com  
  * **Password**: 0000  
* **Admin Login**:  
  * **Email**: fit@gmail.com  
  * **Password**: 0000

## **Troubleshooting**

* **Database Connection Error**: If you see an error related to the database, double-check that MySQL is running in XAMPP and that you successfully imported the udaan\_db.sql file into a database named udaan\_db.  
* **"No module named 'flask'" (or other library)**: This error means the Python libraries were not installed. Please re-run the pip install \-r requirements.txt command from Step 3.1.  
* **Facial Recognition Errors**: The facial analysis feature requires a webcam. Ensure you grant permission if your browser prompts for camera access.