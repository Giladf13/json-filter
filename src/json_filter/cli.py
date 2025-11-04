import argparse       # parses command-line options/flags
import json           # read/write JSON files
import operator       # provides comparison operators as functions
import sys            # access to exit codes and stderr
from typing import Any, Dict, List

# Map symbols like '>=', '==' to real Python functions (ge, eq, etc.)
OPS = {
    "==": operator.eq,
    "!=": operator.ne,
    ">=": operator.ge,
    "<=": operator.le,
    ">": operator.gt,
    "<": operator.lt,
}

def parse_conditions(expr: str):
    """
    Parse a full expression like:
      age>=18 and country==IL
    or:
      active==true or country==US

    Returns a list of (key, op_func, value, logic)
    where 'logic' is 'and' or 'or' (for chaining).
    """
    tokens = expr.replace("AND", "and").replace("OR", "or").split()
    conditions = []
    logic = "and"

    i = 0
    while i < len(tokens):
        token = tokens[i]
        if token.lower() in ("and", "or"):
            logic = token.lower()
            i += 1
            continue

        # Join tokens until we find a comparison symbol
        for symbol in ["==", "!=", ">=", "<=", ">", "<"]:
            if symbol in token:
                left, right = token.split(symbol, 1)
                key = left.strip()
                raw = right.strip()

                val = raw
                for caster in (int, float):
                    try:
                        val = caster(raw)
                        break
                    except ValueError:
                        pass
                if isinstance(val, str) and raw.lower() in ("true", "false"):
                    val = raw.lower() == "true"

                conditions.append((key, OPS[symbol], val, logic))
                break
        i += 1
    return conditions

    raise ValueError(f"Unsupported where expression: {expr}")

def filter_record(rec: Dict[str, Any], include_keys: List[str] | None, where: str | None):
    """
    Apply the --where condition (if any), then keep only --include-keys (if provided).
    Return None to drop the record when the condition fails.
    """
    if where:
        conditions = parse_conditions(where)
        keep = True
        current_logic = "and"
        for key, op, val, logic in conditions:
            result = key in rec and op(rec[key], val)
            if current_logic == "and":
                keep = keep and result
            else:
                keep = keep or result
            current_logic = logic
        if not keep:
            return None


    # if include_keys was provided, return only those keys
    if include_keys:
        return {k: rec.get(k) for k in include_keys}

    # otherwise return the original record unchanged
    return rec

def main():
    # define CLI flags and arguments
    parser = argparse.ArgumentParser(description="Filter JSON by keys/where.")
    parser.add_argument("path", help="Path to JSON file (array of objects)")
    parser.add_argument("--include-keys", nargs="+", help="Keys to keep")
    parser.add_argument("--where", help='Simple condition, e.g. age>=18 or country==US')
    args = parser.parse_args()

    # read the input file safely
    try:
        with open(args.path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Failed to read JSON: {e}", file=sys.stderr)
        sys.exit(2)  # exit code 2 = command usage / input error

    # we expect the file to be a JSON array of objects like: [ {...}, {...} ]
    if not isinstance(data, list):
        print("Input JSON must be an array of objects", file=sys.stderr)
        sys.exit(2)

    out = []
    for rec in data:
        if not isinstance(rec, dict):
            continue
        filtered = filter_record(rec, args.include_keys, args.where)
        if filtered is not None:
            out.append(filtered)

    # print the result to standard output as pretty JSON
    json.dump(out, sys.stdout, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
