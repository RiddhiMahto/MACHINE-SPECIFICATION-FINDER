
import streamlit as st
import pandas as pd
import io

# ================= BUILT-IN MACHINE TYPE DEFINITIONS =================

MACHINE_TYPES = ["PM (Plano Miller)", "HB (Horizontal Boring)", "LT (Lathe)"]

# ─── PM ─────────────────────────────────────────────────────────────────────
PM_SPECS = [
    "Max. Length of workpiece", "Max. width of workpiece", "Max. Height of workpiece",
    "Passage between column", "Length of table", "Width of table",
    "Table travel - X axis", "Cross travel - Y axis", "Ram travel - Z axis",
    "Vertical travel - W axis", "Max. angle of swivel of head",
    "Max. Travel of spindle sleeve", "Spindle Dia.", "Spindle taper",
    "Load capacity (Kg)", "Ram/Spindle travel", "Maximum RPM",
]
PM_UNITS = {
    "Max. Length of workpiece": "mm", "Max. width of workpiece": "mm",
    "Max. Height of workpiece": "mm", "Passage between column": "mm",
    "Length of table": "mm", "Width of table": "mm",
    "Table travel - X axis": "mm", "Cross travel - Y axis": "mm",
    "Ram travel - Z axis": "mm", "Vertical travel - W axis": "mm",
    "Max. angle of swivel of head": "", "Max. Travel of spindle sleeve": "mm",
    "Spindle Dia.": "mm", "Spindle taper": "",
    "Load capacity (Kg)": "Kg", "Ram/Spindle travel": "mm", "Maximum RPM": "RPM",
}
PM_GROUPS = {
    "Workpiece Envelope": ["Max. Length of workpiece", "Max. width of workpiece", "Max. Height of workpiece"],
    "Table Dimensions": ["Length of table", "Width of table", "Passage between column", "Load capacity (Kg)"],
    "Axis Travel": ["Table travel - X axis", "Cross travel - Y axis", "Ram travel - Z axis", "Vertical travel - W axis", "Ram/Spindle travel"],
    "Spindle & Head": ["Max. angle of swivel of head", "Max. Travel of spindle sleeve", "Spindle Dia.", "Spindle taper", "Maximum RPM"],
}
_pm_raw = {
    382: {"Max. width of workpiece": 800, "Max. Height of workpiece": 800, "Length of table": 3000, "Width of table": 300, "Table travel - X axis": 3550, "Max. angle of swivel of head": "30 Deg.", "Max. Travel of spindle sleeve": 200},
    385: {"Max. width of workpiece": 2800, "Max. Height of workpiece": 2500, "Passage between column": 3300, "Length of table": 9200, "Width of table": 2800, "Spindle Dia.": 200, "Spindle taper": "ISO 60"},
    386: {"Passage between column": 3050, "Width of table": 2500, "Table travel - X axis": 6700, "Vertical travel - W axis": 2000, "Load capacity (Kg)": 98000, "Ram/Spindle travel": 1000},
    387: {"Max. Length of workpiece": 7000, "Max. width of workpiece": 1500, "Max. Height of workpiece": 1500, "Maximum RPM": 900},
    388: {"Passage between column": 2500, "Length of table": 6000, "Width of table": 2200, "Table travel - X axis": 6000, "Cross travel - Y axis": 3290, "Ram travel - Z axis": 800, "Vertical travel - W axis": 3450, "Load capacity (Kg)": 40000},
    389: {"Max. Height of workpiece": 2500, "Passage between column": 2500, "Length of table": 5000, "Width of table": 2000, "Table travel - X axis": 6750, "Cross travel - Y axis": 4050, "Ram travel - Z axis": 710, "Vertical travel - W axis": 1700, "Max. angle of swivel of head": "45 Deg.", "Spindle taper": "ISO 50", "Load capacity (Kg)": 20000, "Maximum RPM": 3000},
    390: {"Passage between column": 5000, "Width of table": 4000, "Vertical travel - W axis": 2000},
    391: {"Passage between column": 2500, "Length of table": 3000, "Width of table": 2000, "Table travel - X axis": 4000, "Cross travel - Y axis": 3500, "Ram travel - Z axis": 1500, "Vertical travel - W axis": 1500, "Load capacity (Kg)": 10000, "Maximum RPM": 6000},
    402: {"Max. Length of workpiece": 6000, "Max. width of workpiece": 1500, "Max. Height of workpiece": 1500, "Maximum RPM": 900},
}
PM_DATA = {mn: {spec: raw.get(spec, None) for spec in PM_SPECS} for mn, raw in _pm_raw.items()}

