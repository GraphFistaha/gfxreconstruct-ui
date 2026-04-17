import json

import pandas as pd

COLUMNS = ["index", "type", "frame", "function", "full_info"]

def buildTraceView(traceJson):

    def parseArgs(args) -> str:
        def parseArg(arg_name, arg_value) -> str:
            if type(arg_value) is dict or type(arg_value) is object:
                return f"{arg_name}(...)"
            if type(arg_value) is list:
                return "[...]" if type(arg_value[0]) is dict else str(arg_value)
            if arg_value is None:
                return "nullptr"
            else:
                v = str(arg_value)
                return v if len(v) > 0 else "''"

        return ", ".join(parseArg(k, v) for k, v in args.items())

    rows = []
    currentFrame = 0
    for record in traceJson:
        if "header" in record:
            print(record["header"])
        elif "meta" in record:
            index = int(record["index"])
            meta = record["meta"]
            short_args = parseArgs(meta["args"])
            rows.append([index, "meta", currentFrame, f"{meta['name']}({short_args})", json.dumps(meta, indent=4)])
        elif "function" in record:
            index = int(record["index"])
            function = record["function"]
            short_args = parseArgs(function["args"])
            result = f" -> {function['return']}" if "return" in function else ""
            rows.append(
                [
                    index,
                    "function",
                    currentFrame,
                    f"{function['name']}({short_args}){result}",
                    json.dumps(function, indent=2),
                ]
            )
        elif "frame" in record:
            currentFrame = int(record['frame']['frame_number'])
        elif "annotation" in record:
            print("annotation")
        else:
            print("UNKNOWN RECORD", record)
    
    #indices = [row[0] for row in rows]
    df = pd.DataFrame(rows, columns=COLUMNS)
    df = df.set_index('index')
    return df
