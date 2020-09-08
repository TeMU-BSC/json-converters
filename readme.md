# JSON converters

This is a collection of python scripts that converts many different types of formats into json-based formats.

## Usage

``` bash
$ python3 -m venv venv
$ source venv/bin/activate
(venv) $ pip install -r requirements.txt
```

## Example

Convert brat format into jsonl format for prodigy.
``` bash
(venv) $ cd brat
(venv) $ python3 brat2jsonl.py --txtfiles ictusnet-sample/*.txt --annfiles ictusnet-sample/*.ann --outfile ictusnet-sample.jsonl
```
