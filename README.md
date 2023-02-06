# pywaterkotte

pywaterkotte is a library to communicate with Waterkotte heatpumps. Functions tested with my DS 5012.5AI geothermal heatpump.

# Basic usage

```
>>> from pywaterkotte import Ecotouch, EcotouchTags
>>> e = Ecotouch('192.168.1.123')
>>> e.login()
>>> e.read_value(EcotouchTags.OUTSIDE_TEMPERATURE)
12.7
```

# Warning

> "With great power comes great responsibility"

This library allows writing to fields usually not accessible to the end-user. This option should be used with caution as it might damage your heatpump. No responsibility is taken in any form.

# Contributions

Contributions to this library are encouraged. Feel free to create pull-requests or file bug reports.


