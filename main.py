from openpyxl import Workbook
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.utils import get_column_letter
from openpyxl.workbook.defined_name import DefinedName

# Sample API response (you can replace this with actual API call)
api_data = {
    "event": ["Event1", "Event2"],
    "step": ["Step1", "Step2"],
    "qnastep": ["QnA1", "QnA2"]
}

# Create workbook and sheets
wb = Workbook()
ws_main = wb.active
ws_main.title = "Main"
ws_lists = wb.create_sheet("Lists")

# Step 1: Create lists and define named ranges
for col_idx, (type_name, values) in enumerate(api_data.items(), start=1):
    col_letter = get_column_letter(col_idx)
    ws_lists.cell(row=1, column=col_idx, value=type_name)
    for row_idx, val in enumerate(values, start=2):
        ws_lists.cell(row=row_idx, column=col_idx, value=val)

    # Create a named range for each type (e.g., step = Lists!$A$2:$A$3)
    range_ref = f"Lists!${col_letter}$2:${col_letter}${1 + len(values)}"
    dn = DefinedName(name=type_name, attr_text=range_ref)
    wb.defined_names.add(dn)

# Step 2: Create headers in the main sheet
headers = ["FromType", "FromName", "ToType", "ToName"]
ws_main.append(headers)

# Step 3: Add fixed type dropdowns in FromType and ToType (columns A and C)
type_list = ",".join(api_data.keys())
fromtype_validation = DataValidation(type="list", formula1=f'"{type_list}"', allow_blank=True)
totype_validation = DataValidation(type="list", formula1=f'"{type_list}"', allow_blank=True)

ws_main.add_data_validation(fromtype_validation)
ws_main.add_data_validation(totype_validation)

# Step 4: Add dependent dropdowns (INDIRECT-based) for FromName and ToName
for row in range(2, 101):  # Rows 2 to 100
    # FromType (A), FromName (B)
    fromtype_validation.add(f"A{row}")
    fromname_dv = DataValidation(type="list", formula1=f"=INDIRECT(A{row})", allow_blank=True)
    ws_main.add_data_validation(fromname_dv)
    fromname_dv.add(f"B{row}")

    # ToType (C), ToName (D)
    totype_validation.add(f"C{row}")
    toname_dv = DataValidation(type="list", formula1=f"=INDIRECT(C{row})", allow_blank=True)
    ws_main.add_data_validation(toname_dv)
    toname_dv.add(f"D{row}")

# Save the workbook
wb.save("dynamic_type_dependent_dropdowns.xlsx")
