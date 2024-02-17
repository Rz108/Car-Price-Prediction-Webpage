import pytest
from datetime import datetime as dt
from flask import json, session
import time


def UniqueEmail(base_email):
    timestamp = time.time()
    return f"{base_email.split('@')[0]}_{timestamp}@{base_email.split('@')[1]}"

@pytest.mark.parametrize(
    "entrylist",
    [
        [f'username{time.time()}', UniqueEmail("email1@gmail.com"), "jas", "jas"],
        [f'username1{time.time()}', UniqueEmail("email2@gmail.com"), "jas", "jas"],
        # ['usernam1', "email1@gmail.com", "jas",'jas'],
        # ['username2',"email2@gmail.com", "jas",'jas'],
    ],
)
# Validity testing 
## to see if one is to add user
def test_add_user(client, entrylist, app_context):
    data = {
        'username': entrylist[0],
        "email": entrylist[1],
        "password": entrylist[2],
        "password1": entrylist[3]
    }

    # Make the POST request and get the response
    response = client.post("/api/register", json=data)  # Use json=data here
    assert response.status_code == 201, "Expected status code 201 but got {}".format(response.status_code)
    
    # Checking the Content-Type to be application/json
    assert response.headers["Content-Type"] == "application/json", "Content-Type should be application/json"
    
    # Get the JSON response body
    response_body = response.json  
    assert "id" in response_body, "User ID was not returned!"
    assert response_body["email"] == entrylist[1], "Returned email does not match up!"
    assert "joined_at" in response_body, "Joined At timestamp was not returned!"


# Expected failure testing
## Duplicated errors in database
@pytest.mark.usefixtures("add_base_users")
@pytest.mark.xfail(reason="Email Found in Database", strict=True)
@pytest.mark.parametrize(
    "entrylist",
    [
        ['James4',"test@example.com", "jas","jas"],
        ['James5',"test1@example.com", "jas","jas"],
    ],
)
def test_user_email_exist(client, entrylist, app_context):
    data = {
        'username': entrylist[0],
        "email": entrylist[1],
        "password": entrylist[2],
        "password1": entrylist[3]
    }

    response = client.post("/api/register", json=data) 

    assert response.status_code == 409, "Expected a 409 Conflict due to duplicate email"



