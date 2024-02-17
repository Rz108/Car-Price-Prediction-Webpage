import sys
import os
from datetime import datetime
import pytest
import json
from application import app as ai_app
from application.models import Prediction

# Validty testing
## Test on whether i can add entry

@pytest.mark.usefixtures('logged_in_client')
@pytest.mark.usefixtures('add_base_users')
@pytest.mark.parametrize(
    'entrylist', [
        [2, 'Honda', 1980,2023-1980, 1.0, '2.5L I4 16V GDI DOHC Turbo', 2, '6-Speed Automatic', 'Gasoline', 'Four-wheel Drive', 3.0, 0, 1, 1, 0, 1, 40259.0],
        [2, 'Toyota', 2000,2023-2000, 1.0, '2.5L I4 16V GDI DOHC Turbo', 2, '6-Speed Automatic', 'Gasoline', 'Four-wheel Drive', 3.0, 0, 1, 1, 0, 1,  40259.0]

    ]
)

def test_Add(client, entrylist, capsys, app_context):
    with capsys.disabled():
        with client:
            with client.session_transaction() as sess:
                sess['user_id'] = entrylist[0] 

            data1 = dict(zip([
                'userid', 'brand','year','Age', 'mileage', 'engine', 'engine_size',
                'transmission', 'fuel_type', 'drivetrain', 'min_mpg', 'damaged', 'turbo',
                'navigation_system','backup_camera', 'first_owner', 'prediction'
            ], entrylist))

            response = client.post(f'/api/add/{entrylist[0]}', data=json.dumps(data1), content_type="application/json")
            
            print('Response status code:', response.status_code)
            print('Response data:', response.data)
            assert response.status_code == 200
            assert response.headers["Content-Type"] == "application/json"
            response_body = json.loads(response.get_data(as_text=True))
            assert response_body["id"]


# Range testing
## Check whether I can add user with less than 0 user id and invlaid user id
@pytest.mark.usefixtures('add_base_users', 'logged_in_client')
@pytest.mark.xfail(reason='Invalid User ID', strict=True)
@pytest.mark.parametrize(
    'entrylist', [
        [-1, 'Honda', 2010,2023-2010, 1.0, '2.5L I4 16V GDI DOHC Turbo', 2, '6-Speed Automatic', 
         'Gasoline', 'Four-wheel Drive', 3.0, 0, 1, 1, 0, 1, 0, 40259.0],
                 [-20, 'Honda', 2010,2023-2010, 1.0, '2.5L I4 16V GDI DOHC Turbo', 2, '6-Speed Automatic', 
         'Gasoline', 'Four-wheel Drive', 3.0, 0, 1, 1, 0, 1, 0, 40259.0]
    ]
)
def test_UserInvalid(client, entrylist, capsys, app_context):
    test_Add(client, entrylist, capsys, app_context)

# Validity testing
## Check whether i can add prediction
@pytest.mark.usefixtures("logged_in_client")
@pytest.mark.parametrize(
    'entrylist',[[
        1,'Honda',1970,2023-1970, 1.0, '2.5L I4 16V GDI DOHC Turbo',2
        ,'6-Speed Automatic','Gasoline','Four-wheel Drive',3.0,0,1.5,1,0,1,2000
    ],
    [        1,'Honda',2000,2023-2000, 1.0, '2.5L I4 16V GDI DOHC Turbo',2
        ,'6-Speed Automatic','Gasoline','Four-wheel Drive',3.0,0,1,1,0,1,20000]]
)

def test_PredictionEntry(entrylist,  capsys):
    with capsys.disabled():
        created = datetime.utcnow()
        new_row = Prediction(
            userid=entrylist[0],
            brand=entrylist[1],
            year=entrylist[2],
            age=entrylist[3],
            mileage=entrylist[4],
            engine=entrylist[5],
            engine_size=entrylist[6],
            transmission=entrylist[7],
            fuel_type=entrylist[8],
            drivetrain=entrylist[9],
            min_mpg=entrylist[10],
            damaged=entrylist[11],
            turbo=entrylist[12],
            navigation_system=entrylist[13],
            backup_camera=entrylist[14],
            first_owner = entrylist[15],
            predicted_on=created,
            prediction=entrylist[16]
        )


        assert new_row.userid == entrylist[0], "UserID mismatch"
        assert new_row.brand == entrylist[1], "Brand mismatch"
        assert new_row.year == entrylist[2], "Year mismatch"
        assert new_row.age == entrylist[3], "Age mismatch"
        assert new_row.mileage == entrylist[4], "Mileage mismatch"
        assert new_row.engine == entrylist[5], "Engine mismatch"
        assert new_row.engine_size == entrylist[6], "Engine size mismatch"
        assert new_row.transmission == entrylist[7], "Transmission mismatch"
        assert new_row.fuel_type == entrylist[8], "Fuel type mismatch"
        assert new_row.drivetrain == entrylist[9], "Drivetrain mismatch"
        assert new_row.min_mpg == entrylist[10], "Min MPG mismatch"
        assert new_row.damaged == entrylist[11], "Damaged mismatch"
        assert new_row.turbo == entrylist[12], "Turbo mismatch"
        assert new_row.navigation_system == entrylist[13], "Navigation system mismatch"
        assert new_row.backup_camera == entrylist[14], "Backup camera mismatch"
        assert new_row.first_owner == entrylist[15], "Backup camera mismatch"
        assert new_row.predicted_on == created, "Predicted on mismatch"
        assert new_row.prediction == entrylist[16], "Prediction value mismatch"


# Expected Failure testing
## Check whether i can add when missing values or none values provided
@pytest.mark.xfail(reason="Missing Values", strict=True)
@pytest.mark.usefixtures("logged_in_client")
@pytest.mark.parametrize(
    'entrylist',[[
        1,'Honda','5', 1.0, '2.5L I4 16V GDI DOHC Turbo',2
        ,'6-Speed Automatic','Gasoline','Four-wheel Drive',3.0,0,1.5,1,0,0,20000
    ],
    [1,'Honda',None, 1.0, '2.5L I4 16V GDI DOHC Turbo',2
        ,'6-Speed Automatic','Gasoline','Four-wheel Drive',3.0,0,1,1,0,0,20000]]
)
def test_entry_missing(entrylist, capsys):
    test_PredictionEntry(entrylist, capsys)