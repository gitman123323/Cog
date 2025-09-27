import sys
import json
from cog_lsp import parse_text

while True:
    try:
        # read one JSON line from Node
        line = sys.stdin.readline()
        if not line:
            break

        request = json.loads(line)
        text = request.get("text", "")
        uri = request.get("uri", "")

        errors = parse_text(text)

        # return JSON response
        response = {"uri": uri, "errors": errors}
        print(json.dumps(response))
        sys.stdout.flush()

    except Exception as e:
        # never exit, just report the error
        print(json.dumps({"error": str(e)}))
        sys.stdout.flush()
