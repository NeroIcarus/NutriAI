import os
import pandas as pd
import streamlit as st

@st.cache_data
def load_main_db():
    if os.path.exists("main_course.csv"):
        return pd.read_csv("main_course.csv")
    return None

@st.cache_data
def load_side_db():
    if os.path.exists("side_dish.csv"):
        return pd.read_csv("side_dish.csv")
    return None