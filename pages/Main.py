import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
from scipy.optimize import curve_fit

st.set_page_config(layout="wide")

df = pd.read_csv("data/WorldContinent-annual-co2-emissions.csv")
df_aviation_demand = pd.read_csv("data/annual-co-emissions-from-aviation.csv")
df_emission_by_sectors = pd.read_csv("data/co-emissions-by-sector.csv")

df_world_co2 = df[(df["Entity"] == "World") & (df["Year"].between(2019, 2023))]
df_aviation = df_aviation_demand[(df_aviation_demand["Entity"] == "World") & (df_aviation_demand["Year"].between(2019, 2023))]

#################################
## INTRODUCTION 
#################################

st.markdown("<h1 style='text-align: center;'> Analyse der CO2-Emissionen in der Welt</h1>", 
                    unsafe_allow_html=True)
st.write("")

#################################
## LINIAR CHART 
#################################

with st.container(border=True):
    st.markdown("<h3 style='text-align: center;'>Annual CO₂ Emissions by Regions</h3>", unsafe_allow_html=True)
    
    st.write('Die globalen CO₂-Emissionen sind seit 1950 kontinuierlich gestiegen und erreichten im Jahr 2023 etwa 37,8 Milliarden Tonnen. Trotz des Wachstums haben sich die jährlichen Zuwächse in den letzten sieben Jahren aufgrund von Europa und Nordamerika verlangsamt. Europa hat seine Emissionen in den letzten Jahren reduziert und trägt etwa 7 % zu den globalen CO₂-Emissionen bei.')

    countries_line = df['Entity'].unique()
    selected_countries_line = st.multiselect('Select countries:', countries_line, default=countries_line[:5], key='multiselect_line')
    filtered_df_line = df[df['Entity'].isin(selected_countries_line)]
    
    fig1 = px.line(
        filtered_df_line,
        x="Year",
        y="Annual CO₂ emissions",
        color="Entity",
        labels={"Year": "Year", "Annual CO₂ emissions": "Annual CO₂ Emissions (tonnes)", "Entity": "Country"}
    )

    fig1.update_layout(
        width=1200,  
        height=500,  
        margin=dict(l=40, r=40, t=40, b=40)
    )

    st.plotly_chart(fig1)


#################################
## EMISSION BY SECTORS AND PIE CHART
#################################
with st.container(border=True):
    st.markdown("<h3 style='text-align: center;'>Annual CO₂ Emissions by Countries</h3>", 
                        unsafe_allow_html=True)
    with st.container(border=True): 
            col3, col4 = st.columns(2)

            # EMISSION BY AIRPLANE
            with col4:
                with st.container(border=True):
                    st.markdown("<h5 style='text-align: center;'> CO₂ Emissions from Aviation by Country</h5>", unsafe_allow_html=True)

                    df = pd.DataFrame(df_aviation_demand)
                    countries = st.multiselect("Select countries", df['Entity'].unique())

                    if countries:
                        df_filtered = df[df['Entity'].isin(countries)]

                        fig = px.line(df_filtered, x="Year", 
                                    y="Total annual CO₂ emissions from aviation", 
                                    color="Entity",  
                                    markers=True, width=550, height=558)

                        st.plotly_chart(fig)
                    else:
                        st.write("Please select at least one country.")

            # PIECHART
            with col3:
                with st.container(border=True):
                    tab1, tab2 = st.tabs(["Linear Chart", "Pie Chart"])
                    with tab2: 
                        st.markdown("<h5 style='text-align: center;'> CO₂ emissions by Sector and Country</h5>", unsafe_allow_html=True)

                        df_emission_by_sectors.columns = df_emission_by_sectors.columns.str.strip()

                        country = st.selectbox("Select Country", df_emission_by_sectors["Entity"].unique())
                        year = st.slider("Select Year", min_value=int(df_emission_by_sectors["Year"].min()), max_value=int(df_emission_by_sectors["Year"].max()), value=2021)

                        filtered_df = df_emission_by_sectors.loc[
                            (df_emission_by_sectors["Entity"] == country) & (df_emission_by_sectors["Year"] == year)
                        ]

                        if filtered_df.empty:
                            st.warning(f"No data available for {country} in {year}")
                            st.stop()

                        sectors = [
                            "Buildings", 
                            "Industry", 
                            "Land use change and forestry", 
                            "Other fuel combustion", 
                            "Transport", 
                            "Manufacturing and construction", 
                            "Energy production", 
                            "Electricity and heat", 
                            "Bunker fuels"
                        ]

                        missing_columns = [col for col in sectors if col not in filtered_df.columns]
                        if missing_columns:
                            st.error(f"Missing columns: {missing_columns}")
                            st.stop()

                        values = filtered_df[sectors].values.flatten()
                        labels = sectors

                        valid_indices = (pd.notna(values)) & (values > 0)
                        values = values[valid_indices]
                        labels = [labels[i] for i in range(len(labels)) if valid_indices[i]]

                        fig = px.pie(names=labels, values=values, width=580)
                        st.plotly_chart(fig)
                    with tab1: 
                        st.markdown("<h5 style='text-align: center;'> CO₂ emissions by Country</h5>", unsafe_allow_html=True)

                        df_emission_by_sectors.columns = df_emission_by_sectors.columns.str.strip()

                        country = st.selectbox("Select Country", df_emission_by_sectors["Entity"].unique(), key="country_selectbox")

                        filtered_df = df_emission_by_sectors.loc[
                            df_emission_by_sectors["Entity"] == country
                        ]

                        if filtered_df.empty:
                            st.warning(f"No data available for {country}")
                            st.stop()

                        sectors = [
                            "Buildings", 
                            "Industry", 
                            "Land use change and forestry", 
                            "Other fuel combustion", 
                            "Transport", 
                            "Manufacturing and construction", 
                            "Energy production", 
                            "Electricity and heat", 
                            "Bunker fuels"
                        ]

                        missing_columns = [col for col in sectors if col not in filtered_df.columns]
                        if missing_columns:
                            st.error(f"Missing columns: {missing_columns}")
                            st.stop()

                        fig = go.Figure()

                        for sector in sectors:
                            if sector in filtered_df.columns:
                                fig.add_trace(go.Scatter(
                                    x=filtered_df["Year"], 
                                    y=filtered_df[sector],
                                    mode='lines+markers', 
                                    name=sector
                                ))

                        fig.update_layout(
                            title=f"CO₂ Emissions by Sector in {country}",
                            xaxis_title="Year",
                            yaxis_title="CO₂ Emissions",
                            template="plotly_dark", 
                            width = 580, 
                            height=500
                        )

                        st.plotly_chart(fig)


