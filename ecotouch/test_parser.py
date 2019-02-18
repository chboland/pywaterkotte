RESULT = """
#A1\tS_OK
192\t92
#A2\tS_OK
192\t98
#A3\tS_OK
192\t98
#A4\tS_OK
192\t176
#A5\tS_OK
192\t174
#A6\tS_OK
192\t197
#A7\tS_OK
192\t240
#A8\tS_OK
192\t133
#A9\tS_OK
192\t0
#A10\tS_OK
192\t480
#A17\tS_OK
192\t-400
#I263\tS_OK
192\t4
"""

import re

def test_re():
    tag = 'A6'
    val = re.search(r'#%s\t(?P<status>[A-Z_]+)\n\d+\t(?P<value>\-?\d+)' % tag, RESULT, re.MULTILINE)
    assert val is not None
    assert val.group('status') == "S_OK"
    assert val.group('value') == "197"
