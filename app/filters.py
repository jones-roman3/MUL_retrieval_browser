import streamlit as st
import pandas as pd
from constants import ERA_COLS, TYPE_HIERARCHY


def _build_type_option_map():
    options = []
    option_map = {}
    for name, children in TYPE_HIERARCHY:
        options.append(name)
        option_map[name] = set(children) if children else {name}
        if children:
            for child in children:
                label = f"  └─ {child}"
                options.append(label)
                option_map[label] = {child}
    return options, option_map


def render_sidebar_and_filter(df: pd.DataFrame) -> pd.DataFrame:
    type_options, type_option_map = _build_type_option_map()

    with st.sidebar:
        st.header("Filters")
        search = st.text_input("Search name / specials")
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

    # Apply basic filters
    mask = pd.Series(True, index=df.index)
    if search:
        q = search.lower()
        mask &= (df["Name"].str.lower().str.contains(q, na=False, regex=False) |
                 df["Specials"].str.lower().str.contains(q, na=False, regex=False))
    if sel_types:
        resolved = set()
        for opt in sel_types:
            resolved |= type_option_map[opt]
        mask &= df["Type"].isin(resolved)
    if sel_roles:
        mask &= df["Role"].isin(sel_roles)
    if sel_era != "(any)":
        if sel_faction != "(any)":
            mask &= df[sel_era].str.contains(sel_faction, na=False, case=False)
        else:
            mask &= ~df[sel_era].isin(["Unknown", "Extinct"]) & df[sel_era].notna()

    pre_filtered = df[mask]

    # Advanced filters (ranges derived from pre_filtered)
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

    adv_mask = (
        pre_filtered["PV"].between(*pv_range) &
        pre_filtered["Size"].between(*sel_sizes) &
        pre_filtered["Short"].between(*sel_short) &
        pre_filtered["Medium"].between(*sel_med) &
        pre_filtered["Long"].between(*sel_long) &
        pre_filtered["MoveVal"].between(*sel_move) &
        pre_filtered["JumpVal"].between(*sel_jump)
    )

    return pre_filtered[adv_mask].reset_index(drop=True)
