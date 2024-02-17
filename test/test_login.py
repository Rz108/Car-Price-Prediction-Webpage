import sys
import os
from datetime import datetime
import pytest
import json
from flask import json, session
from werkzeug.security import generate_password_hash, check_password_hash

# Validity testing 
## to see if one is able to log in
@pytest.mark.usefixtures("add_base_users")
@pytest.mark.parametrize(
    "userlist",
    [
        ["email1@gmail.com", "jas"],
        ["email2@gmail.com", "jas"],  
    ],
)
def test_user_login_api(client, userlist, capsys):
    with capsys.disabled():
        with client:
            data = {
                "email": userlist[0],
                "password": userlist[1],
            }

            response = client.post(
                "/api/login", data=json.dumps(data), content_type="application/json"
            )
            response_body = json.loads(response.get_data(as_text=True))
            print(response_body)
            assert response.status_code == 200
            assert response.headers["Content-Type"] == "application/json"
            assert response_body["email"] == userlist[0]

            with client.session_transaction() as sess:
                assert sess["user_id"] == response_body["id"]

# Expected Failure Testing
## to see if one is able to log in with invalid credentials
@pytest.mark.xfail(reason="Invalid login credentials")
@pytest.mark.parametrize(
    "userlist",
    [
        ["test@example.com", "jasss"],
        ["test1@example.com", "jasss"],
    ],
)
def test_user_fail_login_api(client, userlist, capsys):
    test_user_login_api(client, userlist, capsys)
