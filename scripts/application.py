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
from PIL import Image

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
st.title("CAW oost brabant scraper")

image = Image.open('assets\CAW.png')

st.image(image)


################################
####### Scraper settings #######
################################

st.subheader("Scrape settings")

# Select sites to scrape
Sites = ['Zimmo', 'Century21']
SiteOptions = st.multiselect(
     'what sites do you want to check?', Sites)
st.write('You selected:', SiteOptions)

# Select driver for scraping
drivers = ['\chromedriver']
driverChoice = st.selectbox(
     'What internet driver should be used?', drivers)
st.write('You selected:', driverChoice)

# Give further constraintson the scrape focus
title = st.text_input('On what city do you want to focus?', 'City name')
st.write('The current chosen city is', title)

##############################
####### Scrape actions #######
##############################

buttonPress = st.button('Scrape')

status = 'Idle'
status_message = st.empty()

if(buttonPress):
    status = 'Processing'

    for scraper in SiteOptions:
        status_message.markdown('Loading')
        if (scraper == 'Century21'): 
            import drivers.Century21Scraper as ScraperObject
        if (scraper == 'ImmoM'): 
            import drivers.ImmomScraper as ScraperObject
        
        try:
            driver = ScraperObject.setDriver(driverChoice)
        except:
            status_message.markdown('Driver error')
            continue

        try:
            links = ScraperObject.fetchLinks(driver,'3000','FOR_RENT')
        except:
            status_message.markdown('Link gathering error')
            
        progress_bar = st.progress(0)
        progress = 0
        for link in links:
            try:
                ScraperObject.checkLink('\chromedriver',link)
            except:
                status_message.markdown('Data gathering error')

            progress = progress + (1/len(links))
            progress_bar.progress(progress)
        
        progress_bar.progress(100)
    status = 'Done'
    status_message.markdown('done')

    
else:
    status = 'Idle'
    status_message.markdown(' ')

################################
####### Data visualization #####
################################

if (status == 'Done'):
    data = get_data()

    # Set colums
    cols = st.columns([4, 1, 1, 1, 1])

    # Selection screen
    with cols[0]:
        # Title
        st.subheader("Gevonden items")
        st.text("Selecteer rij voor meer info")
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
                height = "300px",
                update_mode=GridUpdateMode.SELECTION_CHANGED)
            
        # Selected data
        selected_row = selcted_class["selected_rows"]
        selected_row = pd.DataFrame(selected_row)

        # Show map
        st.map()

        try:
            selected_data = data[data.Id == selected_row.iloc[0].Id]
        except:
            selected_data = data.iloc[:1]

    # Information screen
    with cols[1]:
        # Title
        st.markdown("## Informatie")

    for col in cols[2:]:
        col.markdown('##')
        col.markdown('##')


    for i in range(len(selected_data.columns)):
        col = selected_data.columns[i]
        print()
        cols[i% 4 + 1].write("#### " + col)
        cols[i% 4 + 1].write(selected_data[col].iloc[0])
