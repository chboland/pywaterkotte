from ecotouch.ecotouch import (Ecotouch, InvalidResponseException, StatusException)
from ecotouch.ecotouch_tags import ecotouch_tag
import responses
import pytest

HOSTNAME = 'hostname'

@pytest.fixture
def wp_instance():
    return Ecotouch(HOSTNAME)


# Helper functions
def prepare_response(action, body):
    responses.add(
            responses.GET, 
            'http://%s/cgi/%s' % (HOSTNAME, action), 
            body=body)


@responses.activate
def test_login_invalid_response(wp_instance):
    prepare_response('login', 'invalid')

    with pytest.raises(InvalidResponseException) as e_info:
        wp_instance.login()

@responses.activate
def test_login_relogin(wp_instance):
    prepare_response('login', '#E_RE-LOGIN_ATTEMPT')
    with pytest.raises(StatusException) as e_info:
        wp_instance.login()

@responses.activate
def test_login_success(wp_instance):
    prepare_response('login', '1\n#S_OK\nIDALToken=7030fabe1f6beb2ca91a6cfd8806d6ad')
    wp_instance.login()
    
@responses.activate
def test_read_tag(wp_instance):
    prepare_response('readTags', '#A1\tS_OK\n192\t86\n')
    assert wp_instance.read_tag(ecotouch_tag.TEMPERATURE_OUTSIDE) == 8.6

@responses.activate
def test_write(wp_instance):
    prepare_response('writeTags', '#I263\tS_OK\n192\t5\n')
    wp_instance.write_tag(ecotouch_tag.ADAPT_HEATING, 6)
    assert len(responses.calls) == 1


@responses.activate
def test_read_multiple_tags(wp_instance):
    RESPONSE = "".join([
    '#A1\tS_OK\n192\t84\n',
    '#A2\tS_OK\n192\t87\n',
    '#A3\tS_OK\n192\t92\n',
    '#A4\tS_OK\n192\t95\n',
    '#A5\tS_OK\n192\t57\n'])
    prepare_response('readTags', RESPONSE)
    result = wp_instance.read_tags([
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

