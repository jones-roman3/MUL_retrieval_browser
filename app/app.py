import streamlit as st
import pandas as pd
from pathlib import Path

st.set_page_config(page_title="Alpha Strike Unit Browser", layout="wide")

ERA_COLS = [
    "Star League (2571 - 2780)",
    "Early Succession War (2781 - 2900)",
    "Late Succession War - LosTech (2901 - 3019)",
    "Late Succession War - Renaissance (3020 - 3049)",
    "Clan Invasion (3050 - 3061)",
    "Civil War (3062 - 3067)",
    "Jihad (3068 - 3085)",
    "Early Republic (3086 - 3100)",
    "Late Republic (3101 - 3130)",
    "Dark Ages (3131 - 3150)",
    "ilClan (3151 - 9999)",
]

STAT_COLS = ["PV", "Size", "Short", "Medium", "Long", "Extreme", "Overheat", "Armor", "Structure", "Threshold"]


@st.cache_data
def load_data():
    # Use the most recently modified unit_list csv
    data_dir = Path(__file__).parent.parent / "data"
    csvs = sorted(data_dir.glob("unit_list*.csv"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not csvs:
        return None
    df = pd.read_csv(csvs[0])
    for col in STAT_COLS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)
    df["Specials"] = df["Specials"].fillna("")
    df["Variant"] = df["Variant"].fillna("")
    df["MoveVal"] = df["Move"].str.extract(r"(\d+)").astype(float).fillna(0).astype(int)
    df["JumpVal"] = df["Move"].str.extract(r"(\d+)\"j").astype(float).fillna(0).astype(int)
    df["Type"] = df["Type"].str.upper()
    type_names = {
        "AF": "Aerospace Fighter",
        "BA": "Battle Armor",
        "BD": "Building",
        "BM": "BattleMech",
        "CF": "Conventional Fighter",
        "CI": "Conventional Infantry",
        "CV": "Combat Vehicle",
        "IM": "IndustrialMech",
        "JS": "Jumpship",
        "PM": "Protomech",
        "SC": "Small Craft",
        "SS": "Support Satellite",
        "SV": "Support Vehicle",
    }
    df["Type"] = df["Type"].map(lambda x: type_names.get(x, x))
    return df, csvs[0].name


result = load_data()
if result is None:
    st.error("No unit_list CSV found. Run the notebook first.")
    st.stop()

df, csv_name = result

st.title("Alpha Strike Unit Browser")
st.caption(f"Source: `{csv_name}` — {len(df):,} units")

# ── Basic filters ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("Filters")

    search = st.text_input("Search name / specials")

    TYPE_HIERARCHY = [
        ("BattleMech", None),
        ("Combat Vehicle", None),
        ("Infantry", ["Battle Armor", "Conventional Infantry"]),
        ("Aerospace", ["Aerospace Fighter", "Conventional Fighter", "Jumpship", "Small Craft", "Support Satellite"]),
        ("IndustrialMech", None),
        ("Protomech", None),
        ("Building", None),
        ("Support Vehicle", None),
    ]
    type_options = []
    type_option_map = {}  # label -> set of actual type values
    for name, children in TYPE_HIERARCHY:
        type_options.append(name)
        type_option_map[name] = set(children) if children else {name}
        if children:
            for child in children:
                label = f"  └─ {child}"
                type_options.append(label)
                type_option_map[label] = {child}

    sel_types = st.multiselect("Unit Type", type_options, default=["BattleMech", "Combat Vehicle"])

    roles = sorted(df["Role"].dropna().unique())
    sel_roles = st.multiselect("Role", roles)

    st.subheader("Era availability")
    sel_era = st.selectbox("Era", ["(any)"] + ERA_COLS)
    if sel_era != "(any)":
        era_factions = sorted(
            {f.strip() for cell in df[sel_era].dropna() for f in str(cell).split(",")
             if f.strip() not in ("Unknown", "Extinct", "")}
        )
        sel_faction = st.selectbox("Faction", ["(any)"] + era_factions)
    else:
        sel_faction = "(any)"

# ── Apply basic filters to get pre_filtered ───────────────────────────────────
basic_mask = pd.Series(True, index=df.index)

if search:
    q = search.lower()
    basic_mask &= df["Name"].str.lower().str.contains(q, na=False, regex=False) | df["Specials"].str.lower().str.contains(q, na=False, regex=False)

if sel_types:
    resolved_types = set()
    for opt in sel_types:
        resolved_types |= type_option_map[opt]
    basic_mask &= df["Type"].isin(resolved_types)

if sel_roles:
    basic_mask &= df["Role"].isin(sel_roles)

if sel_era != "(any)":
    if sel_faction != "(any)":
        basic_mask &= df[sel_era].str.contains(sel_faction, na=False, case=False)
    else:
        basic_mask &= ~df[sel_era].isin(["Unknown", "Extinct"]) & df[sel_era].notna()

pre_filtered = df[basic_mask]

# ── Advanced filters (ranges derived from pre_filtered) ───────────────────────
with st.sidebar:
    with st.expander("Advanced Filters"):
        def slider(label, col):
            lo = int(pre_filtered[col].min()) if not pre_filtered.empty else int(df[col].min())
            hi = int(pre_filtered[col].max()) if not pre_filtered.empty else int(df[col].max())
            if lo == hi:
                return st.slider(label, lo, lo + 1, (lo, lo))
            return st.slider(label, lo, hi, (lo, hi))

        pv_range  = slider("PV range", "PV")
        sel_sizes = slider("Size range", "Size")
        sel_short = slider("Short range", "Short")
        sel_med   = slider("Medium range", "Medium")
        sel_long  = slider("Long range", "Long")
        sel_move  = slider("Movement range", "MoveVal")
        sel_jump  = slider("Jump Movement range", "JumpVal")

# ── Apply advanced filters ────────────────────────────────────────────────────
adv_mask = (
    pre_filtered["PV"].between(*pv_range) &
    pre_filtered["Size"].between(*sel_sizes) &
    pre_filtered["Short"].between(*sel_short) &
    pre_filtered["Medium"].between(*sel_med) &
    pre_filtered["Long"].between(*sel_long) &
    pre_filtered["MoveVal"].between(*sel_move) &
    pre_filtered["JumpVal"].between(*sel_jump)
)

filtered = pre_filtered[adv_mask].reset_index(drop=True)
st.write(f"**{len(filtered):,}** units match")

# ── Table ────────────────────────────────────────────────────────────────────
display_cols = ["Name", "Type", "Role", "PV", "Size", "Move",
                "Short", "Medium", "Long", "Overheat", "Armor", "Structure", "Specials"]
selection = st.dataframe(
    filtered[display_cols],
    use_container_width=True,
    height=450,
    hide_index=True,
    on_select="rerun",
    selection_mode="single-row",
    column_config={"Name": st.column_config.Column(pinned=True)},
)

# ── Detail panel ─────────────────────────────────────────────────────────────
st.divider()
st.subheader("Unit detail")

selected_rows = selection.selection.rows
selected_name = filtered.iloc[selected_rows[0]]["Name"] if selected_rows else None

if selected_name:
    unit = filtered[filtered["Name"] == selected_name].iloc[0]
    col1, col2 = st.columns([1, 2])

    with col1:
        if unit.get("ImageURL"):
            st.image(unit["ImageURL"], width=220)
        st.markdown(f"### {unit['Name']}")
        st.markdown(f"**Class:** {unit['Class']}  \n**Variant:** {unit['Variant']}  \n**Role:** {unit['Role']}  \n**Type:** {unit['Type']}")

    with col2:
        st.markdown("**Alpha Strike stats**")
        stat_data = {
            "PV": unit["PV"], "Size": unit["Size"], "Move": unit["Move"],
            "Short": unit["Short"], "Medium": unit["Medium"],
            "Long": unit["Long"], "Extreme": unit["Extreme"],
            "Overheat": unit["Overheat"], "Armor": unit["Armor"],
            "Structure": unit["Structure"], "Threshold": unit["Threshold"],
        }
        cols = st.columns(4)
        for i, (k, v) in enumerate(stat_data.items()):
            cols[i % 4].metric(k, v)

        if unit["Specials"]:
            st.markdown(f"**Specials:** `{unit['Specials']}`")

        st.markdown("**Era availability**")
        era_rows = []
        for era in ERA_COLS:
            val = unit.get(era, "Unknown")
            if pd.notna(val) and val not in ("Unknown", "Extinct"):
                era_rows.append({"Era": era, "Factions": val})
        if era_rows:
            st.dataframe(pd.DataFrame(era_rows), use_container_width=True, hide_index=True)
        else:
            st.caption("No era availability data.")
