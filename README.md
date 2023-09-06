# Full Stack PaperGo Backend

## About

The PaperGo web app is a vibrant community platform designed for research enthusiasts from diverse fields. It serves as a collaborative hub where users can:

- **Share Research Experiences**: Celebrate your research milestones by sharing your accomplishments, such as published papers.
- **Post Discoveries**: Unveil your latest research discoveries and share materials, including intriguing papers that have sparked your interest.
- **User Authentication**: With secure login and logout functionalities, users can ensure their data is protected.
- **Interactive Playground**: Navigate through the app's playground to view recent discoveries, post new ones, edit existing entries, or even delete them if required. To enhance user experience, the platform also supports paginated viewing.
- **Robust Authorization**: Not all features are available to every user. The app employs a robust authorization mechanism ensuring only users with the right permissions can access specific functionalities.

The endpoints and how to send requests to these endpoints for products and items are described in the 'Endpoint Library' section of the README.

All endpoints need to be tested using curl or postman since there is no frontend for the app yet.

## Getting Started

### Installing Dependencies

#### Python 3.10.12

Follow instructions to install the latest version of python for your platform in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)

#### PIP Dependencies

In the root directory, run the following to install all necessary dependencies:

```bash
pip install -r requirements.txt
```

This will install all of the required packages.

##### Key Dependencies

