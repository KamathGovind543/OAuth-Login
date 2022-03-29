
# Project Title

Google Authentication and Microsoft Authentication.

---

Language - Pyhton

Frmaework - Flask

---


## Documentation for Google Auth
Integrating Google Auth and  Microsoft Auth with python web Application.

This sample shows how to build a Python web app using Flask and Autlib Library,
that signs in a user, and get access to Google Login.

Create Google Oauth Credentilas

1. Create Google Auth Credentials website Login
[Click here for Documentaion](https://www.balbooa.com/gridbox-documentation/how-to-get-google-client-id-and-client-secret)

2. Also Create a Database model for the Datastorage of the user
---
Sqlite 
---

In this sample sqlite database is been used u can use different database also to create a model.


## Documentaion for creating Microsoft Azzure AD Tenant

As a first step you'll need to:

1. Sign in to the [Azure portal](https://portal.azure.com) using either a work or school account or a personal Microsoft account.
1. If your account is present in more than one Azure AD tenant, select your profile at the top right corner in the menu on top of the page, and then **switch directory**.
   Change your portal session to the desired Azure AD tenant.

#### Register the Python Webapp (python-webapp)

1. Navigate to the Microsoft identity platform for developers [App registrations](https://go.microsoft.com/fwlink/?linkid=2083908) page.
1. Select **New registration**.
1. When the **Register an application page** appears, enter your application's registration information:
   - In the **Name** section, enter a meaningful application name that will be displayed to users of the app, for example `python-webapp`.
   - Change **Supported account types** to **Accounts in any organizational directory and personal Microsoft accounts (e.g. Skype, Xbox, Outlook.com)**.
   - In the Redirect URI (optional) section, select **Web** in the combo-box and enter the following redirect URIs: `http://localhost:5000/getAToken`.
1. Select **Register** to create the application.
1. On the app **Overview** page, find the **Application (client) ID** value and record it for later. You'll need it to configure the Visual Studio configuration file for this project.
1. Select **Save**.
1. From the **Certificates & secrets** page, in the **Client secrets** section, choose **New client secret**:

   - Type a key description (of instance `app secret`),
   - Select a key duration of either **In 1 year**, **In 2 years**, or **Never Expires**.
   - When you press the **Add** button, the key value will be displayed, copy, and save the value in a safe location.
   - You'll need this key later to configure the project in Visual Studio. This key value will not be displayed again, nor retrievable by any other means,
     so record it as soon as it is visible from the Azure portal.
1. Select the **API permissions** section
   - Click the **Add a permission** button and then,
   - Ensure that the **Microsoft APIs** tab is selected
   - In the *Commonly used Microsoft APIs* section, click on **Microsoft Graph**
   - In the **Delegated permissions** section, ensure that the right permissions are checked: **User.ReadBasic.All**. Use the search box if necessary.
   - Select the **Add permissions** button

### Step 3:  Configure the sample to use your Azure AD tenant

In the steps below, "ClientID" is the same as "Application ID" or "AppId".

#### Configure the pythonwebapp project

> Note: if you used the setup scripts, the changes below may have been applied for you

1. Open the `app_config.py` file
1. Find the app key `Enter_the_Tenant_Name_Here` and replace the existing value with your Azure AD tenant name.
1. You saved your application secret during the creation of the `python-webapp` app in the Azure portal.
   Now you can set the secret in environment variable `CLIENT_SECRET`,
   and then adjust `app_config.py` to pick it up.
1. Find the app key `Enter_the_Application_Id_here` and replace the existing value with the application ID (clientId) of the `python-webapp` application copied from the Azure portal.

## Deployment

To deploy this project run

```bash
pip install -r requirements.txt
```

### Step 4: Run the sample

- You will need to install dependencies using pip as follows:
```Shell
$ pip install -r requirements.txt
```

Run app.py from shell or command line. Note that the host and port values need to match what you've set up in your redirect_uri:

```Shell
$ flask run --host localhost --port 5000
```

Thank You