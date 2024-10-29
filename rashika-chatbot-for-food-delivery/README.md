# Project Structure
===================
- **backend**: Contains Python FastAPI backend code.
- **db**: Contains the dump of the database. You need to import this into your MySQL database using MySQL Workbench or the command line.
- **dialogflow_assets**: Contains training phrases and other resources for our intents.


# Install Required Modules
==========================
To install the necessary modules, run:

```bash
pip install mysql-connector
pip install "fastapi[all]"
```

OR, to install all dependencies at once, run:

```bash
pip install -r backend/requirements.txt
```

# Start FastAPI Backend Server
================================
1. Navigate to the **backend** directory in your terminal:
   ```bash
   cd backend
   ```
2. Run the following command to start the FastAPI server:
   ```bash
   uvicorn main:app --reload
   ```

# Ngrok for HTTPS Tunneling
=======================================
## Ubuntu
1. To install Ngrok, run the following commands:
   ```bash
   wget https://bin.equinox.io/c/111111/ngrok-stable-linux-amd64.zip # Adjust the link to the latest version if needed
   unzip ngrok-stable-linux-amd64.zip
   sudo mv ngrok /usr/local/bin
   ```

2. Open a terminal and run the following command to start Ngrok:
   ```bash
   ngrok http 8000
   ```

**NOTE**: Ngrok can timeout. If you see a "session expired" message, you will need to restart the Ngrok session.

---

## Windows
1. To install Ngrok, go to [Ngrok Download Page](https://ngrok.com/download) and download the version suitable for your OS.
2. Extract the zip file and place `ngrok.exe` in a folder.
3. Open Command Prompt, navigate to that folder, and run the following command:
   ```bash
   ngrok http 8000
   ```

**NOTE**: Ngrok can timeout. If you see a "session expired" message, you will need to restart the Ngrok session.
