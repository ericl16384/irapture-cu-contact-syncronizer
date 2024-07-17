

"""

Known issues:
 - Weird concatenation of business name and street (originates from CSV)
 - Sometimes a contact becomes a subtask, rather than a task (is this random or predictable)




"""







print("starting")

import csv, json


error_table = [[
    "source",
    "line",
    "message",
    "notes"
]]

current_error_source = None
current_error_line = None

def log_error(message, notes=""):
    error_table.append((
        current_error_source,
        current_error_line,
        message,
        notes
    ))


def remove_extra_whitespace(txt):
    txt = txt.strip()
    while "  " in txt:
        txt = txt.replace("  ", " ")
    return txt

def extract_phone(txt):
    digits = ""
    for x in txt:
        if x.isdigit():
            digits += x

    if txt in ("", "--"): pass
    elif len(digits) not in (7, 10):
        log_error("phone could not be extracted", txt)

    return digits

def compile_address(street, city, state, zip_code, country):
    out = ""

    if street in ("", "--"): return out
    else: out += street

    if city in ("", "--"): return out
    else: out += ", " + city

    if state in ("", "--"): return out
    else: out += ", " + state

    if zip_code in ("", "--"): return out
    else: out += " " + zip_code

    if country in ("", "--"): return out
    else: out += ", " + country

    return out


export_table = [[
    "Task Name",
    "Description",
    "Assignees",
    "Status",
    "List (ClickUp)",
    "Due Date",
    "Start Date",
    "Date Created",
    "Priority",
    "Tags",
    "Time Estimate",
    "Time Tracked",
    "Subtasks",
    "Checklist",
    "Job Type",
    "Office Phone",
    "Organization Email",
    "Position",
    "Website",
    "Extension",
    "Mailing Address",
    "Mobile Phone",
    "Other Contact",
    "Preferred Communication Method",
    "Time Zone",
    "Title"
]]

export_table_header = {k:v for v,k in enumerate(export_table[0])}
def add_contact(description, name, email, phone, address, website, title="", timezone="", tags=[]):
    row = ["" for i in range(len(export_table[0]))]

    row[export_table_header["Description"]] = description
    row[export_table_header["Task Name"]] = remove_extra_whitespace(name)
    row[export_table_header["Organization Email"]] = email
    row[export_table_header["Office Phone"]] = extract_phone(phone)
    row[export_table_header["Mailing Address"]] = address
    row[export_table_header["Website"]] = website
    row[export_table_header["Title"]] = title
    row[export_table_header["Time Zone"]] = timezone

    row[export_table_header["Tags"]] = ",".join(tags)

    row[export_table_header["Priority"]] = "No Priority"

    export_table.append(row)


# Quickbooks report

print("loading from Quickbooks")

with open("Report 07_16_2024T12_31_17.csv", "r") as f:
    header = None

    current_error_source = "Quickbooks"
    for i, row in enumerate(csv.reader(f)):
        current_error_line = i + 1

        if i == 3:
            assert len(row) == 11
            header = row
        if i < 4: continue

        if row[1] == "":
            log_error("name missing")
            continue

        desc = "exported from Quickbooks: " + json.dumps({k:v for k,v in zip(header, row)})

        street = row[3]
        # street_start = 0
        # while street_start < len(street):
        #     if street[street_start].isdigit():
        #         break
        #     street_start += 1
        # if 
        address = compile_address(street, *row[4:8])

        website = ""
        if "." in row[0] and " " not in row[0]:
            website = row[0]

        tags = ["quickbooks"]
        for i, tag in enumerate(tags):
            tags[i] = tag.strip().lower().replace(" ", "-")
        if len(tags) == 2 and tags[1] == "":
            tags.pop()

        add_contact(
            description=desc,
            name=row[1],
            email=row[2],
            phone=row[9],
            address=address,
            website=website,
            tags=tags,
        )


# Nutshell Contacts

print("loading from Nutshell Contacts")

with open("Contacts.csv", "r") as f:
    header = None

    current_error_source = "Nutshell Contacts"
    for i, row in enumerate(csv.reader(f)):
        current_error_line = i + 1

        if i == 0:
            assert len(row) == 22
            header = row
        if i < 1: continue

        if row[1] == "":
            log_error("name missing")
            continue

        desc = "exported from Nutshell Contacts: " + json.dumps({k:v for k,v in zip(header, row)})

        tags = ["nutshell"]
        tags.extend(row[13].split(","))
        for i, tag in enumerate(tags):
            tags[i] = tag.strip().lower().replace(" ", "-")
        if len(tags) == 2 and tags[1] == "":
            tags.pop()

        add_contact(
            description=desc,
            name=row[1],
            email=row[9],
            phone=row[3],
            address=compile_address(row[14], *row[17:21]),
            website=row[10],
            title=row[21],
            timezone=row[12],
            tags=tags,
        )


print("saving data and errors")

with open("savefile.csv", "w") as f:
    csv.writer(f, lineterminator="\n").writerows(export_table)
with open("errorfile.csv", "w") as f:
    csv.writer(f, lineterminator="\n").writerows(error_table)


print("finished")