import sys
import os
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)
from application.models import Prediction
print(Prediction)
from datetime import datetime
import pytest
import json


# Validity testing 
## to see if one is able to predict
@pytest.mark.usefixtures("logged_in_client")
@pytest.mark.parametrize(
    'entrylist',[[
        1,'Honda',1968,2023-1968, 1.0, '2.5L I4 16V GDI DOHC Turbo',2
        ,'6-Speed Automatic','Gasoline','Four-wheel Drive',3.0,0,1.5,1,0,1,20000
    ],
    [        1,'Honda',2011,2023-2011, 1.0, '2.5L I4 16V GDI DOHC Turbo',2
        ,'6-Speed Automatic','Gasoline','Four-wheel Drive',3.0,0,1,1,0,1,30000]]
)
def test_predict(client, entrylist, capsys):
    with capsys.disabled():
        data1 = dict(
            brand = entrylist[1],
            year = entrylist[2],
            Age = entrylist[3],
            mileage = entrylist[4],
            engine = entrylist[5],
            engine_size = entrylist[6],
            transmission = entrylist[7],
            fuel_type = entrylist[8],
            drivetrain = entrylist[9],
            min_mpg = entrylist[10],
            damaged = entrylist[11],
            turbo = entrylist[12],
            navigation_system = entrylist[13],
            backup_camera = entrylist[14],
            first_owner = entrylist[15]
        )
        if len(entrylist) > 16:
            data1["price"] = entrylist[16]
        else:
            data1["price"] = None
        response = client.post(
            "/api/predict", data=json.dumps(data1), content_type="application/json"
        )

        print('Response status code:', response.status_code)
        print('Response data:', response.data)

        response_body = json.loads(response.get_data(as_text=True))

        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"

        pred = float(response_body["prediction"])
        assert pred > 0, "Predicted value should be greater than 0"

# Range testing
## Check if the values is out of range is it able to predict
@pytest.mark.xfail(reason="Out of range", strict=True)
@pytest.mark.usefixtures("logged_in_client")
@pytest.mark.parametrize(
    'entrylist',[[
        1,'Honda',-1967, 1.0, '2.5L I4 16V GDI DOHC Turbo',2
        ,'6-Speed Automatic','Gasoline','Four-wheel Drive',-3.0,0,1,1,0,1,0,20000],
    [        1,'Honda',-2000, 1.0, '2.5L I4 16V GDI DOHC Turbo',2
        ,'6-Speed Automatic','Gasoline','Four-wheel Drive',3.0,0,1,1,0,1,0, 20000]]
)

def test_range_exceed(client, entrylist,capsys):
    test_predict(client, entrylist,capsys)


# Range testing
## Check whether missing values leads to fail
@pytest.mark.xfail(reason="Missing Values", strict=True)
@pytest.mark.usefixtures("logged_in_client")
@pytest.mark.parametrize(
    'entrylist',[[
        1,None,1967.5, 0, '2.5L I4 16V GDI DOHC Turbo',2
        ,'6-Speed Automatic','Gasoline','Four-wheel Drive',3.0,0,1.5,1,0,1,0
    ],
    [        1,'Honda',2010, 1.0, '2.5L I4 16V GDI DOHC Turbo',2
        ,'6-Speed Automatic','Gasoline','Four-wheel Drive',3.0,0,1,1,0,1,0]]
)
def test_missing_output(client, entrylist,capsys):
    test_predict(client, entrylist,capsys)


# Range testing 
## Check whether invalid engine size lead to fail
@pytest.mark.xfail(reason="Invalid engine size", strict=True)
@pytest.mark.usefixtures("logged_in_client")
@pytest.mark.parametrize(
    'entrylist',[[
        1,None,1967.5, -2.5, '2.5L I4 16V GDI DOHC Turbo',2
        ,'6-Speed Automatic','Gasoline','Four-wheel Drive',3.0,0,1.5,1,0,1,0,20000
    ],
    [        1,'Honda',2010, -2.5, '2.5L I4 16V GDI DOHC Turbo',2
        ,'6-Speed Automatic','Gasoline','Four-wheel Drive',3.0,0,1,1,0,1,0,20000]]
)
def test_missing_output(client, entrylist,capsys):
    test_predict(client, entrylist,capsys)


# Consistency testing
## Check whether the prediciton are consistent
@pytest.mark.parametrize(
    'entrylist', [
        [1, 'Honda', 2000, 2023-2000, 1.0, '2.5L I4 16V GDI DOHC Turbo', 2,
         '6-Speed Automatic', 'Gasoline', 'Four-wheel Drive', 3.0, 0, 1, 1, 0, 1, 20000]
    ]
)
def test_prediction_consistency(entrylist):
    created = datetime(2023, 1, 1, 0, 0, 0)  

    predictions = [Prediction(
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
        ) for _ in range(5)]

    prediction_dicts = [{k: v for k, v in pred.__dict__.items() if k != '_sa_instance_state'} for pred in predictions]

    for i in range(1, len(prediction_dicts)):
        assert prediction_dicts[i] == prediction_dicts[0], f"Inconsistency found in instance {i}"