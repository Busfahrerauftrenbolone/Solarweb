def choosing_variables():
    # Date selection
    with st.sidebar:
        st.sidebar.markdown("**First select the data range you want to analyze:** 👇")
        date = st.date_input("Choose a August 2022 date",datetime.date(2022, 8, 6))
    
        # Country selection
        all_options_country = df_heatSpots['pais'].unique()
        select_country = st.multiselect("Country options (Leave blank to allow all countries)", all_options_country, ['Brasil'])

        if len(select_country) > 0:
            temp_select_country = select_country
        else:
            temp_select_country = all_options_country

        # Satellite selection
        all_options_satellite = df_heatSpots['satelite'].unique()
        select_satellite = st.multiselect("satellite options (Leave blank to allow all satellites)", all_options_satellite, ['NOAA-20'])

        if len(select_satellite) > 0:
            temp_select_satellite = select_satellite
        else:
            temp_select_satellite = all_options_satellite

    return date, temp_select_country, temp_select_satellite


df_heatSpots = importing_dataset()

# Defining initial date country and satellite variables
date = datetime.datetime.strptime('19082022', "%d%m%Y").date()
temp_select_country = ['Brasil']
temp_select_satellite = ['NOAA-20']

# Hidding the possible options
date, temp_select_country, temp_select_satellite = choosing_variables()