# ─── HB ─────────────────────────────────────────────────────────────────────
HB_SPECS = [
    "Spindle Diameter", "Max. Dia. Of Job rotated on table", "Tool taper", "RAM Section",
    "Travel of column X axis", "Vertical travel Y axis", "Spindle travel Z axis",
    "RAM travel W axis", "Max. Travel Z + W axes", "Max. RPM", "Table dimension",
    "Travel of table V axis/ Travel of column", "Load capacity (Kg)",
    "Min. Distance between spindle centre and top of table",
]
HB_UNITS = {
    "Spindle Diameter": "mm", "Max. Dia. Of Job rotated on table": "mm",
    "Tool taper": "", "RAM Section": "mm",
    "Travel of column X axis": "mm", "Vertical travel Y axis": "mm",
    "Spindle travel Z axis": "mm", "RAM travel W axis": "mm",
    "Max. Travel Z + W axes": "mm", "Max. RPM": "RPM",
    "Table dimension": "mm", "Travel of table V axis/ Travel of column": "mm",
    "Load capacity (Kg)": "Kg", "Min. Distance between spindle centre and top of table": "mm",
}
HB_GROUPS = {
    "Spindle & Head": ["Spindle Diameter", "Tool taper", "RAM Section", "Max. RPM"],
    "Axis Travel": ["Travel of column X axis", "Vertical travel Y axis", "Spindle travel Z axis", "RAM travel W axis", "Max. Travel Z + W axes", "Travel of table V axis/ Travel of column"],
    "Table & Workpiece": ["Table dimension", "Max. Dia. Of Job rotated on table", "Load capacity (Kg)", "Min. Distance between spindle centre and top of table"],
}
_hb_raw = {
    305: {"Spindle Diameter": 100, "Tool taper": "Morse 6", "Travel of column X axis": 1600, "Max. RPM": 1120, "Table dimension": "1250 x 1250", "Travel of table V axis/ Travel of column": 1250, "Load capacity (Kg)": 3000, "Min. Distance between spindle centre and top of table": 0},
    311: {"Spindle Diameter": 125, "Tool taper": "M 80", "Travel of column X axis": 1800, "Vertical travel Y axis": 1500, "Spindle travel Z axis": 1100, "Table dimension": "2000 x 1800", "Travel of table V axis/ Travel of column": 2000, "Load capacity (Kg)": 6000},
    320: {"Spindle Diameter": 200, "Max. Dia. Of Job rotated on table": 12400, "Tool taper": "M 120", "RAM Section": "530 x 530", "Travel of column X axis": 8000, "Vertical travel Y axis": 3150, "Spindle travel Z axis": 2000, "RAM travel W axis": 1600, "Max. Travel Z + W axes": 2000, "Max. RPM": 630, "Table dimension": "3150 x 2800", "Travel of table V axis/ Travel of column": 2000, "Load capacity (Kg)": 32000},
    322: {"Spindle Diameter": 200, "Max. Dia. Of Job rotated on table": 10000, "Tool taper": "ISO 60", "RAM Section": "720 x 460", "Travel of column X axis": 8000, "Vertical travel Y axis": 4000, "Spindle travel Z axis": 1400, "RAM travel W axis": 1200, "Max. Travel Z + W axes": 2600, "Max. RPM": 800, "Table dimension": "3000 x 2500", "Travel of table V axis/ Travel of column": 2000, "Load capacity (Kg)": 60000, "Min. Distance between spindle centre and top of table": 500},
    323: {"Max. Dia. Of Job rotated on table": 1600, "Travel of column X axis": 2000, "Vertical travel Y axis": 1250, "Spindle travel Z axis": 800, "Table dimension": "2000 x 1600", "Travel of table V axis/ Travel of column": 1000, "Load capacity (Kg)": 12000},
    324: {"Spindle Diameter": 203.4, "Max. Dia. Of Job rotated on table": 14000, "Tool taper": "ISO 60", "RAM Section": "440 x 480", "Travel of column X axis": 10000, "Vertical travel Y axis": 4400, "Spindle travel Z axis": 1000, "RAM travel W axis": 1200, "Max. Travel Z + W axes": 2200, "Max. RPM": 800, "Table dimension": "4000 x 4000", "Travel of table V axis/ Travel of column": 3000, "Load capacity (Kg)": 100000, "Min. Distance between spindle centre and top of table": 270},
    325: {"Tool taper": "ISO 45", "Travel of column X axis": 1750, "Vertical travel Y axis": 1300, "Max. RPM": 3600, "Table dimension": "1000 x 1000", "Travel of table V axis/ Travel of column": 1000, "Load capacity (Kg)": 1800, "Min. Distance between spindle centre and top of table": 75},
    326: {"Spindle Diameter": 130, "Travel of column X axis": 2000, "Vertical travel Y axis": 2000, "Spindle travel Z axis": 800, "Max. RPM": 1000, "Table dimension": "1800 x 1600", "Travel of table V axis/ Travel of column": 1250},
    327: {"Spindle Diameter": 200, "Tool taper": "ISO 60", "RAM Section": "520 x 520", "Travel of column X axis": 10000, "Vertical travel Y axis": 4000, "Spindle travel Z axis": 2000, "RAM travel W axis": 1600},
    328: {"Spindle Diameter": 200, "Tool taper": "ISO 60", "RAM Section": "520 x 520", "Travel of column X axis": 10500, "Vertical travel Y axis": 4500, "Spindle travel Z axis": 1600, "RAM travel W axis": 1400, "Max. Travel Z + W axes": 3000, "Max. RPM": 1600, "Table dimension": "4000 x 4000", "Travel of table V axis/ Travel of column": 4000, "Load capacity (Kg)": 100000},
    329: {"Spindle Diameter": 200, "Tool taper": "ISO 60", "Travel of column X axis": 9500, "Vertical travel Y axis": 4000, "Spindle travel Z axis": 2000, "RAM travel W axis": 1600, "Table dimension": "4000 x 3500", "Travel of table V axis/ Travel of column": 2700, "Load capacity (Kg)": 63000},
    330: {"Spindle Diameter": 125, "Travel of column X axis": 3000, "Vertical travel Y axis": 2000, "Spindle travel Z axis": 800, "Max. RPM": 1600, "Table dimension": "2000 x 1600", "Travel of table V axis/ Travel of column": 1500, "Load capacity (Kg)": 15000},
    331: {"Spindle Diameter": 200, "Tool taper": "ISO 60", "Travel of column X axis": 4000, "Vertical travel Y axis": 3150, "Spindle travel Z axis": 2000, "RAM travel W axis": 1600, "Table dimension": "3600 x 3600", "Travel of table V axis/ Travel of column": 2000, "Load capacity (Kg)": 35000},
    332: {"Spindle Diameter": 160, "Tool taper": "M 100", "Travel of column X axis": 3250, "Vertical travel Y axis": 3150, "Spindle travel Z axis": 1600, "RAM travel W axis": 1250, "Table dimension": "2000 x 2000", "Travel of table V axis/ Travel of column": 1200, "Load capacity (Kg)": 20000},
    334: {"Spindle Diameter": 160, "Tool taper": "ISO 60", "Travel of column X axis": 4000, "Vertical travel Y axis": 3000, "Spindle travel Z axis": 1000, "Max. RPM": 2000, "Table dimension": "3000 x 2500", "Travel of table V axis/ Travel of column": 1600, "Load capacity (Kg)": 25000},
    335: {"Spindle Diameter": 160, "Tool taper": "ISO 60", "Travel of column X axis": 4000, "Vertical travel Y axis": 3000, "Spindle travel Z axis": 1000, "Max. RPM": 2000, "Table dimension": "3000 x 2500", "Travel of table V axis/ Travel of column": 1600, "Load capacity (Kg)": 25000},
    337: {},
    338: {},
    339: {"Spindle Diameter": 120, "Travel of column X axis": 1250, "Vertical travel Y axis": 1250, "Spindle travel Z axis": 1000, "Max. RPM": 8000, "Table dimension": "1250 x 1100", "Load capacity (Kg)": 2800},
    340: {"Travel of column X axis": 3000, "Vertical travel Y axis": 2000, "Spindle travel Z axis": 2000, "Table dimension": "2000 x 1600", "Travel of table V axis/ Travel of column": 800, "Load capacity (Kg)": 20000},
    341: {"Travel of column X axis": 3000, "Vertical travel Y axis": 2000, "Spindle travel Z axis": 2000, "Table dimension": "2000 x 1600", "Travel of table V axis/ Travel of column": 800, "Load capacity (Kg)": 20000},
    342: {},
}
HB_DATA = {mn: {spec: raw.get(spec, None) for spec in HB_SPECS} for mn, raw in _hb_raw.items()}

