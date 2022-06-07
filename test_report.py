import pytest
import pathlib

#file = "/c/Users/Wende/PycharmProjects/TCC/venv"
results = str(pathlib.Path('/c/Users/Wende/PycharmProjects/TCC/venv').parent) #---> o pyteste ta reclamando que esse file não ta definido.
request_id = "test_Case" #---> esse é o nome do meu arquivo onde estão os testes.
path_suite_testes = results #--- esse test_suite é uma pasta ?
path_report = results + request_id
result = pytest.main(
    [
        path_suite_testes,
        "-k Case",
        "--serial_number",
        "RQCT302JYQD",
        "--request_id",
        request_id,
        "--model",
        "S908E",
        "--html={}report.html".format(path_report + "\\"),
    ]
)