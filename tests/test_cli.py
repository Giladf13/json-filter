# tests/test_cli.py
# This file contains tests for your json-filter CLI tool.

from json_filter.cli import filter_record, parse_conditions


def test_parse_conditions_basic():
    conds = parse_conditions("age>=18")
    assert len(conds) == 1
    k, op, v, logic = conds[0]
    assert k == "age"
    assert op(20, v) is True
    assert op(17, v) is False


def test_filter_include_only():
    rec = {"name": "Dana", "id": 5, "age": 30}
    out = filter_record(rec, include_keys=["name", "id"], where=None)
    assert out == {"name": "Dana", "id": 5}


def test_filter_where_true():
    rec = {"name": "Dana", "age": 30}
    out = filter_record(rec, include_keys=None, where="age>=18")
    assert out == rec


def test_filter_where_false():
    rec = {"name": "Dana", "age": 16}
    out = filter_record(rec, include_keys=None, where="age>=18")
    assert out is None


def test_bool_and_string_casts():
    rec = {"active": True, "country": "US"}
    assert filter_record(rec, None, "active==true") == rec
    assert filter_record(rec, None, "country==US") == rec
