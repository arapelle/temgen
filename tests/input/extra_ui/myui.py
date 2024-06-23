import json
import sys

if __name__ == '__main__':
    input_var_fpath = sys.argv[2]
    with open(input_var_fpath, 'r') as var_file:
        variables = json.load(var_file)
    print(variables)
    variables["message"] = "super_" + variables["text"]
    output_var_fpath = sys.argv[1]
    with open(output_var_fpath, 'w') as var_file:
        json.dump(variables, var_file, indent=4)
