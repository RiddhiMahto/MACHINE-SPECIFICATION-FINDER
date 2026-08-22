"""
data_loader.py
----------------
Parses the machine-specification workbook into clean pandas DataFrames.

Expected sheet layout (one sheet per machine type, e.g. "PM", "HB", "Lathe", "GC"):

    Row 0   : Sl. No. | Parameter | Machine No. | ...          (title row, mostly decorative)
    Row 1   : (blank)  | (blank)   | 382 | 385 | 386 | ...      (actual machine numbers)
    Row 2+  : 1 | Max. Length of workpiece | 7000 | None | ... (parameter rows)

Column 0 = Sl. No. (often blank/duplicated for sub-rows -> ignored, we use Parameter as the key)
Column 1 = Parameter name
Column 2..N = one column per machine, values = spec for that parameter

This loader makes NO assumption about how many machines or parameters exist per
sheet, so adding/removing rows or columns in the Excel file "just works" without
touching any code.
"""

from __future__ import annotations
import io
import pandas as pd
import streamlit as st

# Friendly display names / metadata for known sheet codes.
# Any sheet not listed here still works fine - it just falls back to the raw
# sheet name and a generic icon.
SHEET_META = {
    "PM":    {"label": "PM (Plano Miller)",        "icon": "🔧", "color": "#f5a623"},
    "HB":    {"label": "HB (Horizontal Boring)",   "icon": "⚙️", "color": "#4a9eff"},
    "LATHE": {"label": "LT (Lathe)",                "icon": "🛠️", "color": "#34d399"},
    "LT":    {"label": "LT (Lathe)",                "icon": "🛠️", "color": "#34d399"},
    "GC":    {"label": "GC (Gear Cutting/Hobbing)", "icon": "⚒️", "color": "#c084fc"},
}

DEFAULT_META = {"icon": "🏭", "color": "#94a3b8"}


def _clean_label(val) -> str:
    """Format a machine-number cell nicely (386.0 -> '386', 386 -> '386')."""
    if isinstance(val, float) and val.is_integer():
        return str(int(val))
    return str(val).strip()


def get_sheet_meta(sheet_name: str) -> dict:
    meta = SHEET_META.get(sheet_name.strip().upper())
    if meta:
        return meta
    return {"label": sheet_name, **DEFAULT_META}


@st.cache_data(show_spinner=False)
def load_workbook(file_bytes: bytes) -> dict[str, pd.DataFrame]:
    """
    Parse every sheet in the workbook into a dict of:
        { sheet_name: DataFrame(index=Parameter, columns=Machine No., values=spec) }

    Blank / fully-empty parameter rows are dropped. Machine number columns with
    no header value are dropped. Values are left as-is (numbers stay numeric,
    text like 'ISO 60' stays text).
    """
    xls = pd.ExcelFile(io.BytesIO(file_bytes))
    result: dict[str, pd.DataFrame] = {}

    for sheet_name in xls.sheet_names:
        raw = pd.read_excel(xls, sheet_name=sheet_name, header=None)
        if raw.shape[0] < 2 or raw.shape[1] < 3:
            continue  # not enough rows/cols to be a valid spec sheet

        # Row 1 (index 1) holds the machine numbers, starting at column 2
        machine_row = raw.iloc[1, 2:]
        machine_cols = []   # list of (dataframe_column_index, machine_no)
        for col_idx, val in machine_row.items():
            if pd.notna(val):
                machine_cols.append((col_idx, _clean_label(val)))

        if not machine_cols:
            continue

        records = []
        for row_idx in range(2, raw.shape[0]):
            param_name = raw.iat[row_idx, 1]
            if pd.isna(param_name) or str(param_name).strip() == "":
                continue
            param_name = str(param_name).strip()

            row_data = {"Parameter": param_name}
            for col_idx, machine_no in machine_cols:
                val = raw.iat[row_idx, col_idx]
                if pd.isna(val):
                    row_data[machine_no] = None
                elif isinstance(val, float) and val.is_integer():
                    row_data[machine_no] = int(val)
                else:
                    row_data[machine_no] = val
            records.append(row_data)

        if not records:
            continue

        df = pd.DataFrame(records).set_index("Parameter")
        # Deduplicate parameter names that repeat (keep first occurrence's row,
        # but merge in any values a later duplicate row might carry)
        df = df.groupby(level=0, sort=False).first()

        result[sheet_name] = df

    return result


def load_default_workbook() -> dict[str, pd.DataFrame]:
    """Load the workbook bundled in data/machine_specs.xlsx."""
    with open("data/machine_specs.xlsx", "rb") as f:
        return load_workbook(f.read())
