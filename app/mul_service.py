import pandas as pd
import streamlit as st
from pathlib import Path

STAT_COLS = ["PV", "Size", "Short", "Medium", "Long", "Extreme", "Overheat", "Armor", "Structure", "Threshold"]

TYPE_NAMES = {
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
    df["Type"] = df["Type"].map(lambda x: TYPE_NAMES.get(x, x))
    return df, csvs[0].name