# ─── LT (Lathe) ─────────────────────────────────────────────────────────────
LT_SPECS = [
    "Swing over bed", "Swing over carriage", "Distance between centres",
    "Maximum wt. bet. Centres", "Maximum weight between centres without steady",
    "Maximum weight between centres with one steady", "Maximum weight between centres with two steady",
    "Cross slide travel (X axis)", "Maximum movement in Z axis", "Width of bed",
    "Spindle bore dia.", "Minimum dia. Of steady rest", "Maximum dia. Of steady rest",
    "Tail stock quill dia.", "Tail stock quill travel",
]
LT_UNITS = {
    "Swing over bed": "mm", "Swing over carriage": "mm", "Distance between centres": "mm",
    "Maximum wt. bet. Centres": "Kg", "Maximum weight between centres without steady": "Kg",
    "Maximum weight between centres with one steady": "Kg", "Maximum weight between centres with two steady": "Kg",
    "Cross slide travel (X axis)": "mm", "Maximum movement in Z axis": "mm", "Width of bed": "mm",
    "Spindle bore dia.": "mm", "Minimum dia. Of steady rest": "mm", "Maximum dia. Of steady rest": "mm",
    "Tail stock quill dia.": "mm", "Tail stock quill travel": "mm",
}
LT_GROUPS = {
    "Swing & Centres": ["Swing over bed", "Swing over carriage", "Distance between centres"],
    "Weight Capacity": ["Maximum wt. bet. Centres", "Maximum weight between centres without steady",
                        "Maximum weight between centres with one steady", "Maximum weight between centres with two steady"],
    "Bed & Axis Travel": ["Width of bed", "Cross slide travel (X axis)", "Maximum movement in Z axis"],
    "Spindle & Tailstock": ["Spindle bore dia.", "Minimum dia. Of steady rest", "Maximum dia. Of steady rest",
                            "Tail stock quill dia.", "Tail stock quill travel"],
}
_lt_raw = {
    160: {"Swing over bed": 2000, "Swing over carriage": 1600, "Distance between centres": 8000, "Maximum wt. bet. Centres": 50000, "Width of bed": 1700, "Maximum dia. Of steady rest": 1000},
    174: {"Swing over bed": 1520, "Swing over carriage": 1100, "Distance between centres": 4000, "Maximum wt. bet. Centres": 10000, "Cross slide travel (X axis)": 750, "Spindle bore dia.": 104, "Minimum dia. Of steady rest": 140, "Maximum dia. Of steady rest": 600, "Tail stock quill travel": 300},
    176: {"Swing over bed": 3000, "Swing over carriage": 2500, "Distance between centres": 6000, "Maximum wt. bet. Centres": 30000, "Cross slide travel (X axis)": 1000, "Width of bed": 1500, "Spindle bore dia.": 105, "Tail stock quill dia.": 280, "Tail stock quill travel": 200},
    177: {"Swing over bed": 800, "Swing over carriage": 600, "Distance between centres": 3000, "Width of bed": 750, "Spindle bore dia.": 104, "Tail stock quill travel": None},
    178: {"Swing over bed": 800, "Swing over carriage": 600, "Distance between centres": 4000, "Width of bed": 750},
    179: {"Swing over bed": 800, "Swing over carriage": 600, "Distance between centres": 4000, "Width of bed": 750, "Spindle bore dia.": 104},
    180: {"Swing over bed": 1600, "Swing over carriage": 1320, "Distance between centres": 5000, "Width of bed": 1300, "Spindle bore dia.": 150, "Tail stock quill dia.": 240, "Tail stock quill travel": 270,
          "Maximum weight between centres without steady": 10000, "Maximum weight between centres with one steady": 17500, "Maximum weight between centres with two steady": 22500},
    181: {"Swing over bed": 1300, "Swing over carriage": 1000, "Distance between centres": 4000, "Maximum wt. bet. Centres": 10000, "Cross slide travel (X axis)": 580, "Spindle bore dia.": 110, "Tail stock quill dia.": 180, "Tail stock quill travel": 200},
    182: {"Swing over bed": 1300, "Swing over carriage": 1000, "Distance between centres": 4000, "Maximum wt. bet. Centres": 10000, "Cross slide travel (X axis)": 580, "Spindle bore dia.": 110, "Tail stock quill dia.": 180, "Tail stock quill travel": 200},
    183: {"Swing over bed": 1300, "Swing over carriage": 1000, "Distance between centres": 4000, "Maximum wt. bet. Centres": 10000, "Cross slide travel (X axis)": 580, "Spindle bore dia.": 110, "Tail stock quill dia.": 180, "Tail stock quill travel": 200},
    184: {"Swing over bed": 650, "Swing over carriage": 380, "Distance between centres": 2000, "Maximum wt. bet. Centres": 3000, "Spindle bore dia.": 105, "Tail stock quill dia.": 100, "Tail stock quill travel": 180},
    172: {"Swing over bed": 610, "Swing over carriage": 350, "Distance between centres": 2000, "Maximum wt. bet. Centres": 1000, "Cross slide travel (X axis)": 350, "Spindle bore dia.": 103, "Tail stock quill travel": 125},
    103: {"Swing over bed": 530, "Swing over carriage": 360, "Distance between centres": 3000, "Cross slide travel (X axis)": 255, "Width of bed": 325, "Spindle bore dia.": 42, "Tail stock quill travel": 200},
    111: {"Swing over bed": 575, "Swing over carriage": 545, "Distance between centres": 3000, "Cross slide travel (X axis)": 300, "Width of bed": 415},
    120: {"Swing over bed": 900, "Swing over carriage": 570, "Distance between centres": 4000, "Spindle bore dia.": 105, "Tail stock quill travel": None},
    121: {"Swing over bed": 900, "Swing over carriage": 570, "Distance between centres": 3000, "Spindle bore dia.": 105, "Tail stock quill travel": 325},
    175: {"Swing over bed": 900, "Swing over carriage": 570, "Distance between centres": 3000, "Maximum movement in Z axis": 4000, "Spindle bore dia.": 105, "Tail stock quill travel": 325},
    124: {"Swing over bed": 900, "Swing over carriage": 570, "Distance between centres": 2000, "Tail stock quill travel": 325},
    127: {"Swing over bed": 1400, "Swing over carriage": 1100, "Distance between centres": 6000, "Maximum wt. bet. Centres": 20000},
}
LT_DATA = {mn: {spec: raw.get(spec, None) for spec in LT_SPECS} for mn, raw in _lt_raw.items()}