- [Flask](http://flask.pocoo.org/) is a lightweight backend microservices framework. Flask is required to handle requests and responses.

- [SQLAlchemy](https://www.sqlalchemy.org/) is the Python SQL toolkit and ORM we'll use handle the lightweight sqlite database. You'll primarily work in app.py and can reference models.py.

- [Flask-CORS](https://flask-cors.readthedocs.io/en/latest/#) is the extension we'll use to handle cross origin requests from our frontend server.
  Alembic: A database migration tool for SQLAlchemy, helping in maintaining database schema changes over time.

- **Flask-Migrate**: Assists in handling SQLAlchemy-based database migrations for Flask apps using Alembic.

- **gunicorn**: A widely-used Python WSGI HTTP server, perfect for deploying Flask applications in a production setting.

- **psycopg2-binary**: The PostgreSQL adapter for Python, enabling seamless integration with PostgreSQL databases.

- **python-jose**: Implements JavaScript Object Signing and Encryption in Python, essential for JSON Web Token (JWT) handling.

- **Werkzeug**: A foundational WSGI utility library for Python web applications. It provides the tools needed to build a robust WSGI app.

## Running the server

We can now open the application via **Render** using the URL:
https://render-deployment-example-n2d0.onrender.com/ or https://render-deployment-example-n2d0.onrender.com/login for logging in

The live application can only be used to generate tokens via Auth0, the endpoints have to be tested using curl or Postman using the token since I did not build a frontend for the application.

## DATA MODELING:

#### models.py

The schema for the database and helper methods to simplify API behavior are in models.py:

- **Tables**:

  - There are three main tables created: Paper, User, and Discovery.
  - The Paper table stores details about research papers, including attributes like title, abstract, and publication year.
  - The User table keeps track of the users, possibly authors or individuals interested in various papers.
  - The Discovery table, though not explicitly detailed in the provided snippet, seems to store new research discoveries or findings.

- **Relationships**:
  - The Paper table has a many-to-many relationship with the User table, which represent authors or contributors to the papers.
  - Similarly, the Discovery table also establishes a many-to-one relationship with the User table, indicating users who post new discoveries.
  - The paper table shares a one-to-many relationship with the Discovery table.

Each table is equipped with helper functions for insert, update, delete, and format operations, ensuring a smooth interaction with the database.

## API ARCHITECTURE AND TESTING

### Endpoint Library

@app.errorhandler decorators were used to format error responses as JSON objects. Custom @requires_auth decorator were used for Authorization based
on roles of the user. Two roles are assigned to this API: 'user' and 'premiumer'. The 'user' role is assigned by default when someone creates an account from the login page, while the 'premiumer' role is already pre-assigned to certain users.

A token needs to be passed to each endpoint.
The following only works for /products endpoints:
The token can be retrived by following these steps:

1. Go to https: https://render-deployment-example-n2d0.onrender.com/login
2. Enter any credentials into the Auth0 login page. The role is automatically assigned by Auth0.
   Alternatively, sample account that has already been created can be used:
   Email: test@user1.com
   Password: ASDqwe123

### Running the App Locally

##### 1. Set yo the directory

You are assumed to already be in the root directory of the project.

##### 2. Create a virtual environemnt

```
python3 -m venv myenv
source myenv/bin/activate
```

##### 3. Set up the environment variables

```
# Sets environment variables and sample database
chmod +x setup.sh
source setup.sh
echo $TEST_JWT_TOKEN
```

#### 4. Install dependencies

```
pip install -r requirements.txt
```

#### 5. Run the app

```
python3 app.py
```

### Testing Endpoints

#### Populate database with sample data

```
psql -U postgres -d capstone -a -f sample_data.psql
```

#### 1. GET '/'

This is the root URL of the API and directs users to go to the login page.

```
# Sample curl Request:
curl -i http://localhost:5000/
```

#### 2. GET '/login'

Redirects to an Auth0 login page.

```
# Sample curl Request:
curl -i http://localhost:5000//login
```

#### 3. GET '/logout'

A placeholder for the logout functionality.

```
# Sample curl Request:
curl -i http://localhost:5000/logout
```

#### 4. GET '/playground'

Returns the discoveries in the system, ordered by the date posted.

```
# Sample curl Request:
curl -i -H "Content-Type: application/json" -H "Authorization: Bearer $TEST_JWT_TOKEN" http://127.0.0.1:5000/playground
# make sure you have run the setup.sh to set up the env variables
```

#### 5. GET '/user/{int:id}'

Returns user information for a specified user ID.

```
# Sample curl Request:
curl -i -H "Content-Type: application/json" -H "Authorization: Bearer $TEST_JWT_TOKEN" http://127.0.0.1:5000/user/1
```

Sample Output

```
{
  "success": true,
  "user": {
    "authored_papers": [
      2,
      4,
      6
    ],
    "current_project": "Current project description for User 1",
    "email": "user.1@example.com",
    "fields": null,
    "id": 1,
    "institution": "MIT",
    "looking_for_collaborators": true,
    "name": "User 1"
  }
}
```

#### 6. POST '/playground/create'

Creates a new discovery.

```
# Sample curl Request:
curl -i -X POST -H "Content-Type: application/x-www-form-urlencoded" -H "Authorization: Bearer $TEST_JWT_TOKEN" -d "caption=SampleCaption&paper_title=SampleTitle&paper_link=www.samplelink.com" http://localhost:5000/playground/create
```

Sample Output

```
{
  "new_discovery": {
    "caption": "SampleCaption",
    "date_posted": "Thu, 24 Aug 2023 23:38:33 GMT",
    "id": 13,
    "paper": {
      "abstract": "",
      "authors": [],
      "id": 11,
      "link": "www.samplelink.com",
      "publish_year": "",
      "title": "SampleTitle"
    },
    "user_name": "User 1"
  },
  "success": true
}
```

#### 7. POST '/playground/search'

Searches for discoveries that include the given search term in their associated paper titles.

```
# Sample curl Request:
curl -i -X POST -H "Content-Type: application/x-www-form-urlencoded" -H "Authorization: Bearer $TEST_JWT_TOKEN" -d "search_term=Title" http://localhost:5000/playground/search
```

Sample Output

```
{
  "current_page": 1,
  "discoveries": [
    {
      "caption": "SampleCaption",
      "date_posted": "Thu, 24 Aug 2023 23:38:33 GMT",
      "id": 13,
      "paper": {
        "abstract": "",
        "authors": [],
        "id": 11,
        "link": "www.samplelink.com",
        "publish_year": "",
        "title": "SampleTitle"
      },
      "user_name": "User 1"
    }
  ],
  "success": true,
  "total_discoveries": 1
}
```

#### 8. PATCH 'playground/edit/{int:discovery_id}'

Updates the caption of a discovery by its ID.

```
# Sample curl Request:
curl -i -X PATCH -H "Content-Type: application/x-www-form-urlencoded" -H "Authorization: Bearer $TEST_JWT_TOKEN" -d "caption=NewCaption" http://localhost:5000/playground/edit/1
```

Sampe Output

```
{
  "discovery": {
    "caption": "NewCaption",
    "date_posted": null,
    "id": 1,
    "paper": {
      "abstract": "Abstract for Sample Paper 1",
      "authors": [
        6,
        10,
        4,
        2,
        8
      ],
      "id": 1,
      "link": "http://example.com/paper1",
      "publish_year": "2020",
      "title": "Sample Paper 1"
    },
    "user_name": "User 2"
  },
  "success": true
}
```

#### 9. DELETE '/playground/delete/{int:discovery_id}'

Deletes a discovery by its ID.

```
# Sample curl Request:
curl -i -X DELETE -H "Authorization: Bearer $TEST_JWT_TOKEN" http://localhost:5000/playground/delete/2
```

Sample Output:

```
{
  "deleted": 2,
  "success": true
}
```

## Testing

There are 18 unittests in test_app.py. To run this file use:

```
# sample database has already been set up
python test_capstone.py

```

The tests include one test for expected success and error behavior for each endpoint, and tests demonstrating role-based access control,
where all endpoints are tested with and without the correct authorization.

## THIRD-PARTY AUTHENTICATION

#### auth.py

Auth0 is set up and running. The following configurations are in a .env file which is exported by the app:

- The Auth0 Domain Name
- The JWT code signing secret
- The Auth0 Client ID
  The JWT token contains the permissions for the 'user' and 'premiumer' roles.

As specified above, there are two roles created for this application, 'user' and 'premiumer'. 'premiumer' simply refers to premium users who have the additional right to delete their discoveries(posts) in the playground. Below are detailed information regarding their corresponding permissions.

**user**

- get:discoveries: view the posts in the playground
- get:user: view users' profile page
- post:discovery: create post
- search:discoveries: search for paper titles
- patch:discovery: edit posts

**premiumer**

- get:discoveries: view the posts in the playground
- get:user: view users' profile page
- post:discovery: create post
- search:discoveries: search for paper titles
- patch:discovery: edit posts
- delete:discovery: delete published posts

## DEPLOYMENT

The app is hosted live on heroku at the URL:
https://render-deployment-example-n2d0.onrender.com

**Note**
To create JWT token, you have to visit the Login Page at:
https://render-deployment-example-n2d0.onrender.com/login

However, there is no frontend for this app yet, and it can only be presently used to authenticate using Auth0 by entering
credentials and retrieving a fresh token to use with curl or postman.
