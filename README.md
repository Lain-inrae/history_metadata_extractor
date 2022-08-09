


History Metadata Extractor
===

This tool xtracts informations from the `jobs_attrs.txt` and
`datasets_attrs` files in exported histories, and produces an html page
showing these informations in a kawaii table.


Each history entry is displayed like the following:

```
[{ID}] - {tool name} - {tool version}
status: {text status}({error code})
{table}
```
note that `[ID]` is replaced by `[DELETED]` if the dataset has been deleted.
the error code can be "None" sometimes, if not provided in the archive.

The table is always presented like the following:
```
|              | value | name | extension | hid |
| parameters 1 |       |      |           |     |
| parameters 2 |       |      |           |     |
| parameters 3 |       |      |           |     |
| ...          | ...   | ...  | ...       | ... |
| parameters n |       |      |           |     |
```

The `value` is the textual representation of the parameter provided.
For files, the value is not very interesting but the name, extension and
history ID should be meaningfull to you.
The hid value is the same number as the one found between brackets.
So, if a file with hid = 42 has been input to your tool, you can find where
this file comes from, from its hid.
The only exception is for the `__DATA_FETSH__` tool. This tool is invoked the
when the "upload" button is pressed, so the hid for these files will always be
"_weird_".

examples
===

<div style="width: 760px;">

Produced tables
---

Some tables are produced to display the tool's parameters you used.

![Example a produced tables](./example/shown_tables.png)

Tables can be hidden
---

We can click on the "fold/unforld tables" button to hide/show the tables.
The table of one dataset can be fold/unfold when clicking on the title
of the dataset (for example: `[42] - __DATA_FETCH__ - 0.1.0`)

![Tables can be hidden](./example/hidden_tables.png)

Displays only non-deleted datasets
---

"show/hide deleted" will hide deleted datasets. Re-click it to re-display
deleted datasets.
![Displays only non-deleted datasets](./example/not_deleted.png)

</div>

An [example.html](example/example.html) file can be found in the `example`
directory.

Metadata
===

 * **@AUTHOR**: Lain Pavot - lain.pavot@inrae.fr
 * **@CREATION DATE**: 22/06/2022
 * **@LAST UPDATE DATE**: 09/08/2022
 * **@VERSION**: 0.2.0
