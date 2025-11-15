# python-flask-sso-example

An example Flask application demonstrating how to use the [WorkOS Python SDK](https://github.com/workos/workos-python) to authenticate users via **Single Sign-On (SSO)** and integrate with **Directory Sync**.

## Prerequisites

* Python 3.6+

---

## Flask Project Setup

1.  Clone the main git repo for these Python example apps using your preferred secure method (HTTPS or SSH).

    ```bash
    # HTTPS
    $ git clone [https://github.com/workos/python-flask-example-applications.git](https://github.com/workos/python-flask-example-applications.git)
    ```

    or

    ```bash
    # SSH
    $ git clone git@github.com:workos/python-flask-example-applications.git
    ```

2.  Navigate to the sso app within the cloned repo.

    ```bash
    $ cd python-flask-example-applications/python-flask-sso-example
    ```

3.  Create and source a Python virtual environment. You should then see `(env)` at the beginning of your command-line prompt.

    ```bash
    $ python3 -m venv env
    $ source env/bin/activate
    (env) $
    ```

4.  Install the cloned app's dependencies.

    ```bash
    (env) $ pip install -r requirements.txt
    ```

5.  Obtain and make note of the following values from your WorkOS Dashboard:

    * Your [WorkOS API key](https://dashboard.workos.com/api-keys)
    * Your [SSO-specific, WorkOS Client ID](https://dashboard.workos.com/configuration)
    * Your [Directory Sync-specific, WorkOS Client ID](https://dashboard.workos.com/configuration/directories)

6.  Ensure you're in the root directory for the example app, `python-flask-sso-example/`. Create a `.env` file to securely store the environment variables. Open this file with the Nano text editor. (This file is listed in this repo's `.gitignore` file, so your sensitive information will not be checked into version control.)

    ```bash
    (env) $ touch .env
    (env) $ nano .env
    ```

7.  Once the Nano text editor opens, directly edit the `.env` file by listing the environment variables:

    ```bash
    # --- Required for both SSO and Directory Sync ---
    WORKOS_API_KEY=<value found in step 5>
    APP_SECRET_KEY=<any string value you'd like>
    
    # --- SSO Specific ---
    WORKOS_CLIENT_ID=<Your SSO-specific Client ID from step 5>
    
    # --- Directory Sync Specific ---
    WORKOS_DS_CLIENT_ID=<Your Directory Sync-specific Client ID from step 5>
    ```

    To exit the Nano text editor, type `CTRL + x`. When prompted to "Save modified buffer", type `Y`, then press the `Enter` or `Return` key.

8.  Source the environment variables so they are accessible to the operating system.

    ```bash
    (env) $ source .env
    ```

    You can ensure the environment variables were set correctly by running the following commands. The output should match the corresponding values.

    ```bash
    (env) $ echo $WORKOS_API_KEY
    (env) $ echo $WORKOS_CLIENT_ID
    ```

9.  In `python-flask-sso-example/app.py`, change the `CUSTOMER_ORGANIZATION_ID` string value to the Organization ID you will be testing the login for. This can be found in your WorkOS Dashboard.

10. The final setup step is to start the server.

    ```bash
    (env) $ flask run
    ```

    If you are using macOS Monterey, port 5000 is often not available. You can start the app on a different port with this slightly different command:

    ```bash
    (env) $ flask run -p 5001
    ```

    Navigate to `localhost:5000`, or `localhost:5001` depending on which port you launched the server, in your web browser. You should see a "Login" button.

    You can stop the local Flask server for now by entering `CTRL + c` on the command line.

---

## SSO Setup with WorkOS

Follow the [SSO authentication flow instructions](https://workos.com/docs/sso/guide/introduction) to set up an SSO connection.

When you get to the step where you provide the `REDIRECT_URI` value, use **`http://localhost:5000/auth/callback`**.

### Testing the SSO Integration

11. Navigate to the `python-flask-sso-example` directory. Source the virtual environment we created earlier, if it isn't still activated, and start the Flask server locally.

    ```bash
    $ cd ~/Desktop/python-flask-sso-example/
    $ source env/bin/activate
    (env) $ flask run
    ```

    Once running, navigate to `localhost:5000` (or `localhost:5001`) to test out the SSO workflow.

---

## Directory Sync Setup with WorkOS

This example application also includes endpoints to demonstrate the Directory Sync flow, allowing you to synchronize users and groups from a customer's Identity Provider (IdP) directly to your application.

1.  **Create a Directory:** In your WorkOS Dashboard, go to the **Directory Sync** section and click "Add Directory." Select an IdP (e.g., Azure AD, Okta, or Mock Directory) and follow the steps to create a new Directory Connection.

2.  **Retrieve Connection ID:** Once the Directory Connection is created, note the **ID** (starts with `directory_...`).

3.  **Update `app.py`:** Open `python-flask-sso-example/app.py` and set the `CUSTOMER_DIRECTORY_ID` string value to the Directory Connection ID you just retrieved.

4.  **Test the Sync:**
    * **Listen for Events:** The app is configured to handle webhooks for Directory Sync events at `/webhooks/workos-directory-sync`. If you are using the Mock Directory, you can manually trigger events.
    * **View Directory Data:** Navigate to the `/directories` endpoint in your running application to fetch and display the users and groups from the connected directory.
---
## Video Walkthrough

![2025-11-14_13-17-11 (1)](https://github.com/user-attachments/assets/aa54a05b-1e24-4f08-b380-6670531ee0db)

