import streamlit as st
from mul_service import load_data
from filters import render_sidebar_and_filter
from browser_view import render_browser_tab
from lance_builder_view import render_lance_builder_tab

st.set_page_config(page_title="Alpha Strike Unit Browser", layout="wide")

if "lance_units" not in st.session_state:
    st.session_state.lance_units = []

result = load_data()
if result is None:
    st.error("No unit_list CSV found. Run the notebook first.")
    st.stop()

df, csv_name = result

st.title("Alpha Strike Unit Browser")
st.caption(f"Source: `{csv_name}` — {len(df):,} units")

filtered = render_sidebar_and_filter(df)

n = len(st.session_state.lance_units)
browser_label = "Browse"
lance_label = f"Lance Builder ({n})" if n else "Lance Builder"

browse_tab, lance_tab = st.tabs([browser_label, lance_label])

with browse_tab:
    render_browser_tab(filtered)

with lance_tab:
    render_lance_builder_tab(df)
