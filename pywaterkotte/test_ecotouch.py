from pywaterkotte.ecotouch import (
    Ecotouch, EcotouchTags, InvalidResponseException, AuthenticationException)
import responses
import pytest
from datetime import datetime

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
    with pytest.raises(AuthenticationException) as e_info:
        wp_instance.login()


@responses.activate
def test_login_success(wp_instance):
    prepare_response(
        'login', '1\n#S_OK\nIDALToken=7030fabe1f6beb2ca91a6cfd8806d6ad')
    wp_instance.login()


@responses.activate
def test_read_float32(wp_instance):

    #first  straight forward test
    prepare_response('readTags',
                     "".join([
                         '#A444\tS_OK\n192\t17708\n',
                         '#A445\tS_OK\n192\t7519\n']))
    assert wp_instance.read_value(EcotouchTags.COMPRESSOR_ELECTRIC_CONSUMPTION_YEAR) == pytest.approx(2753.8, 0.1)

    RESPONSE = "#A448\tS_OK\n192\t0\n#A449\tS_OK\n192\t0\n"
    prepare_response("readTags", RESPONSE)
    result = wp_instance.read_value(
        EcotouchTags.ELECTRICAL_HEATER_ELECTRIC_CONSUMPTION_YEAR
    )
    assert result == 0

    prepare_response('readTags',
                     "".join([
                         '#A454\tS_OK\n192\t17877\n',
                         '#A455\tS_OK\n192\t-17979\n']))
    assert wp_instance.read_value(EcotouchTags.HOT_WATER_ENERGY_PRODUCED_YEAR) == pytest.approx(6839.2, 0.1)


@ responses.activate
def test_read_tag(wp_instance):
    prepare_response('readTags', '#A1\tS_OK\n192\t86\n')
    assert wp_instance.read_value(EcotouchTags.TEMPERATURE_OUTSIDE) == 8.6


@ responses.activate
def test_read_bitfield(wp_instance):
    prepare_response('readTags', '#I51\tS_OK\n192\t170\n')
    assert wp_instance.read_value(EcotouchTags.STATE_COMPRESSOR) == True
    assert wp_instance.read_value(EcotouchTags.STATE_SOURCEPUMP) == False
    assert wp_instance.read_value(EcotouchTags.STATE_EXTERNAL_HEATER) == True
    assert wp_instance.read_value(EcotouchTags.STATE_HEATINGPUMP) == True


@ responses.activate
def test_write(wp_instance):
    prepare_response('writeTags', '#I263\tS_OK\n192\t5\n')
    wp_instance.write_value(EcotouchTags.ADAPT_HEATING, 6)
    assert len(responses.calls) == 1


@ responses.activate
def test_write_date(wp_instance):
    prepare_response('writeTags', '#I263\tS_OK\n192\t5\n')
    wp_instance.write_value(EcotouchTags.HOLIDAY_START_TIME,
                            datetime(2019, 3, 2, 11, 00))
    assert len(responses.calls) == 5


@ responses.activate
def test_read_date(wp_instance):
    RESPONSE="".join([
        '#I1250\tS_OK\n192\t18\n',
        '#I1251\tS_OK\n192\t2\n',
        '#I1252\tS_OK\n192\t1\n',
        '#I1253\tS_OK\n192\t3\n',
        '#I1254\tS_OK\n192\t19\n'])
    prepare_response('readTags', RESPONSE)
    result=wp_instance.read_value(EcotouchTags.HOLIDAY_START_TIME)
    assert isinstance(result, datetime)
    assert datetime(2019, 3, 1, 18, 2) == result


@ responses.activate
def test_read_multiple_tags(wp_instance):
    RESPONSE="".join([
        '#A1\tS_OK\n192\t84\n',
        '#A2\tS_OK\n192\t87\n',
        '#A3\tS_OK\n192\t92\n',
        '#A4\tS_OK\n192\t95\n',
        '#A5\tS_OK\n192\t57\n'])
    prepare_response('readTags', RESPONSE)
    result=wp_instance.read_values([
        EcotouchTags.TEMPERATURE_OUTSIDE,
        EcotouchTags.TEMPERATURE_OUTSIDE_1H,
        EcotouchTags.TEMPERATURE_OUTSIDE_24H,
        EcotouchTags.TEMPERATURE_SOURCE_IN,
        EcotouchTags.TEMPERATURE_SOURCE_OUT])

    assert result is not None
    assert isinstance(result, dict)
    assert result[EcotouchTags.TEMPERATURE_OUTSIDE] == 8.4
    assert result[EcotouchTags.TEMPERATURE_OUTSIDE_1H] == 8.7
    assert result[EcotouchTags.TEMPERATURE_OUTSIDE_24H] == 9.2
    assert result[EcotouchTags.TEMPERATURE_SOURCE_IN] == 9.5
    assert result[EcotouchTags.TEMPERATURE_SOURCE_OUT] == 5.7
