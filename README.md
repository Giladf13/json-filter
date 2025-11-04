![CI](https://github.com/Giladf13/json-filter/actions/workflows/ci.yml/badge.svg)


# json-filter
Small Python CLI to filter JSON input by keys and simple conditions.

## Examples
```bash
json-filter --include-keys name id --where "age>=18" people.json
