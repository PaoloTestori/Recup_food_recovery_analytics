import streamlit as st


pages = [
    st.Page("pages/1_Homepage.py", title="Homepage", icon="🍌"),
    st.Page("pages/2_Overview.py", title="Overview", icon="🍲"),
    st.Page("pages/3_Mercati.py", title="Mercati", icon="🥠"),
    st.Page("pages/4_Giornate di mercato.py", title="Giornate di mercato", icon="☀"),
]

pg = st.navigation(pages, position="sidebar", expanded=True)

pg.run()