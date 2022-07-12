#!/usr/bin/env python

import json


PAGE_TEMPLATE = '\n'.join((
  "<!doctype HTML>",
  "<html>",
  "{styles}",
  "{header}",
  """
    <div
      style="
        position: fixed ;
        top: 80px ;
        left: 0px ;
        color: white;
        background-color: #2c3143;
        z-index: 999 ;
      "
    >
      <button
        id="top"
        class="btn btn-outline-light d-block m-2"
      >Top</button>
      <button
        id="folder"
        class="btn btn-outline-light d-block m-2"
      >Fold/Unfold tables</button>
      <button
        id="toggle_deleted"
        class="btn btn-outline-light d-block m-2"
      >Show/Hide deleted</button>
      <button
        id="bottom"
        class="btn btn-outline-light d-block m-2"
      >Bottom</button>
    </div>
  """,
  """
  <nav
    class="navbar justify-content-center navbar-dark navbar-expand"
    id="masthead"
    style="
      background-color: #2c3143;
      top:0px;
      position:fixed;
      width: 100%;
      z-index: 999 ;
    "
  >
    <a class="navbar-brand">
      <span class="navbar-brand-title">{title}</span>
    </a>
  </nav>
  """,
  "  <body",
  "    class=\"bg-secondary bg-gradient\"",
  "    style=\"--bs-bg-opacity: .1; padding-top: 80px\"",
  "  >",
  """
      <div
        id=\"content\"
        class=\"container pt-2 bg-white\"
        style=\"overflow-y: auto ; height: 100%\"
      >
  """,
  "        {table_list}",
  "      </div>"
  "    </div>"
  "  </body>",
  "<script>{javascript}</script>",
  "</html>",
))

HEADER = """
<head>
  <link href="vendor/bootstrap.min.css" rel="stylesheet" />
</head>
"""
CSS_STYLES = """
<style>
html, body {
  height: 100% ;
}
</style>
"""

JAVASCRIPT = """

var content = document.getElementById("content") ;
document.getElementById("top").onclick = () => {
  content.scrollTo(0, 0);
} ;
document.getElementById("bottom").onclick = () => {
  content.scrollTo(0, content.scrollHeight);
} ;
var folded = false ;
document.getElementById("folder").onclick = (e) => {
  if (folded) {
    var func = (item) => item.classList.remove("d-none") ;
  } else {
    var func = (item) => item.classList.add("d-none") ;
  }
  Array.prototype.forEach.call(
    document.getElementsByClassName("table"),
    func
  ) ; 
  folded = !folded ;
}
var show_deleted = true ;
document.getElementById("toggle_deleted").onclick = (e) => {
  show_deleted = !show_deleted ;
  if (show_deleted) {
    var func = (item) => item.classList.remove("d-none") ;
  } else {
    var func = (item) => item.classList.add("d-none") ;
  }
  Array.prototype.forEach.call(
    document.getElementsByClassName("deleted"),
    func
  ) ; 
}

Array.prototype.forEach.call(document.getElementsByTagName("h2"), (h2) => {
  var table = h2.nextSibling.nextSibling.nextSibling.nextSibling ;
  h2.onclick = (e) => {
    if (table.classList.contains("d-none")) {
      table.classList.remove("d-none")
    } else {
      table.classList.add("d-none")
    }
  } ;
})
"""

TITLE_TEMPLATE = "<h1>Galaxy - {galaxy_version}</h1>"

TABLE_TEMPLATE = '\n'.join((
  "<div class=\"{classes}\">"
  """
<h2
  style=\"cursor: pointer\"
  title=\"click to fold/unfold the table\"
>{tool_name}</h2>
""",
  "<p>Outputs: {tool_output}</p>"
  "<p>Status: {tool_status}</p>"
  "<table class=\"table table-bordered table-dark table-striped table-hover d-block\">",
  "{table}",
  "</table>",
  "</div>"
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


JOB_CACHE = {}
HISTORY_CACHE = {}
DATASET_CACHE = {}
GLOBAL_CACHE = {
  "jobs": JOB_CACHE,
  "history": HISTORY_CACHE,
  "dataset": DATASET_CACHE,
}

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
    header=HEADER,
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
    for dataset_id_set in job_attr["output_dataset_mapping"].values()
    for dataset_id in dataset_id_set
  ))

def convert_item_to_table(job_attr, dataset_id):
  # if "dataset_attrs" in GLOBAL_CACHE:
  #   encoded_jid = GLOBAL_CACHE["dataset_attrs"][index]["hid"]
  # else:
  encoded_jid = job_attr.get("encoded_id")
  history = HISTORY_CACHE.get(dataset_id, {})
  hid = history.get("hid", "DELETED")
  if job_attr["exit_code"] == 0:
    status = "Ok"
    classes = "alert alert-success"
  else:
    status = "Failed"
    classes = "alert alert-danger"
  if hid == "DELETED":
    classes += " deleted"
  tool_name = job_attr["tool_id"]
  if tool_name.count("/") >= 4:
    tool_name = job_attr["tool_id"].split("/")[-2]
  tool_name = tool_name + " - " + job_attr["tool_version"]
  # print(GLOBAL_CACHE)
  # print(encoded_jid)
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
    # indent(get_table_header(params, keys)),
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
    JOB_CACHE[job_attr["encoded_id"]] = {
      "hid": join_noempty(file["hid"] for file in params["files"]),
      "name": join_noempty(file["name"] for file in params["files"]),
      "extension": join_noempty(file["extension"] for file in params["files"]),
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
        ids.append(file_id)
        if file_id in DATASET_CACHE:
          file_info = DATASET_CACHE[file_id]
          param["name"] = file_info["name"]
          param["hid"] = file_info["hid"]
          param["extension"] = file_info["extension"]
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

  (options, args) = parser.parse_args()
  with open(options.jobs_attrs) as j:
    jobs_attrs = json.load(j)

  with open(options.dataset_attrs) as ds:
    dataset_attrs = json.load(ds)

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
    jobs_attrs = sorted(jobs_attrs, key=lambda x:x["output_datasets"][0])

  with open(options.output, "w") as o:
    o.write(convert_to_html(jobs_attrs, dataset_attrs=dataset_attrs))
