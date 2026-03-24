import streamlit as st
import pandas as pd
from constants import ERA_COLS

DISPLAY_COLS = ["Name", "Type", "Role", "PV", "Size", "Move",
                "Short", "Medium", "Long", "Overheat", "Armor", "Structure", "Specials"]


def render_browser_tab(filtered: pd.DataFrame):
    st.write(f"**{len(filtered):,}** units match")

    selection = st.dataframe(
        filtered[DISPLAY_COLS],
        use_container_width=True,
        height=450,
        hide_index=True,
        on_select="rerun",
        selection_mode="single-row",
        column_config={"Name": st.column_config.Column(pinned=True)},
    )

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

            in_lance = selected_name in st.session_state.lance_units
            if in_lance:
                if st.button("Remove from lance"):
                    st.session_state.lance_units.remove(selected_name)
                    st.rerun()
            else:
                if st.button("Add to lance"):
                    st.session_state.lance_units.append(selected_name)
                    st.rerun()

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
            era_rows = [
                {"Era": era, "Factions": unit.get(era)}
                for era in ERA_COLS
                if pd.notna(unit.get(era)) and unit.get(era) not in ("Unknown", "Extinct")
            ]
            if era_rows:
                st.dataframe(pd.DataFrame(era_rows), use_container_width=True, hide_index=True)
            else:
                st.caption("No era availability data.")
