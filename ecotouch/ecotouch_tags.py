from enum import Enum

class ecotouch_tag(Enum):
    def __init__(self, identifier, tag, description, unit, val_type, no_decimal_places = 0):
        self.identifier = identifier
        self.tag = tag
        self.description = description
        self.unit = unit
        self.val_type = val_type
        self.no_decimal_places = no_decimal_places

    TEMPERATURE_OUTSIDE = ('temperature_outside', 'A1', 'Außentemperatur', '°C', float, 1)
    TEMPERATURE_OUTSIDE_1H = ('temperature_outside_1h', 'A2', 'Außentemperatur gemittelt 1h', '°C', float, 1)
    TEMPERATURE_OUTSIDE_24H = ('temperature_outside_24h', 'A3', 'Außentemperatur gemittelt 24h', '°C', float, 1)
    TEMPERATURE_SOURCE_IN = ('temperature_source_in', 'A4', 'Quelleneintrittstemperatur', '°C', float, 1)
    TEMPERATURE_SOURCE_OUT = ('temperature_source_out', 'A5', 'Quellenaustrittstemperatur', '°C', float, 1)
    TEMPERATURE_EVAPORATION = ('temperature_evaporation', 'A6', 'Verdampfungstemperatur', '°C', float, 1)
    TEMPERATURE_SUCTION = ('temperature_suction', 'A7', 'Sauggastemperatur', '°C', float, 1)
    PRESSURE_EVAPORATION = ('pressure_evaporation', 'A8', 'Verdampfungsdruck', 'hPa', float, 1)
    TEMPERATURE_RETURN_SET = ('temperature_return_set', 'A9', 'Rücklauftemperatur Soll', '°C', float, 1)
    TEMPERATURE_RETURN = ('temperature_return_set', 'A10', 'Rücklauftemperatur', '°C', float, 1)
    TEMPERATURE_ROOM = ('temperature_room', 'A17', 'Zimmertemperatur', '°C', float, 1)


    ADAPT_HEATING = ('adapt_heating', 'I263', 'Temperaturanpassung', None, int)



