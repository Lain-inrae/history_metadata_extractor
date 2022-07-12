#!/usr/bin/env python

import json


PAGE_TEMPLATE = '\n'.join((
  "<!doctype HTML>",
  "<html>",
  "{header}"
  "  <body",
  "    class=\"bg-secondary bg-gradient\"",
  "    style=\"--bs-bg-opacity: .1;\"",
  "  >",
  "    <div class=\"container bg-white\">"
  "{styles}",
  "{title}",
  "{table_list}",
  "    </div>"
  "  </body>",
  "</html>",
))

HEADER = """
<head>
  <link href="vendor/bootstrap.min.css" rel="stylesheet" />
</head>
"""
CSS_STYLES = """
"""
"""
<style>
table{
  border: 1px solid;
  border-collapse: separate;
  border-radius: var(--elem-radius);
  border-spacing: 0;
  margin: 1rem 0;
  width: 100%;
  text-align: center;
  box-sizing: border-box;
  border-collapse: collapse;
}

tr {
  border: none;
}

td, th {
  border-right: solid 1px #000;
  border-left: solid 1px #000;
}

.even {
  background-color: #e3ffe3
}
.odd {
  background-color: #e3e3e3
}
</style>"""

TITLE_TEMPLATE = "<h1>Galaxy {galaxy_version}</h1>"

TABLE_TEMPLATE = '\n'.join((
  "<h2>{tool_id}</h2>",
  "<h3>{tool_output}</h3>",
  "<table class=\"table table-dark table-striped table-hover\">",
  "{table}",
  "</table>",
))

HEADER_LIST_TEMPLATE = '\n'.join((
  "<thead class=\"\">",
  "{header_list}",
  "</thead>",
))

HEADER_TEMPLATE = "<th scope=\"col\">{}</th>"
COLUMN_TEMPLATE = "<th scope=\"row\">{}</th>"

TABLE_LINE_LIST_TEMPLATE = '\n'.join((
  "<tr class=\"{classes}\">",
  "{table_lines}",
  "</tr>",
))
TABLE_LINE_TEMPLATE = "<td class=\"\">{}</td>"

INDENT = "  "

GLOBAL_CACHE = {}

def indent(text):
  if text.startswith("\n"):
    return text.replace("\n", f"\n{INDENT}")
  else:
    return INDENT+text.replace("\n", f"\n{INDENT}")

def convert_to_html(objects):
  return PAGE_TEMPLATE.format(
    header=HEADER,
    styles=CSS_STYLES.replace("\n<", "\n  <"),
    title=indent(indent(get_title(objects))),
    table_list=indent(indent(get_table_list(objects)))
  )

def get_title(objects):
  galaxy_version = objects[0].get("galaxy_version", "Unknown version")
  return TITLE_TEMPLATE.format(galaxy_version=galaxy_version)

def get_table_list(objects):
  return '\n'.join((
    convert_item_to_table(obj)
    for obj in objects
  ))

def convert_item_to_table(obj):
  output_hid = obj.get("encoded_id")
  if not output_hid:
    print(obj)
    if obj["output_datasets"]:
      output_hid = ';'.join(map(str, sorted(obj["output_datasets"])))
    else:
      output_hid = "Unknown"
  return TABLE_TEMPLATE.format(
    tool_id=obj["tool_id"],
    tool_output=output_hid,
    table=convert_parameters_to_html(obj)
  )

def convert_parameters_to_html(obj):
  params = obj["params"]
  params_enrichment(obj, params)
  keys = [
    key for key in iter_parameter_keys(params)
    if key not in ("dbkey", "chromInfo", "__input_ext", "request_json")
  ]
  return '\n'.join((
    indent(get_table_header(params, keys)),
    indent(get_table_lines(params, keys)),
  ))

def params_enrichment(obj, params):
  if (
    all(map(params.__contains__, ("request_json", "files")))
    and "encoded_id" in obj
  ):
    params.update(json.loads(params.pop("request_json")))
    for i, target in enumerate(params.pop("targets")):
      files = target["elements"]
      params["files"][i]["hid"] = ';'.join(str(file["object_id"]) for file in files)
      params["files"][i]["name"] = ';'.join(str(file["name"]) for file in files)
      params["files"][i]["extension"] = ';'.join(str(file["ext"]) for file in files)
    GLOBAL_CACHE[obj["encoded_id"]] = {
      "hid": ';'.join(file["hid"] for file in params["files"]),
      "name": ';'.join(file["name"] for file in params["files"]),
      "extension": ';'.join(file["extension"] for file in params["files"]),
    }

