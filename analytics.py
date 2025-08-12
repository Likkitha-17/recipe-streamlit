analytics.py
import streamlit as st

def inject_ga():
    ga_code = """
    <!-- Google tag (gtag.js) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-HPV312DF1Q"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){dataLayer.push(arguments);}
      gtag('js', new Date());

      gtag('config', 'G-HPV312DF1Q');
    </script>
    """
    st.markdown(ga_code, unsafe_allow_html=True)
