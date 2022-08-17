# Data Transformation
from importlib.resources import read_text
from select import select
import pandas as pd

# Visualization
import streamlit as st
from st_aggrid import AgGrid
from st_aggrid.grid_options_builder import GridOptionsBuilder
from st_aggrid.shared import GridUpdateMode
import plotly.express

#########################
####### FUNCTIONS #######
#########################

@st.cache
def get_data():
    df = pd.read_excel("./outputs/Merged_output.xlsx").drop("Unnamed: 0", axis=1).reset_index().rename(columns={"index": "Id"})
    return df


#########################
####### Dashboard #######
#########################

# Set wide layout
st.set_page_config(layout="wide", page_title="Unassigned Classes")

# Get data
data = get_data()

# Set colums
cols = st.columns(2)

# Selection screen
with cols[0]:
    # Title
    st.title("Selecteer rij voor meer info")
    selection_df = data[["Id", "site", "itemtype","rent", "monthly_fee", "bedrooms"]]
    # Create Ag Grid options
    gb = GridOptionsBuilder.from_dataframe(selection_df)
    gb.configure_pagination()
    gb.configure_side_bar()
    gb.configure_selection(selection_mode="single", use_checkbox=True)
    gb.configure_default_column(groupable=True, value=True, enableRowGroup=True)
    gridOptions = gb.build()

    selcted_class = AgGrid(
            selection_df, 
            gridOptions=gridOptions,
            fit_columns_on_grid_load=True,
            theme="dark",
            height = "610px",
            update_mode=GridUpdateMode.SELECTION_CHANGED)
        
    # Selected data
    selected_row = selcted_class["selected_rows"]
    selected_row = pd.DataFrame(selected_row)

    try:
        selected_data = data[data.Id == selected_row.iloc[0].Id]
    except:
        selected_data = data.iloc[:1]
    st.dataframe(selected_data)

# Information screen
with cols[1]:
    # Title
    st.title("Informatie")
    st.table(selected_data)

    st.map()