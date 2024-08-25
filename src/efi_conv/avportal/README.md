# Import from AV-Portal

This module is used to import metadata about audio visual material
presented on the [AV-Portal](https://av.tib.eu/).

The input parser has been auto generated from the in-house NTM schema
courtesy of the [xsData project][xsdata] by running the following
command in this directory:

```console
$ pdm run xsdata generate --include-header --unnest-classes \
    --relative-imports --docstring-style NumPy --package generated \
    http://www.tib.eu/fileadmin/extern/knm/NTM-Metadata-Schema_v_2.5.xsd
```

[xsdata]: https://xsdata.readthedocs.io/
