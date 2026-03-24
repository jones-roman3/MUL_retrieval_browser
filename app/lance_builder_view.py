import streamlit as st
import pandas as pd


def render_lance_builder_tab(df: pd.DataFrame):
    if not st.session_state.lance_units:
        st.caption('No units added yet. Browse to a unit and click "Add to lance".')
        return

    if st.button("Clear all"):
        st.session_state.lance_units.clear()
        st.rerun()

    to_remove = None
    for name in st.session_state.lance_units:
        matches = df[df["Name"] == name]
        if matches.empty:
            continue
        u = matches.iloc[0]
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"**{name}**")
            st.caption(f"{u['Type']} · PV {u['PV']} · {u['Move']}")
        with col2:
            if st.button("Remove", key=f"remove_{name}"):
                to_remove = name
        st.divider()

    if to_remove:
        st.session_state.lance_units.remove(to_remove)
        st.rerun()
