from enum import Enum

class ecotouch_tag(Enum):
    def __init__(self, identifier, tag, description):
        self.identifier = identifier
        self.tag = tag
        self.description = description

    TEMPERATURE_OUTSIDE = ('temperature_outside', 'A1', 'Außentemperatur')


