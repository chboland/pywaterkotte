from ecotouch.ecotouch import (Ecotouch, InvalidResponseException, StatusException)
from ecotouch.ecotouch_tags import ecotouch_tag
import responses
import pytest

HOSTNAME = 'hostname'


# Helper functions
def prepare_response(action, body):
    responses.add(
            responses.GET, 
            'http://%s/cgi/%s' % (HOSTNAME, action), 
            body=body)


@responses.activate
def test_login_invalid_response():
    prepare_response('login', 'invalid')
    wp = Ecotouch(HOSTNAME)

    with pytest.raises(InvalidResponseException) as e_info:
        wp.login()

@responses.activate
def test_login_relogin():
    prepare_response('login', '#E_RE-LOGIN_ATTEMPT')
    wp = Ecotouch(HOSTNAME)
    with pytest.raises(StatusException) as e_info:
        wp.login()

@responses.activate
def test_login_success():
    prepare_response('login', '1\n#S_OK\nIDALToken=7030fabe1f6beb2ca91a6cfd8806d6ad')
    wp = Ecotouch(HOSTNAME)
    wp.login()
    
@responses.activate
def test_read_tag():
    prepare_response('readTags', '#A1\tS_OK\n192\t86\n')
    wp = Ecotouch(HOSTNAME)
    assert wp.read_tag(ecotouch_tag.TEMPERATURE_OUTSIDE) == 8.6

@responses.activate
def test_read_multiple_tags():
    RESPONSE = "".join([
    '#A1\tS_OK\n192\t84\n',
    '#A2\tS_OK\n192\t87\n',
    '#A3\tS_OK\n192\t92\n',
    '#A4\tS_OK\n192\t95\n',
    '#A5\tS_OK\n192\t57\n'])
    prepare_response('readTags', RESPONSE)
    wp = Ecotouch(HOSTNAME)
    result = wp.read_tags([
        ecotouch_tag.TEMPERATURE_OUTSIDE,
        ecotouch_tag.TEMPERATURE_OUTSIDE_1H,
        ecotouch_tag.TEMPERATURE_OUTSIDE_24H,
        ecotouch_tag.TEMPERATURE_SOURCE_IN,
        ecotouch_tag.TEMPERATURE_SOURCE_OUT])

    assert result is not None
    assert isinstance(result, dict)
    assert result[ecotouch_tag.TEMPERATURE_OUTSIDE] == 8.4
    assert result[ecotouch_tag.TEMPERATURE_OUTSIDE_1H] == 8.7
    assert result[ecotouch_tag.TEMPERATURE_OUTSIDE_24H] == 9.2
    assert result[ecotouch_tag.TEMPERATURE_SOURCE_IN] == 9.5
    assert result[ecotouch_tag.TEMPERATURE_SOURCE_OUT] == 5.7

