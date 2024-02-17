import pytest
import json

# Validity testing
## Check on the link whether it is able to pass the test and the status code
@pytest.mark.parametrize(
    "links",
    [
        ("/useless", 404),
        ("/", 200),
        ("/login", 200),
        ("/register", 200),
        ("/predict", 401),  
        ("/api/predict", 405),  
        ("/api/login", 405),
        ("/api/register", 405),
    ],
)
def test_links(client, links):
    link, code = links
    response = client.get(link)
    assert response.status_code == code

# Validity testing 
## to see if the links after loggin
@pytest.mark.usefixtures('logged_in_client')
@pytest.mark.parametrize(
    "links",
    [
        ("/useless", 404),
        ("/", 200),
        ("/login", 200),  
        ("/register", 200), 
        ("/predict", 200),  
        ("/api/predict", 405),  
        ("/api/login", 405),
        ("/api/register", 405),
    ],
)
def test_logged_in_links(client, links):
    link, code = links
    response = client.get(link)
    assert response.status_code == code