# ================= REGISTRY =================

BUILTIN_REGISTRY = {
    "PM (Plano Miller)":        (PM_DATA, PM_SPECS, PM_UNITS, PM_GROUPS),
    "HB (Horizontal Boring)":   (HB_DATA, HB_SPECS, HB_UNITS, HB_GROUPS),
    "LT (Lathe)":               (LT_DATA, LT_SPECS, LT_UNITS, LT_GROUPS),
}

TYPE_ACCENT = {
    "PM (Plano Miller)":       "#f0a500",
    "HB (Horizontal Boring)":  "#4a9eff",
    "LT (Lathe)":              "#00c17c",
}
UPLOADED_ACCENT = "#c084fc"

# ================= HELPERS =================

def format_value(spec, value, units):
    if value is None:
        return "—"
    unit = units.get(spec, "")
    if unit and not str(value).endswith(unit):
        return "{} {}".format(value, unit)
    return str(value)

def build_comparison_df(machines, mdata, specs, units):
    rows = []
    for spec in specs:
        unit = units.get(spec, "")
        label = "{} ({})".format(spec, unit) if unit else spec
        row = {"Parameter": label}
        for m in machines:
            val = mdata[m].get(spec)
            row["Machine {}".format(m)] = val if val is not None else "—"
        rows.append(row)
    return pd.DataFrame(rows)

def count_available(mn, mdata, specs):
    return sum(1 for s in specs if mdata[mn].get(s) is not None)

def get_min_max_machine(spec, mdata):
    values = []
    for mn, d in mdata.items():
        v = d.get(spec)
        if isinstance(v, (int, float)):
            values.append((mn, v))
    if not values:
        return None
    max_machine, max_value = max(values, key=lambda x: x[1])
    min_machine, min_value = min(values, key=lambda x: x[1])
    return {"max_machine": max_machine, "max_value": max_value,
            "min_machine": min_machine, "min_value": min_value}

def parse_uploaded_excel(uploaded_file):
    """
    Parse an uploaded Excel file into (mdata, specs, units, groups).

    Expected Excel format — TWO SUPPORTED LAYOUTS:

    LAYOUT A — Parameters as rows (recommended):
      • Column 1 : "Parameter" (parameter names)
      • Column 2 : "Unit"      (optional — units for each parameter)
      • Column 3+ : Machine numbers as headers (e.g. 101, 102, ...)

    LAYOUT B — Parameters as columns:
      • Row 1  : header row — first cell "Machine No." or "Machine", rest = parameter names
      • Row 1b : optional second header row with units (if first non-number row after header)
      • Remaining rows: each row = one machine

    Returns (mdata, specs, units, groups) or raises ValueError with a user-friendly message.
    """
    try:
        df_raw = pd.read_excel(uploaded_file, header=None)
    except Exception as e:
        raise ValueError(f"Could not read Excel file: {e}")

    if df_raw.empty:
        raise ValueError("The uploaded Excel file is empty.")

    # Detect layout by checking first cell
    first_cell = str(df_raw.iloc[0, 0]).strip().lower()

    # ── LAYOUT A: first column = "Parameter" ─────────────────────────────────
    if first_cell in ("parameter", "parameters", "spec", "specification", "specifications"):
        has_unit_col = str(df_raw.iloc[0, 1]).strip().lower() in ("unit", "units") if df_raw.shape[1] > 1 else False

        if has_unit_col:
            machine_col_start = 2
        else:
            machine_col_start = 1

        # Machine numbers from header row
        machine_numbers = []
        for col_idx in range(machine_col_start, df_raw.shape[1]):
            val = df_raw.iloc[0, col_idx]
            if pd.notna(val) and str(val).strip():
                try:
                    machine_numbers.append(int(float(str(val).strip())))
                except ValueError:
                    machine_numbers.append(str(val).strip())

        if not machine_numbers:
            raise ValueError("No machine numbers found in the header row.")

        specs = []
        units = {}
        mdata = {mn: {} for mn in machine_numbers}

        for row_idx in range(1, df_raw.shape[0]):
            param = str(df_raw.iloc[row_idx, 0]).strip()
            if not param or param.lower() in ("nan", "none", ""):
                continue
            specs.append(param)
            unit = ""
            if has_unit_col:
                u = df_raw.iloc[row_idx, 1]
                unit = "" if pd.isna(u) else str(u).strip()
            units[param] = unit
            for i, mn in enumerate(machine_numbers):
                col_idx = machine_col_start + i
                if col_idx < df_raw.shape[1]:
                    raw_val = df_raw.iloc[row_idx, col_idx]
                    if pd.isna(raw_val) or str(raw_val).strip() in ("", "nan", "None", "-", "—"):
                        mdata[mn][param] = None
                    else:
                        try:
                            mdata[mn][param] = float(raw_val) if "." in str(raw_val) else int(float(str(raw_val)))
                        except (ValueError, TypeError):
                            mdata[mn][param] = str(raw_val).strip()
                else:
                    mdata[mn][param] = None

    # ── LAYOUT B: first column = "Machine No." ───────────────────────────────
    else:
        # Try to use first row as header
        header_row = df_raw.iloc[0]
        params = []
        param_col_start = 1
        for col_idx in range(param_col_start, df_raw.shape[1]):
            p = str(header_row[col_idx]).strip()
            if p and p.lower() not in ("nan", "none"):
                params.append(p)

        if not params:
            raise ValueError(
                "Could not detect layout. Please ensure your Excel file has:\n"
                "• Layout A: First column = 'Parameter', second = 'Unit' (optional), then machine numbers as headers\n"
                "• Layout B: First column = 'Machine No.', then parameter names as headers"
            )

        specs = params
        units = {p: "" for p in params}

        # Check if second row looks like a units row (all text, no numbers)
        data_start = 1
        if df_raw.shape[0] > 1:
            second_row = df_raw.iloc[1]
            is_units_row = True
            for col_idx in range(param_col_start, param_col_start + len(params)):
                if col_idx < df_raw.shape[1]:
                    v = str(second_row[col_idx]).strip()
                    if v and v.lower() not in ("nan", "none"):
                        try:
                            float(v)
                            is_units_row = False
                            break
                        except ValueError:
                            pass
            if is_units_row:
                for i, p in enumerate(params):
                    col_idx = param_col_start + i
                    if col_idx < df_raw.shape[1]:
                        u = str(second_row[col_idx]).strip()
                        units[p] = "" if u.lower() in ("nan", "none", "") else u
                data_start = 2

        mdata = {}
        for row_idx in range(data_start, df_raw.shape[0]):
            mn_raw = df_raw.iloc[row_idx, 0]
            if pd.isna(mn_raw) or str(mn_raw).strip() in ("", "nan"):
                continue
            try:
                mn = int(float(str(mn_raw).strip()))
            except ValueError:
                mn = str(mn_raw).strip()
            mdata[mn] = {}
            for i, p in enumerate(params):
                col_idx = param_col_start + i
                if col_idx < df_raw.shape[1]:
                    raw_val = df_raw.iloc[row_idx, col_idx]
                    if pd.isna(raw_val) or str(raw_val).strip() in ("", "nan", "None", "-", "—"):
                        mdata[mn][p] = None
                    else:
                        try:
                            mdata[mn][p] = float(raw_val) if "." in str(raw_val) else int(float(str(raw_val)))
                        except (ValueError, TypeError):
                            mdata[mn][p] = str(raw_val).strip()
                else:
                    mdata[mn][p] = None

    if not mdata:
        raise ValueError("No machine data rows were found in the uploaded file.")

    # Auto-generate a single group containing all specs
    groups = {"All Parameters": specs}

    return mdata, specs, units, groups


