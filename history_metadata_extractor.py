#!/usr/bin/env python

import json
import os
import sys


with open(os.path.join(sys.path[0], "static", "app.css")) as css:
  CSS_STYLES = css.read()

with open(os.path.join(sys.path[0], "vendor", "bootstrap.min.css")) as bootstrap:
  CSS_STYLES = f"{CSS_STYLES}\n{bootstrap.read()}"

with open(os.path.join(sys.path[0], "static", "app.js")) as js:
  JAVASCRIPT = js.read()

with open(os.path.join(sys.path[0], "static", "app.template.html")) as template:
  PAGE_TEMPLATE = template.read()

with open(os.path.join(sys.path[0], "static", "title.template.html")) as template:
  TITLE_TEMPLATE = template.read()

with open(os.path.join(sys.path[0], "static", "table.template.html")) as template:
  TABLE_TEMPLATE = template.read()

with open(os.path.join(sys.path[0], "static", "header_list.template.html")) as template:
  HEADER_LIST_TEMPLATE = template.read()

HEADER_LIST_TEMPLATE = '\n'.join((
  "<thead>",
  "  <tr>",
  "{header_list}",
  "  </tr>",
  "</thead>",
))

HEADER_TEMPLATE = "<th scope=\"col\">{}</th>"
COLUMN_TEMPLATE = "<th scope=\"row\">{}</th>"

TABLE_LINE_LIST_TEMPLATE = '\n'.join((
  "<tr class=\"{classes}\">",
  "{table_lines}",
  "</tr>",
))
TABLE_LINE_TEMPLATE = "<td>{}</td>"

INDENT = "  "


HISTORY_CACHE = {}

def indent(text):
  if text.startswith("\n"):
    return text.replace("\n", f"\n{INDENT}")
  else:
    return INDENT+text.replace("\n", f"\n{INDENT}")

def noempty(ls, as_list=True):
  if as_list:
    return [x for x in ls if x]
  return (x for x in ls if x)

def join_noempty(ls, sep=';'):
  return sep.join(noempty(ls, as_list=False))

def extract_dataset_attributes(dataset_attrs):
  for dataset_attr in dataset_attrs:
    HISTORY_CACHE[dataset_attr["encoded_id"]] = dataset_attr
  HISTORY_CACHE["dataset_attrs"] = dataset_attrs

def convert_to_html(jobs_attrs, dataset_attrs=None):
  if dataset_attrs:
    extract_dataset_attributes(dataset_attrs)
  return PAGE_TEMPLATE.format(
    styles=CSS_STYLES.replace("\n<", "\n  <"),
    javascript=JAVASCRIPT,
    title=indent(indent(get_title(jobs_attrs))),
    table_list=indent(indent(get_table_list(jobs_attrs)))
  )

def get_title(jobs_attrs):
  galaxy_version = jobs_attrs[0]["galaxy_version"] or "Unknown version"
  return TITLE_TEMPLATE.format(galaxy_version=galaxy_version)

def get_table_list(jobs_attrs):
  return '\n'.join((
    convert_item_to_table(job_attr, dataset_id)
    for job_attr in jobs_attrs
    for dataset_id_set in (
      job_attr["output_dataset_mapping"]
      or {1:"unknown"}
    ).values()
    for dataset_id in dataset_id_set
  ))

def convert_item_to_table(job_attr, dataset_id):
  encoded_jid = job_attr.get("encoded_id")
  if HISTORY_CACHE:
    history = HISTORY_CACHE.get(dataset_id, {})
    hid = history.get("hid", "DELETED")
  else:
    hid = "?"
  exit_code = job_attr.get("exit_code")
  if job_attr["exit_code"] == 0:
    status = f"Ok ({exit_code})"
    classes = "alert alert-success"
  else:
    status = f"Failed ({exit_code})"
    classes = "alert alert-danger"
  if hid == "DELETED":
    classes += " history_metadata_extractor_deleted"
  tool_name = job_attr["tool_id"]
  if tool_name.count("/") >= 4:
    tool_name = job_attr["tool_id"].split("/")[-2]
  tool_name = tool_name + " - " + job_attr["tool_version"]
  tool_name = f"[{hid}] - {tool_name}"
  return TABLE_TEMPLATE.format(
    classes=classes,
    tool_name=tool_name,
    tool_output="",
    tool_status=status,
    table=convert_parameters_to_html(job_attr)
  )

