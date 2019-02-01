from enum import Enum

class ecotouch_tag(Enum):
    def __init__(self, identifier, tag, description, unit, factor, pattern):
        self.identifier = identifier
        self.tag = tag
        self.description = description
        self.unit = unit
        self.factor = factor
        self.pattern = pattern

    TEMPERATURE_OUTSIDE = ('temperature_outside', 'A1', 'Außentemperatur', '°C', 0.1, '%.1f')
    TEMPERATURE_OUTSIDE_1H = ('temperature_outside_1h', 'A2', 'Außentemperatur gemittelt 1h', '°C', 0.1, '%.1f')
    TEMPERATURE_OUTSIDE_24H = ('temperature_outside_24h', 'A3', 'Außentemperatur gemittelt 24h', '°C', 0.1, '%.1f')


