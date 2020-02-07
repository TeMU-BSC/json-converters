# Patents to Mesinesp converter

Convert from patents' json schema (compressed inside GZ files) into mesinesp json schema (inside a valid single json array file).

## Examples

### Filter by Spanish language
```bash
python patents2mesinesp.py /path/to/input/files/*.gz /path/to/output/file/patents_es.json --lang es
```

<!-- ### Filter by English and Spanish languages
```bash
python patents2mesinesp.py /path/to/input/files/*.gz /path/to/output/file/patents_en_es.json --lang en es
``` -->

### Display help
```bash
python patents2mesinesp.py --help
```