def iter_parameter_keys(params):
  for key in params:
    param = params[key]
    if param_is_file(param):
      yield key
    elif isinstance(param, dict):
      for subkey in iter_parameter_keys(param):
        if subkey not in ("__current_case__", ):
          yield f"{key}.{subkey}"
    else:
      yield key

def param_is_file(param):
  return is_file_v1(param) or is_file_v2(param)

def is_file_v1(param):
  return (
    isinstance(param, dict)
    and all(map(
      param.__contains__,
      ("info", "peek", "name", "extension")
    ))
  )

def is_file_v2(param):
  return (
    isinstance(param, dict)
    and "values" in param
    and isinstance(param["values"], list)
    and isinstance(param["values"][0], dict)
    and all(map(param["values"][0].__contains__, ("id", "src")))
  )

def get_table_header(params, keys):
  return HEADER_LIST_TEMPLATE.format(
    header_list=indent('\n'.join(map(HEADER_TEMPLATE.format, [""]+keys)))
  )

def get_table_lines(params, keys):
  return ''.join(table_lines_iterator(params, keys))

def table_lines_iterator(params, param_names):
  keys = ("value", "name", "extension", "hid",)
  for key in keys:
    classes = ""
    table_lines = []
    for param_name in param_names:
      subparam = params
      while '.' in param_name:
        subkey, param_name = param_name.split('.', 1)
        subparam = subparam[subkey]
      param = extract_param_info(key, subparam[param_name])
      table_lines.append(param)
    yield TABLE_LINE_LIST_TEMPLATE.format(
      classes=classes,
      table_lines=(
        indent(COLUMN_TEMPLATE.format(key) + '\n')
        + indent('\n'.join(map(
          TABLE_LINE_TEMPLATE.format,
          table_lines
        )))
      )
    )

def extract_param_info(key, param):
  if key == "value":
    return extract_param_value(param)
  if isinstance(param, dict) and key in param:
    return str(param[key])
  if isinstance(param, list):
    return ';'.join(extract_param_info(key, p) for p in param)
  return ""

def extract_param_value(param):
  if isinstance(param, dict):
    if "__current_case__" in param:
      return join_dict_key_values(param, ignore=("__current_case__", ))
    for acceptable_value in ("file_data", "file_name"):
      if acceptable_value in param:
        return f"{acceptable_value}: {param[acceptable_value]}"
    if "values" in param:
      ids = []
      for file_id in param["values"]:
        file_id = file_id["id"]
        ids.append(file_id)
        if file_id in GLOBAL_CACHE:
          file_info = GLOBAL_CACHE[file_id]
          param["name"] = file_info["name"]
          param["hid"] = file_info["hid"]
          param["extension"] = file_info["extension"]
      return ';'.join(ids)
  if isinstance(param, (str, int, float)):
    return str(param)
  if isinstance(param, (list, tuple)):
    return ';'.join(map(extract_param_value, param))
  return str(param)

def join_dict_key_values(dico, ignore=()):
  return ';'.join(
    f"{name}: {dico[name]}"
    for name in dico
    if name not in ignore
  )

if __name__ == "__main__":
  import optparse
  parser = optparse.OptionParser()
  parser.add_option(
    "-i", "--input",
    dest="input",
    help="write report of FILE",
    metavar="FILE",
    default="jobs_attrs.txt"
  )
  parser.add_option(
    "-o", "--output",
    dest="output",
    help="write report to FILE",
    metavar="FILE",
    default="out.html"
  )

  (options, args) = parser.parse_args()
  with open(options.input) as j:
    objects = json.load(j)

  objects = sorted([{
    key: obj.get(key)
    for key in (
      "galaxy_version",
      "tool_id",
      "tool_version",
      "encoded_id",
      "params",
      "output_datasets",
    )
  } for obj in objects],
    key=lambda x:x.get("output_datasets", [-1])[0]
  )

  with open(options.output, "w") as o:
    o.write(convert_to_html(objects))