def generate_template_excel(layout="A"):
    """Generate a downloadable Excel template for users to fill in."""
    output = io.BytesIO()
    if layout == "A":
        # Layout A: Parameters as rows
        sample_data = {
            "Parameter": ["Spindle Diameter", "Max. RPM", "Table dimension", "Load capacity (Kg)"],
            "Unit": ["mm", "RPM", "mm", "Kg"],
            "101": [150, 1200, "2000 x 1600", 15000],
            "102": [200, 800, "3000 x 2500", 30000],
            "103": [None, 1600, "1500 x 1200", 8000],
        }
        df = pd.DataFrame(sample_data)
    else:
        # Layout B: Parameters as columns
        sample_data = {
            "Machine No.": ["Unit", 101, 102, 103],
            "Spindle Diameter": ["mm", 150, 200, None],
            "Max. RPM": ["RPM", 1200, 800, 1600],
            "Table dimension": ["mm", "2000 x 1600", "3000 x 2500", "1500 x 1200"],
            "Load capacity (Kg)": ["Kg", 15000, 30000, 8000],
        }
        df = pd.DataFrame(sample_data)

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Machine Specs")
    output.seek(0)
    return output.getvalue()


# ================= PAGE CONFIG =================

st.set_page_config(
    page_title="Machine Specification System",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ================= SESSION STATE =================

if "machine_type" not in st.session_state:
    st.session_state["machine_type"] = MACHINE_TYPES[0]
if "uploaded_data" not in st.session_state:
    st.session_state["uploaded_data"] = None   # (name, mdata, specs, units, groups)
if "active_source" not in st.session_state:
    st.session_state["active_source"] = "builtin"   # "builtin" or "uploaded"

# ================= GLOBAL CSS =================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;600&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.stApp { background-color: #0f1117; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 0 !important; padding-bottom: 2rem !important; max-width: 1400px !important; }
.header-banner { background: linear-gradient(135deg,#1a1d27 0%,#12151f 100%); border-bottom: 2px solid #f0a500; padding: 1.4rem 2.5rem; display: flex; align-items: center; justify-content: space-between; }
.header-title { font-size: 1.5rem; font-weight: 600; color: #ffffff; letter-spacing: 0.04em; text-transform: uppercase; margin: 0; }
.header-subtitle { font-size: 0.78rem; color: #f0a500; letter-spacing: 0.12em; text-transform: uppercase; margin-top: 2px; }
.header-badge { background: #f0a500; color: #0f1117; font-size: 0.7rem; font-weight: 600; letter-spacing: 0.1em; padding: 4px 12px; border-radius: 2px; text-transform: uppercase; }
.metric-card { background: #1a1d27; border: 1px solid #2a2e3e; border-radius: 4px; padding: 1.2rem 1.4rem; text-align: center; }
.metric-label { font-size: 0.68rem; letter-spacing: 0.12em; text-transform: uppercase; color: #6b7080; margin-bottom: 0.4rem; }
.metric-value { font-family: 'JetBrains Mono', monospace; font-size: 1.6rem; font-weight: 600; color: #f0a500; line-height: 1; }
.metric-unit { font-size: 0.75rem; color: #8b90a0; margin-top: 4px; }
.stSelectbox > div > div, .stMultiSelect > div > div { background-color: #1a1d27 !important; border-color: #2a2e3e !important; color: #e8eaf0 !important; border-radius: 4px !important; }
.stSelectbox label, .stMultiSelect label, .stCheckbox label { color: #8b90a0 !important; font-size: 0.75rem !important; font-weight: 500 !important; letter-spacing: 0.08em !important; text-transform: uppercase !important; }
.stTabs [data-baseweb="tab-list"] { background-color: #1a1d27; border-bottom: 1px solid #2a2e3e; gap: 0; }
.stTabs [data-baseweb="tab"] { background-color: transparent !important; color: #6b7080 !important; font-size: 0.75rem !important; font-weight: 600 !important; letter-spacing: 0.1em !important; text-transform: uppercase !important; border-radius: 0 !important; padding: 0.8rem 1.8rem !important; border-bottom: 2px solid transparent !important; }
.stTabs [aria-selected="true"] { color: #f0a500 !important; border-bottom: 2px solid #f0a500 !important; background-color: transparent !important; }
.stDataFrame { border: 1px solid #2a2e3e !important; border-radius: 4px !important; }
.stDownloadButton button { background: transparent !important; border: 1px solid #f0a500 !important; color: #f0a500 !important; font-size: 0.75rem !important; font-weight: 600 !important; letter-spacing: 0.1em !important; text-transform: uppercase !important; border-radius: 2px !important; padding: 0.5rem 1.2rem !important; }
.stDownloadButton button:hover { background: #f0a500 !important; color: #0f1117 !important; }
div[data-testid="stButton"] button { background: transparent !important; border: 1px solid #00c17c !important; color: #00c17c !important; font-size: 0.8rem !important; font-weight: 600 !important; letter-spacing: 0.12em !important; text-transform: uppercase !important; border-radius: 2px !important; padding: 0.6rem 1.2rem !important; width: 100% !important; }
div[data-testid="stButton"] button:hover { background: #00c17c !important; color: #0f1117 !important; }
div[data-testid="stAlert"] { border-radius: 4px !important; font-size: 0.82rem !important; }
.upload-box { background: #12151f; border: 2px dashed #2a2e3e; border-radius: 6px; padding: 1.5rem 2rem; margin-bottom: 1rem; }
.upload-box:hover { border-color: #c084fc; }
.source-badge-builtin { display:inline-block; background:#1a1d27; border:1px solid #f0a500; color:#f0a500; font-size:0.68rem; font-weight:600; letter-spacing:0.1em; text-transform:uppercase; padding:3px 10px; border-radius:2px; }
.source-badge-uploaded { display:inline-block; background:#1a1d27; border:1px solid #c084fc; color:#c084fc; font-size:0.68rem; font-weight:600; letter-spacing:0.1em; text-transform:uppercase; padding:3px 10px; border-radius:2px; }
</style>
""", unsafe_allow_html=True)

# ================= HEADER =================

st.markdown("""
<div class="header-banner">
    <div>
        <div class="header-title">&#9881; Machine Specification System</div>
        <div class="header-subtitle">Heavy Machining &nbsp;·&nbsp; Technical Reference Database</div>
    </div>
    <div class="header-badge">Industrial Use</div>
</div>
""", unsafe_allow_html=True)

st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

# ================= EXCEL UPLOAD SECTION =================

with st.expander("📂  UPLOAD EXCEL FILE  —  Load a custom machine dataset", expanded=False):
    st.markdown("""
    <div style='font-size:0.78rem;color:#8b90a0;margin-bottom:1rem;line-height:1.7;'>
    Upload your own Excel file to view and query any machine type.
    The app will automatically detect parameters, units, and machine numbers from your file.
    <br><br>
    <b style='color:#c084fc;'>Supported Excel Layouts:</b><br>
    &nbsp;&nbsp;<b>Layout A (recommended)</b> — First column = <code>Parameter</code>, second = <code>Unit</code> (optional), then machine numbers as column headers<br>
    &nbsp;&nbsp;<b>Layout B</b> — First column = <code>Machine No.</code>, first row = parameter names, optional second row = units
    </div>
    """, unsafe_allow_html=True)

    tcol1, tcol2 = st.columns(2)
    with tcol1:
        tpl_a = generate_template_excel("A")
        st.download_button(
            "⬇  Download Layout A Template",
            data=tpl_a,
            file_name="machine_spec_template_layoutA.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="tpl_a",
        )
    with tcol2:
        tpl_b = generate_template_excel("B")
        st.download_button(
            "⬇  Download Layout B Template",
            data=tpl_b,
            file_name="machine_spec_template_layoutB.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            key="tpl_b",
        )

    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "Choose an Excel file (.xlsx or .xls)",
        type=["xlsx", "xls"],
        key="excel_uploader",
        label_visibility="collapsed",
    )

    if uploaded_file is not None:
        try:
            u_mdata, u_specs, u_units, u_groups = parse_uploaded_excel(uploaded_file)
            st.session_state["uploaded_data"] = (uploaded_file.name, u_mdata, u_specs, u_units, u_groups)
            st.session_state["active_source"] = "uploaded"
            st.success(
                f"✅  Loaded **{uploaded_file.name}** — "
                f"{len(u_mdata)} machines · {len(u_specs)} parameters detected"
            )
        except ValueError as e:
            st.error(f"❌  {e}")
            st.session_state["uploaded_data"] = None

    if st.session_state["uploaded_data"] is not None:
        col_sw1, col_sw2 = st.columns(2)
        with col_sw1:
            if st.button("✅  USE UPLOADED FILE", key="use_uploaded"):
                st.session_state["active_source"] = "uploaded"
        with col_sw2:
            if st.button("🔁  SWITCH TO BUILT-IN DATA", key="use_builtin"):
                st.session_state["active_source"] = "builtin"

st.markdown("<div style='height:0.4rem'></div>", unsafe_allow_html=True)

# ================= RESOLVE ACTIVE DATA SOURCE =================

active_source = st.session_state["active_source"]

if active_source == "uploaded" and st.session_state["uploaded_data"] is not None:
    u_name, u_mdata, u_specs, u_units, u_groups = st.session_state["uploaded_data"]
    active_accent = UPLOADED_ACCENT
    mdata    = u_mdata
    specs    = u_specs
    units    = u_units
    groups   = u_groups
    machine_numbers = sorted(mdata.keys())

    st.markdown(f"""
    <div style='background:#12151f;border:1px solid #2a2e3e;border-left:3px solid {active_accent};
    border-radius:3px;padding:0.55rem 1.1rem;margin-bottom:0.8rem;display:flex;align-items:center;gap:1rem;'>
      <span class='source-badge-uploaded'>Uploaded File</span>
      <span style='font-size:0.85rem;font-weight:600;color:#e8eaf0;'>{u_name}</span>
      <span style='margin-left:auto;font-size:0.68rem;color:#6b7080;'>
        {len(mdata)} machines &nbsp;·&nbsp; {len(specs)} parameters
      </span>
    </div>
    """, unsafe_allow_html=True)

else:
    # ── Built-in mode: show machine type selector ──────────────────────────
    active_type = st.session_state["machine_type"]
    active_accent = TYPE_ACCENT[active_type]

    st.markdown("""
    <div style='font-size:0.7rem;font-weight:600;letter-spacing:0.14em;text-transform:uppercase;
    color:#6b7080;margin-bottom:0.6rem;padding-left:0.2rem;'>Select Machine Type</div>
    """, unsafe_allow_html=True)

    type_col1, type_col2, type_col3, _ = st.columns([1, 1, 1, 2])
    type_map = [
        ("PM (Plano Miller)",      "🔧", type_col1, "#f0a500"),
        ("HB (Horizontal Boring)", "⚙️", type_col2, "#4a9eff"),
        ("LT (Lathe)",             "🔩", type_col3, "#00c17c"),
    ]
    for label, icon, col, col_accent in type_map:
        with col:
            is_active = (active_type == label)
            bg  = col_accent if is_active else "transparent"
            fg  = "#0f1117"  if is_active else col_accent
            cnt = len(BUILTIN_REGISTRY[label][0])
            st.markdown(f"""
            <div style='background:{bg};border:1px solid {col_accent};border-radius:4px;
            padding:0.75rem 1rem;text-align:center;margin-bottom:0.25rem;cursor:default;'>
              <div style='font-size:1.3rem;line-height:1;'>{icon}</div>
              <div style='font-size:0.72rem;font-weight:700;color:{fg};letter-spacing:0.08em;
              text-transform:uppercase;margin-top:0.35rem;'>{label}</div>
              <div style='font-size:0.65rem;color:{"#0f1117" if is_active else "#6b7080"};margin-top:0.2rem;'>{cnt} machines</div>
            </div>""", unsafe_allow_html=True)
            if st.button(f"{'✓ Active' if is_active else 'Select'}", key=f"typebtn_{label}", use_container_width=True):
                st.session_state["machine_type"] = label
                st.session_state["active_source"] = "builtin"
                st.experimental_rerun()

    st.markdown("<div style='height:0.6rem'></div>", unsafe_allow_html=True)
    mdata, specs, units, groups = BUILTIN_REGISTRY[active_type]
    machine_numbers = sorted(mdata.keys())

    st.markdown(f"""
    <div style='background:#12151f;border:1px solid #2a2e3e;border-left:3px solid {active_accent};
    border-radius:3px;padding:0.55rem 1.1rem;margin-bottom:1.4rem;display:flex;align-items:center;gap:1rem;'>
      <span class='source-badge-builtin'>Built-in Data</span>
      <span style='font-size:0.85rem;font-weight:600;color:#e8eaf0;'>{active_type}</span>
      <span style='margin-left:auto;font-size:0.68rem;color:#6b7080;'>
        {len(mdata)} machines &nbsp;·&nbsp; {len(specs)} parameters
      </span>
    </div>
    """, unsafe_allow_html=True)

# ================= TABS =================

tab_lookup, tab_compare, tab_full = st.tabs(["SPEC LOOKUP", "MACHINE COMPARISON", "FULL SPEC SHEET"])

# ─── TAB 1: SPEC LOOKUP ──────────────────────────────────────────────────────
with tab_lookup:
    st.markdown("<div style='height:1.2rem'></div>", unsafe_allow_html=True)
    col_sel, col_spacer, col_result = st.columns([1, 0.08, 2])

    with col_sel:
        st.markdown(f"<div style='font-size:0.7rem;font-weight:600;letter-spacing:0.14em;text-transform:uppercase;color:{active_accent};margin-bottom:0.5rem;'>Select Machine</div>", unsafe_allow_html=True)
        machine_no = st.selectbox("Machine Number", machine_numbers, key="lookup_machine", label_visibility="collapsed")
        st.markdown("<div style='height:0.8rem'></div>", unsafe_allow_html=True)
        st.markdown(f"<div style='font-size:0.7rem;font-weight:600;letter-spacing:0.14em;text-transform:uppercase;color:{active_accent};margin-bottom:0.5rem;'>Select Parameter</div>", unsafe_allow_html=True)
        specification = st.selectbox("Specification", specs, key="lookup_spec", label_visibility="collapsed")
        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
        check_clicked = st.button("CHECK PARAMETER", use_container_width=True, key="check_btn")

    with col_result:
        if check_clicked:
            value = mdata[machine_no][specification]
            unit = units.get(specification, "")
            is_na = value is None
            display_val = str(value) if not is_na else "N/A"
            value_color = "#00c17c" if not is_na else "#3a3e50"

            machine_card = (
                f"<div style='background:#1a1d27;border:1px solid #2a2e3e;border-top:2px solid {active_accent};"
                "border-radius:4px;padding:1.4rem 1.6rem;text-align:center;flex:1;min-width:130px;'>"
                "<div style='font-size:0.68rem;letter-spacing:0.12em;text-transform:uppercase;color:#6b7080;margin-bottom:0.5rem;'>Machine No.</div>"
                f"<div style='font-family:JetBrains Mono,monospace;font-size:2rem;font-weight:600;color:{active_accent};line-height:1;'>{machine_no}</div>"
                "</div>"
            )
            param_card = (
                "<div style='background:#1a1d27;border:1px solid #2a2e3e;border-top:2px solid #4a9eff;"
                "border-radius:4px;padding:1.4rem 1.6rem;flex:3;min-width:220px;text-align:center;'>"
                "<div style='font-size:0.68rem;letter-spacing:0.12em;text-transform:uppercase;color:#6b7080;margin-bottom:0.6rem;'>Parameter</div>"
                f"<div style='font-family:Inter,sans-serif;font-size:1.15rem;font-weight:600;color:#a8c8ff;line-height:1.4;'>{specification}</div>"
                "</div>"
            )
            value_card = (
                "<div style='background:#f8f6f2;border:1px solid #d9d4cc;border-top:2px solid #e5dfd6;"
                "border-radius:4px;padding:2rem 2rem;text-align:center;flex:2;min-width:260px;'>"
                "<div style='font-size:0.68rem;letter-spacing:0.12em;text-transform:uppercase;color:#666;margin-bottom:0.5rem;'>Value</div>"
                f"<div style='font-family:JetBrains Mono,monospace;font-size:3rem;font-weight:600;color:{value_color};line-height:1;'>{display_val}</div>"
                f"<div style='font-size:0.78rem;color:#666;margin-top:6px;'>{unit if not is_na else 'no data'}</div>"
                "</div>"
            )
            st.markdown(
                f"<div style='background:#12151f;border:1px solid #2a2e3e;border-radius:4px;padding:1.8rem 1.8rem;'>"
                f"<div style='font-size:0.68rem;letter-spacing:0.14em;text-transform:uppercase;color:{active_accent};margin-bottom:1.2rem;'>Query Result</div>"
                f"<div style='display:flex;gap:1.2rem;flex-wrap:wrap;'>{machine_card}{param_card}{value_card}</div>"
                "</div>",
                unsafe_allow_html=True,
            )

            stats = get_min_max_machine(specification, mdata)
            if stats:
                st.markdown("<div style='height:1.2rem'></div>", unsafe_allow_html=True)
                col_max, col_min = st.columns(2)
                with col_max:
                    st.markdown(f"""
                    <div style='background:#1a1d27;border:1px solid #2a2e3e;border-top:3px solid #00c17c;border-radius:4px;padding:1.6rem;text-align:center;'>
                        <div style='color:#00c17c;font-size:0.75rem;font-weight:600;text-transform:uppercase;'>Maximum Value</div>
                        <div style='color:white;font-size:2rem;font-weight:600;margin-top:0.8rem;'>Machine {stats['max_machine']}</div>
                        <div style='color:#00c17c;font-size:3rem;font-weight:700;margin-top:0.8rem;'>{stats['max_value']}</div>
                        <div style='color:#8b90a0;'>{unit}</div>
                    </div>""", unsafe_allow_html=True)
                with col_min:
                    st.markdown(f"""
                    <div style='background:#1a1d27;border:1px solid #2a2e3e;border-top:3px solid #4a9eff;border-radius:4px;padding:1.6rem;text-align:center;'>
                        <div style='color:#4a9eff;font-size:0.75rem;font-weight:600;text-transform:uppercase;'>Minimum Value</div>
                        <div style='color:white;font-size:2rem;font-weight:600;margin-top:0.8rem;'>Machine {stats['min_machine']}</div>
                        <div style='color:#4a9eff;font-size:3rem;font-weight:700;margin-top:0.8rem;'>{stats['min_value']}</div>
                        <div style='color:#8b90a0;'>{unit}</div>
                    </div>""", unsafe_allow_html=True)
        else:
            st.markdown(
                "<div style='background:#1a1d27;border:1px solid #2a2e3e;border-radius:4px;"
                "padding:3.5rem 2rem;text-align:center;color:#3a3e50;"
                "font-size:0.82rem;letter-spacing:0.1em;text-transform:uppercase;'>"
                "Select a machine and parameter, then press CHECK PARAMETER"
                "</div>",
                unsafe_allow_html=True,
            )

# ─── TAB 2: COMPARISON ───────────────────────────────────────────────────────
with tab_compare:
    st.markdown("<div style='height:1.2rem'></div>", unsafe_allow_html=True)
    st.markdown(f"<div style='font-size:0.7rem;font-weight:600;letter-spacing:0.14em;text-transform:uppercase;color:{active_accent};margin-bottom:0.5rem;'>Select Machines to Compare</div>", unsafe_allow_html=True)
    selected_machines = st.multiselect(
        "Machines", machine_numbers,
        default=machine_numbers[:min(3, len(machine_numbers))],
        key="compare_machines", label_visibility="collapsed",
    )

    if len(selected_machines) < 2:
        st.info("Select at least 2 machines to generate a comparison.")
    else:
        hide_empty = st.checkbox("Hide parameters with no data across all selected machines", value=True)
        df_compare = build_comparison_df(selected_machines, mdata, specs, units)
        if hide_empty:
            machine_cols = ["Machine {}".format(m) for m in selected_machines]
            mask = df_compare[machine_cols].apply(lambda row: any(v != "—" for v in row), axis=1)
            df_compare = df_compare[mask].reset_index(drop=True)
        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
        st.dataframe(df_compare, use_container_width=True, hide_index=True,
                     height=min(60 + len(df_compare) * 35, 620))
        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
        csv = df_compare.to_csv(index=False).encode("utf-8")
        st.download_button(
            "EXPORT COMPARISON — CSV", data=csv,
            file_name="comparison_{}.csv".format("_".join(str(m) for m in selected_machines)),
            mime="text/csv",
        )

# ─── TAB 3: FULL SPEC SHEET ──────────────────────────────────────────────────
with tab_full:
    st.markdown("<div style='height:1.2rem'></div>", unsafe_allow_html=True)
    c1, c2 = st.columns([1, 3])
    with c1:
        st.markdown(f"<div style='font-size:0.7rem;font-weight:600;letter-spacing:0.14em;text-transform:uppercase;color:{active_accent};margin-bottom:0.5rem;'>Select Machine</div>", unsafe_allow_html=True)
        machine_fs = st.selectbox("Machine", machine_numbers, key="full_machine", label_visibility="collapsed")
        show_only_available = st.checkbox("Show available parameters only", value=False)
    with c2:
        avail_fs = count_available(machine_fs, mdata, specs)
        pct = int(avail_fs / len(specs) * 100)
        st.markdown(f"""
        <div style='display:flex;gap:1rem;flex-wrap:wrap;'>
            <div class='metric-card' style='min-width:140px;'><div class='metric-label'>Machine No.</div><div class='metric-value'>{machine_fs}</div></div>
            <div class='metric-card' style='min-width:140px;'><div class='metric-label'>Parameters on Record</div><div class='metric-value'>{avail_fs}</div><div class='metric-unit'>of {len(specs)} total</div></div>
            <div class='metric-card' style='min-width:140px;'><div class='metric-label'>Data Coverage</div><div class='metric-value'>{pct}%</div></div>
        </div>""", unsafe_allow_html=True)

    st.markdown("<div style='height:1.2rem'></div>", unsafe_allow_html=True)
    export_rows = []
    for idx, spec in enumerate(specs):
        v = mdata[machine_fs][spec]
        if show_only_available and v is None:
            continue
        export_rows.append({"#": str(idx + 1).zfill(2), "Parameter": spec, "Value": format_value(spec, v, units)})
    df_full = pd.DataFrame(export_rows)
    st.dataframe(df_full, use_container_width=True, hide_index=True,
                 height=min(60 + len(df_full) * 35, 660))
    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
    csv_full = df_full.to_csv(index=False).encode("utf-8")
    st.download_button(
        "EXPORT MACHINE {} SPECS — CSV".format(machine_fs),
        data=csv_full,
        file_name="machine_{}_specifications.csv".format(machine_fs),
        mime="text/csv",
    )
