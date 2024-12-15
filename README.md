# Running the Dash Project

This guide explains how to set up and run the Dash project located in the `app.py` file and provides the link where the application will be accessible once the server is running.

---

## Prerequisites

Ensure you have the following installed on your system:

1. **Python (>=3.7)**

    - Verify installation:
        ```bash
        python --version
        ```

2. **Pip** (Python package installer)

    - Verify installation:
        ```bash
        pip --version
        ```

3. **Virtual Environment (Optional but Recommended)**
    - Install virtualenv if not already installed:
        ```bash
        pip install virtualenv
        ```

---

## Steps to Run the Project

### 1. Clone the Repository

If the project is in a Git repository, clone it to your local machine:

```bash
git clone <repository-url>
cd <repository-folder>
```

### 2. Set Up a Virtual Environment (Optional)

To isolate the project dependencies:

```bash
virtualenv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Required Packages

Manually install the following dependencies:

```bash
pip install dash plotly pandas numpy dash-bootstrap-components
```

### 4. Run the Application

To start the Dash application, run the `app.py` file:

```bash
python app.py
```

---

## Viewing the Application

Once the server starts successfully, the application will be available at the following URL:

```
http://127.0.0.1:8050
```

Open this link in your web browser to view the application.

If you are running the application on a remote server, replace `127.0.0.1` with your server's IP address or hostname.

---

## Notes

-   If you make changes to the code in `app.py`, the server will auto-reload, and the changes will reflect on refreshing the browser.
-   For deployment to a production environment, consider using services like **Heroku**, **AWS**, or **Google Cloud Platform**.



https://github.com/user-attachments/assets/4b54b8df-a473-47c3-ab2f-63467fe17034


