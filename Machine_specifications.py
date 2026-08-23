"""
Machine Specification System
=============================
Streamlit app for looking up, comparing, and browsing heavy-machining
equipment specifications (Plano Millers, Horizontal Borers, Lathes, Gear
Cutting machines, etc).

All data is read from an Excel workbook (one sheet per machine type) instead
of being hardcoded, so updating specs is just an Excel edit + re-deploy -
no code changes needed. Users can also upload their own workbook at runtime
to preview a different dataset.

Run locally:
    streamlit run app.py

Deploy: push this folder to GitHub and point Streamlit Community Cloud at
app.py. Make sure data/machine_specs.xlsx is committed to the repo.
"""

import re
import pandas as pd
import streamlit as st

from data_loader import load_default_workbook, load_workbook, get_sheet_meta


def h(template: str) -> str:
    """
    Collapse a multi-line HTML template into a single line before handing it
    to st.markdown(). Streamlit's Markdown renderer treats any line indented
    4+ spaces as a code block, so an indented multi-line f-string can leak
    raw tags (e.g. a stray "</div>") into the page. Flattening to one line
    sidesteps that entirely - this is the fix, not just tidying.
    """
    return re.sub(r">\s+<", "><", re.sub(r"\s+", " ", template)).strip()


# --------------------------------------------------------------------------
# Page config + styling
# --------------------------------------------------------------------------
st.set_page_config(
    page_title="Machine Specification System",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# --------------------------------------------------------------------------
# PWA: makes the app installable ("Add to Home Screen") on Android/iOS.
# Streamlit renders inside an iframe, so we reach into the parent window
# to inject the manifest link and a theme-color meta tag into the real
# page <head>.
# --------------------------------------------------------------------------
import streamlit.components.v1 as components

components.html("""
<script>
  const doc = window.parent.document;
  if (!doc.querySelector('link[rel="manifest"]')) {
    const link = doc.createElement('link');
    link.rel = 'manifest';
    link.href = './static/manifest.json';
    doc.head.appendChild(link);
  }
  if (!doc.querySelector('meta[name="theme-color"]')) {
    const meta = doc.createElement('meta');
    meta.name = 'theme-color';
    meta.content = '#181c24';
    doc.head.appendChild(meta);
  }
  if (!doc.querySelector('link[rel="apple-touch-icon"]')) {
    const appleIcon = doc.createElement('link');
    appleIcon.rel = 'apple-touch-icon';
    appleIcon.href = './static/icon-192.png';
    doc.head.appendChild(appleIcon);
  }
</script>
""", height=0)

st.markdown(h("""
<style>
    .stApp { background-color: #0b0e17; }
    #MainMenu, footer, header {visibility: hidden;}

    /* Streamlit reserves a large top gap above the first element by default -
       trim it so the header sits right under the browser chrome, especially
       on phones where that gap otherwise pushes everything down a full
       screen's worth of empty space. */
    .block-container, div[data-testid="stMainBlockContainer"] {
        padding-top: 1.2rem !important;
        padding-bottom: 2rem !important;
    }
    @media (max-width: 640px) {
        .block-container, div[data-testid="stMainBlockContainer"] {
            padding-top: 0.6rem !important;
        }
    }

    .app-header {
        background: #11141f; border: 1px solid #2a2f42; border-radius: 10px;
        padding: 22px 28px; margin-bottom: 20px;
    }
    .app-title { color: #ffffff; font-size: 26px; font-weight: 800; margin: 0; }
    .app-subtitle {
        color: #f5a623; font-size: 12px; letter-spacing: 1.5px;
        font-weight: 600; margin-top: 6px;
    }
    .badge-pill {
        display: inline-block; background: #f5a623; color: #1a1000;
        font-weight: 700; font-size: 12px; letter-spacing: 1px;
        padding: 6px 14px; border-radius: 6px;
    }
    .section-label {
        color: #9aa3b5; font-size: 12px; font-weight: 700; letter-spacing: 1px;
        text-transform: uppercase; margin-bottom: 10px;
    }

    /* ---- machine-type selector cards ---- */
    /* Streamlit can't put an onclick handler on a plain HTML div, so the
       actual click target is a native button. Rather than guessing the
       card's pixel height and shifting the button up to match (fragile -
       any drift between the guessed height and the real one leaves part
       of the card dead to clicks), the button's own container is
       absolutely positioned to fill its column edge-to-edge. Since the
       column's height is set by the card (the button is taken out of
       flow), the button always exactly covers the card, at any size,
       automatically. */
    .type-card {
        border-radius: 10px; padding: 12px 8px; text-align: center;
        box-sizing: border-box;
        display: flex; flex-direction: column; align-items: center; justify-content: center;
        position: relative; z-index: 1;
    }
    .type-card .icon { font-size: 17px; line-height: 1; }
    .type-card .label { font-size: 16px; font-weight: 800; margin-top: 7px; }
    .type-card .count { font-size: 9.5px; margin-top: 4px; }

    /* ---- baseline shape for every button in the app ----
       Selectors are written several redundant ways (data-testid, class name,
       plain "button" fallback) because Streamlit has renamed these testids
       across versions - this makes the rule survive that. Every rule is
       !important because Streamlit's own button CSS is otherwise more
       specific / loaded later. This is a normal, fully-rounded button
       (e.g. "CHECK PARAMETER") - the type-selector cards below override it
       to become an invisible full-card overlay instead. */
    div.stButton button,
    div[data-testid="stButton"] button,
    div[class*="stButton"] button {
        border-radius: 8px !important;
        min-height: 44px !important; /* comfortable tap target on mobile */
        font-weight: 700 !important;
        font-size: 13px !important;
        letter-spacing: 0.5px !important;
        box-shadow: none !important;
        width: 100% !important;
    }
    div.stButton button[kind="primary"],
    div[data-testid="stButton"] button[kind="primary"],
    div[class*="stButton"] button[kind="primary"] {
        background-color: #f5c518 !important;
        color: #1a1400 !important;
        border: 1px solid #f5c518 !important;
    }
    div.stButton button[kind="primary"]:hover,
    div[data-testid="stButton"] button[kind="primary"]:hover,
    div[class*="stButton"] button[kind="primary"]:hover {
        background-color: #dcae0f !important;
        color: #1a1400 !important;
    }
    div.stButton button[kind="secondary"],
    div[data-testid="stButton"] button[kind="secondary"],
    div[class*="stButton"] button[kind="secondary"] {
        background-color: #11141f !important;
        color: #cbd2e0 !important;
        border: 1px solid #2a2f42 !important;
    }
    div.stButton button[kind="secondary"]:hover,
    div[data-testid="stButton"] button[kind="secondary"]:hover,
    div[class*="stButton"] button[kind="secondary"]:hover {
        border-color: #4a5170 !important;
        color: #ffffff !important;
    }
    /* Neutralize Streamlit's focus/active red-ish outline & re-tint it to
       the app's palette so tapping a card on mobile doesn't flash red. */
    div.stButton button:focus:not(:active),
    div[data-testid="stButton"] button:focus:not(:active) {
        box-shadow: none !important;
    }

    /* ---- type-selector cards only: stretch the (invisible) button's own
       container to exactly fill the card's column, using each button's
       key-derived class (st-key-select_<TYPE>) rather than a hardcoded
       pixel size. The column is the positioning anchor; the card (in
       normal flow) sets the column's height; the button (taken out of
       flow via absolute positioning) exactly matches that height and
       covers 100% of the card, at any screen size, with no drift. ---- */
    div.st-key-type_selector div[data-testid="stColumn"] {
        position: relative !important;
    }
    /* The chain of wrapper divs between the column and our .type-card can
       otherwise end up shorter than the card's real rendered height (a
       stale auto-height calculation from Streamlit), which would leave
       part of the card outside the click overlay below. Forcing every
       link in that chain to auto-size to its content keeps the column's
       height (and therefore the overlay's height) exactly equal to the
       card's real height. */
    div.st-key-type_selector div[data-testid="stElementContainer"],
    div.st-key-type_selector div[data-testid="stElementContainer"] > div,
    div.st-key-type_selector div[data-testid="stMarkdown"],
    div.st-key-type_selector div[data-testid="stMarkdown"] > div,
    div.st-key-type_selector div[data-testid="stMarkdownContainer"] {
        height: auto !important;
        display: block !important;
        -webkit-line-clamp: unset !important;
    }
    div.st-key-type_selector div.stElementContainer[class*="st-key-select_"] {
        position: absolute !important;
        top: 0 !important; left: 0 !important; right: 0 !important;
        /* The parent flex column has "gap: 1rem" between its children.
           Even though this element is taken out of flow via absolute
           positioning, that gap still shows up missing from the
           containing block's height - so the plain "bottom: 0" edge sits
           1rem short of the card's real bottom edge. Extend past it by
           exactly that amount so the overlay always covers 100% of the
           card, regardless of the card's actual rendered height. */
        height: calc(100% + 1rem) !important;
        z-index: 5 !important;
    }
    div.st-key-type_selector div.stElementContainer[class*="st-key-select_"] div[data-testid="stButton"] {
        height: 100% !important;
    }
    div.st-key-type_selector div.stElementContainer[class*="st-key-select_"] button {
        height: 100% !important; min-height: 0 !important;
        background: transparent !important; border: none !important;
        color: transparent !important; cursor: pointer;
    }
    div.st-key-type_selector div.stElementContainer[class*="st-key-select_"] button:hover,
    div.st-key-type_selector div.stElementContainer[class*="st-key-select_"] button:focus {
        background: transparent !important; border: none !important;
        color: transparent !important;
    }

    /* ---- mobile tightening ---- */
    @media (max-width: 640px) {
        .app-header { padding: 14px 16px; margin-bottom: 12px; }
        .app-title { font-size: 19px; letter-spacing: 0.2px; }
        .app-subtitle { font-size: 10.5px; letter-spacing: 1px; margin-top: 4px; }
        .section-label { font-size: 11.5px; margin-bottom: 6px; }

        div[data-testid="stExpander"] summary { padding: 6px 10px !important; min-height: 0 !important; }
        div[data-testid="stExpander"] summary p { font-size: 11.5px !important; }
        div[data-testid="stExpander"] div[data-testid="stFileUploaderDropzone"] { padding: 8px !important; }

        .type-card { padding: 6px 4px; min-height: 58px; }
        .type-card .icon { font-size: 12px; }
        .type-card .label { font-size: 12.5px; margin-top: 3px; }
        .type-card .count { font-size: 7.5px; margin-top: 2px; }

        .source-banner { padding: 7px 10px; margin: 8px 0; }
        .source-banner .badge-pill { font-size: 9.5px; padding: 3px 8px; }
        .source-banner > div:last-child { font-size: 10px !important; }

        div[data-testid="stTabs"] button[data-baseweb="tab"] { padding: 6px 8px !important; }
        div[data-testid="stTabs"] button[data-baseweb="tab"] p { font-size: 11px !important; }

        .placeholder-card { padding: 24px 14px; font-size: 11px; }

        .result-field .card-value { font-size: 16px !important; }
        .result-machine .card-value { font-size: 19px !important; }
        .result-value-row .card-value { font-size: 26px !important; }
        .minmax-half { padding: 12px 8px; }
        .minmax-half .card-value { font-size: 20px !important; }
    }

    /* ---- keep the machine-type row side-by-side even on mobile ---- */
    /* Scoped to the type-selector container only (via st.container(key=...))
       so the lookup form's columns elsewhere in the app can still stack
       normally on narrow screens - only these 3 cards need to stay in a row. */
    div.st-key-type_selector div[data-testid="stHorizontalBlock"] {
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        gap: 6px !important;
    }
    div.st-key-type_selector div[data-testid="stColumn"] {
        flex: 1 1 0 !important;
        width: auto !important;
        min-width: 0 !important;
    }

    /* ---- data-source banner ---- */
    .source-banner {
        border-left: 3px solid #f5a623; background: #11141f;
        padding: 14px 18px; border-radius: 0 8px 8px 0; margin: 18px 0;
        display: flex; justify-content: space-between; align-items: center;
        flex-wrap: wrap; gap: 8px;
    }

    /* ---- result card (Spec Lookup tab) ---- */
    /* One single card holds the whole query result: Machine No. + Parameter
       side by side up top (separated by a vertical divider), a horizontal
       rule, then the Value front and center underneath. This reads as one
       coherent answer instead of three separate boxes stacked on top of
       each other. */
    .card-label {
        color: #9aa3b5; font-size: 11px; font-weight: 700; letter-spacing: 1.2px;
        text-transform: uppercase; margin-bottom: 8px;
    }
    .card-value { font-weight: 800; line-height: 1.2; word-break: break-word; color: #ffffff; }
    .card-sub { font-size: 12px; color: #6b7280; margin-top: 6px; }
    .machine-name { color: #cbd2e0; font-size: 14px; font-weight: 600; margin-bottom: 4px; }

    .result-card {
        background: #11141f; border: 1px solid #2a2f42; border-top: 3px solid #f5a623;
        border-radius: 8px; padding: 18px 16px 20px; box-sizing: border-box;
    }
    .result-top {
        display: flex; align-items: stretch;
        padding-bottom: 16px; margin-bottom: 16px; border-bottom: 1px solid #2a2f42;
    }
    .result-field {
        flex: 1; text-align: center; padding: 0 10px; box-sizing: border-box;
    }
    .result-field + .result-field { border-left: 1px solid #2a2f42; }
    .result-machine .card-value { color: #f5a623; font-size: 24px; }
    .result-parameter .card-value { color: #4a9eff; font-size: 16px; }

    .result-value-row { text-align: center; }
    .result-value-row .card-value { font-size: 34px; }
    .result-value-row .card-value.small { font-size: 18px; color: #7d8494; }

    /* Max / Min: one card, two halves, split by a single vertical line. */
    .minmax-card {
        display: flex; align-items: stretch;
        background: #11141f; border: 1px solid #2a2f42; border-radius: 8px;
        box-sizing: border-box; overflow: hidden;
    }
    .minmax-half {
        flex: 1; text-align: center; padding: 18px 12px; box-sizing: border-box;
        border-top: 3px solid transparent;
    }
    .minmax-half + .minmax-half { border-left: 1px solid #2a2f42; }
    .minmax-half.max { border-top-color: #34d399; }
    .minmax-half.max .card-label { color: #34d399; }
    .minmax-half.max .card-value { color: #34d399; font-size: 26px; }
    .minmax-half.min { border-top-color: #4a9eff; }
    .minmax-half.min .card-label { color: #4a9eff; }
    .minmax-half.min .card-value { color: #4a9eff; font-size: 26px; }

    .placeholder-card {
        background: #11141f; border: 1px dashed #2a2f42; border-radius: 10px;
        padding: 40px 20px; text-align: center; color: #5b6377;
        font-size: 13px; letter-spacing: 0.5px; height: 100%;
        display: flex; align-items: center; justify-content: center;
    }

    .app-footer {
        text-align: center; color: #5b6377; font-size: 12px; margin-top: 34px;
    }

    section[data-testid="stSidebar"] { background: #0b0e17; }
</style>
"""), unsafe_allow_html=True)

# --------------------------------------------------------------------------
# Header
# --------------------------------------------------------------------------
st.markdown(h("""
<div class="app-header">
    <div class="app-title">⚙️ MACHINE SPECIFICATION SYSTEM</div>
    <div class="app-subtitle">HEAVY MACHINING &nbsp;·&nbsp; TECHNICAL REFERENCE DATABASE</div>
</div>
"""), unsafe_allow_html=True)

# --------------------------------------------------------------------------
# Data source: bundled workbook, optionally overridden by an upload
# --------------------------------------------------------------------------
with st.expander("📁  UPLOAD EXCEL FILE — Load a custom machine dataset"):
    uploaded = st.file_uploader(
        "Workbook must follow the same layout as the built-in file: one sheet "
        "per machine type, machine numbers on row 2, parameters from row 3 down.",
        type=["xlsx"],
    )

using_custom = uploaded is not None
if using_custom:
    sheets = load_workbook(uploaded.getvalue())
    st.success(f"Loaded custom dataset: **{uploaded.name}** ({len(sheets)} machine type sheet(s))")
else:
    sheets = load_default_workbook()
    # Only PM, HB, and Lathe are in scope for this system - drop any other
    # sheet that happens to be in the workbook (e.g. GC).
    sheets = {k: v for k, v in sheets.items() if k.strip().upper() in {"PM", "HB", "LATHE", "LT"}}

if not sheets:
    st.error("No valid sheets found in the workbook. Check the file layout and try again.")
    st.stop()

# --------------------------------------------------------------------------
# Machine type selector
# --------------------------------------------------------------------------
st.markdown('<div class="section-label">Select Machine Type</div>', unsafe_allow_html=True)

sheet_names = list(sheets.keys())
if "selected_type" not in st.session_state or st.session_state["selected_type"] not in sheet_names:
    st.session_state["selected_type"] = sheet_names[0]

with st.container(key="type_selector"):
    cols = st.columns(len(sheet_names))
    for col, name in zip(cols, sheet_names):
        meta = get_sheet_meta(name)
        type_df = sheets[name]
        is_active = st.session_state["selected_type"] == name

        # Card border matches the button's border exactly (white when active,
        # neutral dark-grey when inactive) so the two elements read as one
        # continuous shape. The type's own accent color is still shown via a
        # top bar, so machine types stay visually distinguishable.
        bg = "#f5c518" if is_active else "#11141f"
        border = "#f5c518" if is_active else "#2a2f42"
        accent = "#f5c518" if is_active else meta["color"]

        # Split "HB (Horizontal Boring)" into a short code (shown on the
        # button) and a descriptive remainder (shown as a hover tooltip
        # instead of cluttering the compact card).
        label = meta["label"]
        if "(" in label:
            short, _, rest = label.partition("(")
            short, rest = short.strip(), "(" + rest
        else:
            short, rest = label, ""

        with col:
            st.markdown(h(f"""
            <div class="type-card" style="background:{bg}; border:1px solid {border}; border-top:3px solid {accent};">
                <div class="icon">{meta['icon']}</div>
                <div class="label" style="color:{'#1a1400' if is_active else '#ffffff'};">{short}</div>
                <div class="count" style="color:{'#5b5220' if is_active else '#9aa3b5'};">{type_df.shape[1]} machines</div>
            </div>
            """), unsafe_allow_html=True)

            if st.button(f"Select {short}", key=f"select_{name}", use_container_width=True,
                         help=rest.strip("() ") or None):
                st.session_state["selected_type"] = name
                st.rerun()

selected_type = st.session_state["selected_type"]
df = sheets[selected_type]
meta = get_sheet_meta(selected_type)
machine_numbers = list(df.columns)
parameters = list(df.index)

source_label = "CUSTOM UPLOAD" if using_custom else "BUILT-IN DATA"
st.markdown(h(f"""
<div class="source-banner">
    <div>
        <span class="badge-pill">{source_label}</span>
        &nbsp;&nbsp;<b style="color:#fff;">{meta['label']}</b>
    </div>
    <div style="color:#9aa3b5; font-size:13px;">
        {len(machine_numbers)} machines &nbsp;·&nbsp; {len(parameters)} parameters
    </div>
</div>
"""), unsafe_allow_html=True)

# --------------------------------------------------------------------------
# Tabs
# --------------------------------------------------------------------------
tab_lookup, tab_compare, tab_full = st.tabs(
    ["🔍 SPEC LOOKUP", "📊 MACHINE COMPARISON", "📋 FULL SPEC SHEET"]
)

# ---- Tab 1: Spec Lookup ----------------------------------------------------
with tab_lookup:
    left, right = st.columns([1, 2], gap="large")

    with left:
        st.markdown('<div class="section-label">Select Machine</div>', unsafe_allow_html=True)
        machine_choice = st.selectbox(
            "Machine number", machine_numbers, key="lookup_machine",
            label_visibility="collapsed", filter_mode=None,
        )
        st.markdown('<div class="section-label" style="margin-top:16px;">Select Parameter</div>', unsafe_allow_html=True)
        param_choice = st.selectbox(
            "Parameter", parameters, key="lookup_param",
            label_visibility="collapsed", filter_mode=None,
        )
        st.write("")
        check = st.button("CHECK PARAMETER", type="primary", use_container_width=True)

    with right:
        if check:
            st.session_state["last_lookup"] = (machine_choice, param_choice)

        lookup = st.session_state.get("last_lookup")

        if lookup and lookup[0] in df.columns and lookup[1] in df.index:
            m, p = lookup
            value = df.loc[p, m]
            has_value = not (value is None or (isinstance(value, float) and pd.isna(value)))

            st.markdown('<div class="section-label">Query Result</div>', unsafe_allow_html=True)

            if has_value:
                value_block = f"""
                <div class="card-label">Value</div>
                <div class="card-value">{value}</div>
                """
            else:
                value_block = """
                <div class="card-label">Value</div>
                <div class="card-value small">N / A</div>
                <div class="card-sub">no data recorded</div>
                """

            st.markdown(h(f"""
            <div class="result-card">
                <div class="result-top">
                    <div class="result-field result-machine">
                        <div class="card-label">Machine No.</div>
                        <div class="card-value">{m}</div>
                    </div>
                    <div class="result-field result-parameter">
                        <div class="card-label">Parameter</div>
                        <div class="card-value">{p}</div>
                    </div>
                </div>
                <div class="result-value-row">{value_block}</div>
            </div>
            """), unsafe_allow_html=True)

            # ---- Max / Min across all machines for this parameter, shown
            # as one card split by a single vertical line down the middle ----
            numeric_row = pd.to_numeric(df.loc[p], errors="coerce").dropna()
            if len(numeric_row) >= 2:
                max_machine, max_val = numeric_row.idxmax(), numeric_row.max()
                min_machine, min_val = numeric_row.idxmin(), numeric_row.min()

                st.write("")
                st.markdown(h(f"""
                <div class="minmax-card">
                    <div class="minmax-half max">
                        <div class="card-label">Maximum Value</div>
                        <div class="machine-name">Machine {max_machine}</div>
                        <div class="card-value">{max_val:g}</div>
                    </div>
                    <div class="minmax-half min">
                        <div class="card-label">Minimum Value</div>
                        <div class="machine-name">Machine {min_machine}</div>
                        <div class="card-value">{min_val:g}</div>
                    </div>
                </div>
                """), unsafe_allow_html=True)
        else:
            st.markdown(h("""
            <div class="placeholder-card">
                SELECT A MACHINE AND PARAMETER, THEN PRESS CHECK PARAMETER
            </div>
            """), unsafe_allow_html=True)

# ---- Tab 2: Machine Comparison ---------------------------------------------
with tab_compare:
    st.markdown('<div class="section-label">Select Machines to Compare</div>', unsafe_allow_html=True)
    compare_machines = st.multiselect(
        "Machines", machine_numbers, default=machine_numbers[: min(3, len(machine_numbers))],
        key="compare_machines", label_visibility="collapsed",
    )

    st.markdown('<div class="section-label" style="margin-top:16px;">Select Parameters (leave empty for all)</div>', unsafe_allow_html=True)
    compare_params = st.multiselect(
        "Parameters", parameters, key="compare_params", label_visibility="collapsed"
    )

    st.write("")
    if compare_machines:
        rows = compare_params if compare_params else parameters
        comp_df = df.loc[rows, compare_machines]
        comp_df = comp_df.dropna(how="all")
        st.dataframe(comp_df, use_container_width=True, height=min(600, 45 + 35 * len(comp_df)))

        csv = comp_df.to_csv().encode("utf-8")
        st.download_button(
            "⬇ Download comparison as CSV", csv,
            file_name=f"{selected_type}_comparison.csv", mime="text/csv",
        )
    else:
        st.info("Select at least one machine to compare.")

# ---- Tab 3: Full Spec Sheet -------------------------------------------------
with tab_full:
    search = st.text_input("🔎 Filter parameters", placeholder="e.g. spindle, travel, load...")
    display_df = df.copy()
    if search:
        display_df = display_df[display_df.index.str.contains(search, case=False, na=False)]

    st.dataframe(display_df, use_container_width=True, height=min(700, 45 + 35 * len(display_df)))

    csv_full = display_df.to_csv().encode("utf-8")
    st.download_button(
        "⬇ Download full spec sheet as CSV", csv_full,
        file_name=f"{selected_type}_full_spec_sheet.csv", mime="text/csv",
    )

st.markdown(h("""
<div class="app-footer">
    Machine Specification System &nbsp;·&nbsp; data-driven from Excel &nbsp;·&nbsp; built for industrial use
</div>
"""), unsafe_allow_html=True)