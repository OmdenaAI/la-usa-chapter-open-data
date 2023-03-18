import streamlit as st
import geopandas
import numpy as np
import pandas as pd
from shapely.geometry import Point
import missingno as msn
import seaborn as sns
import matplotlib.pyplot as plt
import folium
import asyncio
from streamlit_folium import st_folium

# Define the Streamlit app
def app():
    # Add a title to the app
    st.title("Hospital and Medical Centers")
    st.set_option('deprecation.showPyplotGlobalUse', False)

    # Load the dataset
    hospital = geopandas.read_file("Hospitals_and_Medical_Centers.geojson")
    inpatient = pd.read_csv('inpatientCharges.csv')
    hospital_loc = pd.read_csv('us_hospital_locations.csv')
    rating = pd.read_csv('Hospital_rating.csv',  encoding='ISO-8859-1')
    doctors = pd.read_csv('doctors.csv')

    # Subset data to California- LA

    # Filter the dataframes based on California state for the providers
    inpatient = inpatient.loc[inpatient['Provider State'] == "CA"]
    inpatient.drop_duplicates()

    hospital_loc = hospital_loc.loc[hospital_loc['CITY'] == "LOS ANGELES"]
    hospital_loc.drop_duplicates()

    rating = rating.loc[rating['City'] == "LOS ANGELES"]
    rating.dropna(axis=1, inplace= True)

    doctors = doctors.loc[doctors['County'] == "Los Angeles"]

    # Merge datasets
    #do inner join on inpatient and rating datasets
    inpatient_plus_rating = pd.merge(inpatient, rating, left_on=['Provider Id'],right_on=["Provider ID"])
    #inner join hospital location dataset to the merged data using Provider Name
    hosp_df = pd.merge(inpatient_plus_rating, hospital_loc, left_on=['Provider Name'],right_on=["NAME"])


    # Remove unnecessary columns
    hospital = hospital.drop(columns=['ext_id', 'date_updated', 'dis_status', 'email', 'phones', 'url', 'source', 'OBJECTID', 'addrln2'])

    # Remove rows with missing values
    hospital = hospital.dropna(subset=['cat3', 'org_name', 'addrln1', 'city', 'state', 'hours', 'zip'])

    # Some pre-processing
    # we have to rename the column city in the hosp_df
    # rename the "city" column to "City"
    hosp_df = hosp_df.rename(columns={'City': 'city'})
    # Format the values in the City column
    hosp_df['city'] = hosp_df['city'].apply(lambda x: ' '.join(word.capitalize() for word in x.split()))
    hosp_df[' Average Covered Charges '] = hosp_df[' Average Covered Charges '].str[1:].astype(float)
    hosp_df[' Average Total Payments '] = hosp_df[' Average Total Payments '].str[1:].astype(float)
    hosp_df['Average Medicare Payments'] = hosp_df['Average Medicare Payments'].str[1:].astype(float)

    # Visualizations
    # plot for beds
    st.subheader("Count of Beds")
    column = hosp_df['BEDS']
    plt.hist(column, bins=20, color='blue', edgecolor='black')
    plt.xlabel('BEDS')
    plt.ylabel('COUNT')
    plt.title('Histogram of Your Beds')
    st.pyplot()

    # plot for bed vs hospital name
    st.subheader("Joint plot for Beds and Hospital name")
    sns.jointplot(data=hosp_df, x='BEDS', y='Hospital Name', height=8)
    st.pyplot()

    # plot of hospital rating
    st.subheader("Hospital Rating")
    st.text("3 denotes a good rating for the hospital")
    sns.set(rc={'figure.figsize':(15,10)});
    sns.countplot(x=hosp_df["Hospital overall rating"]);
    st.pyplot()

    # plot of emergency services
    st.subheader("Total emergency services available")
    sns.set(rc={'figure.figsize':(8,8)});
    sns.countplot(x=hosp_df["Emergency Services"]);
    st.pyplot()

    # plot trauma count
    st.subheader("Trauma vs Count")
    sns.set(rc={'figure.figsize':(15,10)})
    sns.countplot(y=hosp_df["TRAUMA"])
    st.pyplot()

    # plot ownership of the hospitals
    st.subheader("Hospital owenership")
    st.text("Most ownerships is proprietary based.")
    sns.set(rc={'figure.figsize':(15,10)});
    sns.countplot(y=hosp_df["Hospital Ownership"]);
    st.pyplot()

    # plot avg covered charges by the provider names
    st.subheader("Average charges based on provider name with location")
    hosp_df_avg = hosp_df.groupby(['Provider Name', 'LATITUDE', 'LONGITUDE'])[[' Average Covered Charges ']].mean().sort_values(by=[' Average Covered Charges '], ascending=False)
    st.dataframe(hosp_df_avg)

    # plot activities for doctor
    st.subheader("Activities in Medicine based on doctors")
    doctors['Activities in Medicine'].value_counts(sort=True).plot.bar(rot=90)
    st.pyplot()

    # plot for areas practiced by the doctor
    st.subheader("Department of the doctors")
    doctors['Primary Area of Practice'].value_counts(sort=True).plot.bar(rot=90)
    st.pyplot()

    # Create a map using Folium
    st.subheader("Map of Hospitals and Medical Centers")
    m = folium.Map(location=[20,0], tiles="OpenStreetMap", zoom_start=2)
    for i in range(0,len(hospital)):
        folium.Marker(
            location=[hospital.iloc[i]['latitude'], hospital.iloc[i]['longitude']],
            popup=hospital.iloc[i]['Name'],
        ).add_to(m)
    st_data = st_folium(m, width = 725)

# Run the Streamlit app
app()