def convert_parameters_to_html(job_attr):
  params = job_attr["params"]
  params_enrichment(job_attr, params)
  keys = [
    key for key in iter_parameter_keys(params)
    if key not in ("dbkey", "chromInfo", "__input_ext", "request_json")
  ]
  return '\n'.join((
    indent(get_table_header(params, ["value", "name", "extension", "hid"])),
    indent(get_table_lines(params, keys)),
  ))

def params_enrichment(job_attr, params):
  if (
    all(map(params.__contains__, ("request_json", "files")))
    and "encoded_id" in job_attr
  ):
    params.update(json.loads(params.pop("request_json")))
    for i, target in enumerate(params.pop("targets")):
      files = target["elements"]
      params["files"][i]["hid"] = join_noempty(
        str(file["object_id"])
        for file in files
      )
      params["files"][i]["name"] = join_noempty(
        str(file["name"])
        for file in files
      )
      params["files"][i]["extension"] = join_noempty(
        str(file["ext"])
        for file in files
      )

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
    header_list=indent(indent('\n'.join(map(HEADER_TEMPLATE.format, [""]+keys))))
  )

def get_table_lines(params, keys):
  return ''.join(table_lines_iterator(params, keys))

def table_lines_iterator(params, param_names):
  keys = ("value", "name", "extension", "hid",)
  for param_name in param_names:
    classes = ""
    table_lines = []
    subparam = params
    while '.' in param_name:
      subkey, param_name = param_name.split('.', 1)
      subparam = subparam[subkey]
    for key in keys:
      param = extract_param_info(key, subparam[param_name])
      table_lines.append(param)
    yield TABLE_LINE_LIST_TEMPLATE.format(
      classes=classes,
      table_lines=(
        indent(COLUMN_TEMPLATE.format(param_name) + '\n')
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
    return join_noempty(extract_param_info(key, p) for p in param)
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
        if file_id in HISTORY_CACHE:
          file_info = HISTORY_CACHE[file_id]
          param["name"] = file_info["name"]
          param["hid"] = file_info["hid"]
          param["extension"] = file_info["extension"]
          ids.append(file_id)
      return join_noempty(ids)
  if isinstance(param, (str, int, float)):
    return str(param)
  if isinstance(param, (list, tuple)):
    return join_noempty(map(extract_param_value, param))
  return str(param)

def join_dict_key_values(dico, ignore=()):
  return join_noempty(
    f"{name}: {dico[name]}"
    for name in dico
    if name not in ignore
  )

if __name__ == "__main__":
  import optparse
  parser = optparse.OptionParser()
  parser.add_option(
    "-j", "--jobs-attrs",
    dest="jobs_attrs",
    help="write report of FILE",
    metavar="FILE",
    default="jobs_attrs.txt"
  )
  parser.add_option(
    "-d", "--dataset-attrs",
    dest="dataset_attrs",
    help="extract additional info from this file",
    metavar="FILE",
    default=None,
  )
  parser.add_option(
    "-o", "--output",
    dest="output",
    help="write report to FILE",
    metavar="FILE",
    default="out.html"
  )
  parser.add_option(
    "-v", "--version",
    action="store_true",
    help="Show this script's version and exits",
  )

  (options, args) = parser.parse_args()

  if options.version:

    import re

    with open(os.path.join(sys.path[0], "README.md")) as readme:
      for line in readme.readlines():
        if "**@VERSION**" in line:
          print(re.search(r"\d+\.\d+\.\d+", line)[0])
    sys.exit(0)

  with open(options.jobs_attrs) as j:
    jobs_attrs = json.load(j)

  if options.dataset_attrs is not None:
    with open(options.dataset_attrs) as ds:
      dataset_attrs = json.load(ds)
  else:
    dataset_attrs = {}

  jobs_attrs = [{
    key: jobs_attr.get(key)
    for key in (
      "galaxy_version",
      "tool_id",
      "tool_version",
      "encoded_id",
      "params",
      "output_datasets",
      "exit_code",
      "output_dataset_mapping",
    )
  } for jobs_attr in jobs_attrs]
  if jobs_attrs and jobs_attrs[0].get("output_datasets"):
    jobs_attrs = sorted(
      jobs_attrs,
      key=lambda x:x["output_datasets"][0]
    )

  with open(options.output, "w") as o:
    o.write(convert_to_html(jobs_attrs, dataset_attrs=dataset_attrs))
