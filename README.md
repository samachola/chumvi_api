# Chumvi-FlaskAPI
<a class="badge-align" href="https://www.codacy.com/app/samachola/chumvi_api?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=samachola/chumvi_api&amp;utm_campaign=Badge_Grade"><img src="https://api.codacy.com/project/badge/Grade/8798ea6e9fbe4958bf3feb52e3c53981"/></a><a href='https://coveralls.io/github/samachola/chumvi_api'><img src='https://coveralls.io/repos/github/samachola/chumvi_api/badge.svg?branch=develop' alt='Coverage Status'/></a><a href='https://travis-ci.org/samachola/chumvi_api'><img src='https://travis-ci.org/samachola/chumvi_api.svg?branch=develop' alt='Build Status' /></a><a href="https://codeclimate.com/github/samachola/chumvi_api/maintainability"><img src="https://api.codeclimate.com/v1/badges/142de535e6bed3e16354/maintainability" /></a>



A Flask Based REST API that enables clients to do the following:

- Register, login and manage their account.
- Create, update, view and delete a category.
- Create, update, view or delete recipes.


## Prerequisites

Python 2.6 or a later version

## Dependencies
Install all package requirements in your python virtual environment.
```
pip install -r requirements.txt
```
## Env
Rename .env.sample into .env

## Virtual environment
Activate virtual environment:

```
$ source .venv/bin/activate
```

## Testing
To set up unit testing environment:

```
$ pip install nose
```

To execute a test file:

```
$ source .env
$ nosetests
```

## Testing API

*Note* After user login, ensure you  specify the generated token in the header:

- In postman header **key** : `x-access-token` **value** : <token>
- While testing on the browser, key in the `<token>` in Authorize header.

## Initialize the database
You need to initialize database and tables by running migrations.

```
flask db init

flask db migrate

flask db upgrade

```

## Start The Server
Start the server which listens at port 5000 by running the following command:
```
python app.py

```
## Pagination

The API enables pagination by passing in *page* and *limit* as arguments in the request url as shown in the following example:

```
http://127.0.0.1:5000/api-v0/recipe?page=1&limit=10

```

## Searching

The API implements searching based on the name using a GET parameter *q* as shown below:

```
http://127.0.0.1:5000/api-v0/recipe?q=example

```

### Api endpoints

| url | Method|  Description| Authentication |
| --- | --- | --- | --- |
| /api-v0/auth/register | POST | Registers new user | FALSE
| /api-v0/auth/login | POST | Handles POST request for /auth/login | TRUE
| /api-v0/category | GET | Get every category of logged in user|TRUE
| /api-v0/category/ | GET | Gets the list of categories |TRUE
| /api-v0/category | POST | Create a new category|TRUE
| /api-v0/category/{category_id}  | PUT | Update a category|TRUE
| /api-v0/category/{category_id} | DELETE | Delete category by id|TRUE
| /api-v0/recipe | POST | Creates a recipe|TRUE
| /api-v0/recipe | GET | Gets all recipes
| /api-v0/recipe/{id} | GET | Gets a single recipe|TRUE
| /api-v0/recipe/{id} | PUT | Updates a single recipe|TRUE
| /api-v0/recipe/{id} | DELETE | Deletes a single recipe|TRUE