#################################
## SCATTERGEO
#################################
with st.container(border=True):
    st.markdown("<h3 style='text-align: center;'>Top 50 busiest airports in the world. Year 2022. </h3>", unsafe_allow_html=True)
    st.write("")
    col5, col6 = st.columns([2.5, 1.5])
    with col5: 
        with st.container(border=True, height=800): 
        
            df_bussiest_airports = pd.read_csv("data/modified_busiest_airports_2022.csv")

            fig = go.Figure(go.Scattergeo(
                lat=df_bussiest_airports['lat'],
                lon=df_bussiest_airports['long'],
                text=df_bussiest_airports.apply(lambda row: f"{row['Airport']}<br>{row['Location']}<br>Passengers: {row['Total passengers']:,}", axis=1),  
                hoverinfo="text",  
                marker=dict(
                    size=df_bussiest_airports['Total passengers'] / 1000000,
                    color=df_bussiest_airports['Total passengers'],  
                    colorscale='Viridis',  
                    showscale=True,  
                    opacity=0.6  
                ),
            ))

            fig.update_geos(
                projection_type="orthographic",
                showland=True,
                landcolor="white",  
                showcoastlines=True,
                coastlinecolor="grey",  
                showcountries=True,  
                countrycolor="grey",  
                showocean=True,  
                oceancolor='#4C78A8',  
            )

            fig.update_layout(
                height=700,  
                width=700
            )
            st.plotly_chart(fig)

    with col6: 
        with st.container(border=True, height=800):  
            st.table(df_bussiest_airports[['Country', 'Location', 'Total passengers']])


#################################
## LOGISTIK REGESSION 
#################################

with st.container(border=True):
    st.markdown("<h3 style='text-align: center;'>Prediction with Logistic Regression for CO₂ Emissions by Region</h3>", unsafe_allow_html=True)
    st.write('Meine Prognosen gehen davon aus, dass die Emissionen bis 2050 auf 47,00 Milliarden Tonnen ansteigen könnten und trotz 2100, wenn der Trend anhält, die Emissionen 52 Milliarden Tonnen betragen könnten.')

    log_reg_df = pd.read_csv("data/WorldContinent-annual-co2-emissions.csv")

    countries_logistic = log_reg_df['Entity'].unique()
    selected_countries_logistic = st.multiselect('Select countries', countries_logistic, default=countries_logistic[:5], key='multiselect_logistic')
    filtered_df_logistic = log_reg_df[log_reg_df['Entity'].isin(selected_countries_logistic)]
    
    def logistic(x, L, x0, k, b):
        return L / (1 + np.exp(-k * (x - x0))) + b

    fig2 = px.scatter(
        filtered_df_logistic,
        x="Year",
        y="Annual CO₂ emissions",
        color="Entity",
        labels={"Year": "Year", "Annual CO₂ emissions": "Annual CO₂ Emissions (tonnes)", "Entity": "Country"}
    )

    for country in selected_countries_logistic:
        country_data = filtered_df_logistic[filtered_df_logistic["Entity"] == country]
        x_data = country_data["Year"].values
        y_data = country_data["Annual CO₂ emissions"].values

        if len(x_data) > 5:
            try:
                popt, _ = curve_fit(logistic, x_data, y_data, maxfev=10000, p0=[max(y_data), np.median(x_data), 1, min(y_data)])

                x_fit = np.linspace(min(x_data), 2100, 100).astype(int)  
                y_fit = logistic(x_fit, *popt)

                fig2.add_scatter(
                    x=x_fit, 
                    y=y_fit, 
                    mode='lines', 
                    name=f"Vorhersage: {country}",
                    hovertemplate=f'Region: {country}<br>Year: %{{x:.0f}}<br>Emissions: %{{y:,.2f}} Tonnen'
                )
            except Exception as e:
                st.warning(f"Could not fit logistic regression for {country}: {e}")

    fig2.update_layout(
        width=1200,  
        height=500,  
        margin=dict(l=40, r=40, t=40, b=40)
    )

    st.plotly_chart(fig2)



