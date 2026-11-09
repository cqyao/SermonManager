Sermon Manager allows for an easy but visually appealing way to upload sermons online. It includes many important features like compiling sermons into different series, categorising them by topic or book, and filtering by the speaker. 

Sermon Manager is built on Flask for the backend, HTML and Javascript for the frontend, and Supabase handling the database and storage. This makes for an easy, modifiable system with the possibility of upgrades in the future in mind.

Have a look at the website [here](https://freebaptistchurch.au)

**Technologies Used**

<img width="100" height="100" alt="image" src="https://github.com/user-attachments/assets/bd5057af-94b8-4722-87ea-a07cc4c9e59e" />
<img width="100" height="100" alt="image" src="https://github.com/user-attachments/assets/95687007-e3c8-4842-a9d4-3d6fd25d9fde" />
<img width="100" height="100" alt="image" src="https://github.com/user-attachments/assets/499efd07-53e2-49bf-87ec-30ea992c57bb" />

_There are three branches in the repo: dev, test, and main. When implementing a new feature, use the 'dev' branch until ready to be tested. Then, move to 'test'. Once, the feature has been fully tested, commit changes to 'main'._

## Local Python environment

Install the app dependencies after creating the environment:

```shell
python -m pip install -r requirements.txt
```

In VS Code, select the interpreter inside `.venv` once on each machine. The workspace default points to `.venv`, and each OS resolves the platform-specific executable.

## GitHub Actions Workflow
The repo includes a GitHub Action that automates CI/CD processes. The Action checks for any changes from the specified remote branch and then pulls those changes. Next, the virtualenv is activated, requirements are installed from the requirements file, and a POST request is sent to PythonAnywhere to reload the web app. 
While the Action does work, it is limited by needing to keep a BASH console open on PythonAnywhere. If the deployment fails, it's likely that the BASH console isn't open and active. To my knowledge, PythonAnywhere closes any console not on an active browser tab which isn't a problem if you're actively developing but it adds an extra step for infrequent deployments.
