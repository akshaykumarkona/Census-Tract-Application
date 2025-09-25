# import streamlit as st
# import geopandas as gpd
# import pandas as pd
# from streamlit_folium import st_folium
# import folium
# import json
# import os
# from folium.features import GeoJsonTooltip
# from shapely.geometry import Polygon
# from utils import *
# from folium.plugins import Draw
# import requests

# # Check session state
# if "show_home_modal" not in st.session_state:
#     st.session_state.show_home_modal = True

# # If modal should be shown
# if st.session_state.show_home_modal:
#     with st.container():
#         st.markdown("## 👋 Welcome to Crash Prediction App")
#         st.markdown("This app allows you to **Predict crash counts using ML models**")

#         # Disclaimer summary
#         st.markdown(r"""**Disclaimer:**  
#         The models behind this tool were trained on Kansas crash, weather, traffic, and demographic data from **2012–2016**, validated on **2017**, and tested on **2018–2019**. Using inputs from other geographical areas or years after 2019 may degrade performance and produce biased or unreliable results. By using this tool, you agree to the Terms of Usage below.
#         """)

#         # Terms of Usage with agreement checkbox
#         with st.expander("Terms of Usage"):
#             with open("C:/censustract/ui/terms_of_usage.md", "r", encoding="utf-8") as f:
#                 st.markdown(f.read())

#             agree = st.checkbox("I have read and agree to the Terms of Usage.", key="agree_terms")

#         # Link to paper
#         st.markdown("""
#         **For methods and limitations**, see the paper:  
#         *Comparative Geospatial Analysis of Weather-Related Impacts on Crash Frequency with Explainable Machine Learning: A Case for Kansas Census Tracts* (Working Paper)
#         """)

#         # Show Continue button only after agreement
#         if st.session_state.get("agree_terms", False):
#             if st.button("Continue to App"):
#                 st.session_state.show_home_modal = False
#                 st.rerun()
#         else:
#             st.info("Please review and agree to the Terms of Usage to continue.")
# else:
        
#     ST_MAP_CENTER = [38.4987789, -98.3200779]

#     st.header("Census Tract Application")

#     with st.sidebar:

#         role_options = ["Select a Role", "Highway Patrol Officer", "Researcher(Deep Dive)"]
#         input_role = st.selectbox("Choose your Role", options=role_options, index=0)

#         if input_role == "Select a Role":
#             st.warning("Please select a role to proceed.")
#             st.stop()

#     models_mapping = {
#                         "AdaBoost": 'AdaBoostClassifier_aggregate_model',
#                         "CatBoost": 'CatBoostClassifier_aggregate_model',
#                         "CatBoost Regression": 'catBoost_regression_pickled',
#                         "Gradient Boost": 'GradientBoostingClassifier_aggregate_model',
#                         "LightGBM": 'LGBMClassifier_aggregate_model',
#                         "Random Forest": 'RandomForestClassifier_aggregate_model',
#                         "TabNet": 'TabNetClassifier_aggregate_model',
#                         "XGBoost": 'XGBClassifier_aggregate_model'
#                     }


#     m = folium.Map(location=ST_MAP_CENTER, zoom_start=7)

#     # static_prediction_df = pd.read_csv(r"ui\data\static_crashes_week1.csv")

#     with open(r'C:\censustract_package\ui\configs\range_config.json', 'r') as f:
#             range_config = json.load(f)

#     with open(r'C:\censustract_package\ui\configs\tabnet_classifcation_range_config.json', 'r') as f:
#             tabnet_classification_range_config = json.load(f)

#     # Paths
#     geojson_paths = {
#         "kansas": r'C:\censustract_package\data\kansas.geojson',
#         "counties_base": r"C:\censustract_package\data\ks_county_files",
#         "county_info": r'C:\censustract_package\data\FRPP_GLC__United_States_April_8_2024.csv',
#         "tracts": r'C:\censustract_package\data\Tiger_2020_Boundaries/Tiger_2020_Boundaries.geojson',
#         "roads": r"C:\censustract_package\data\tl_2024_20_prisecroads/tl_2024_20_prisecroads_geojson/tl_2024_20_prisecroads.geojson",
#         # "valid_dmvt" : r"ui/data/all_dataset_dmvt.csv"
#         # "static_crashes": r"ui/data/static_crashes_week1.csv"
#     }

#     user_inputs = {}

#     county_names_df = cached_read_csv(geojson_paths["county_info"], encoding='ISO-8859-1')
#     kansas_counties = county_names_df[county_names_df['State Name'] == 'KANSAS']    

#     if input_role=='Highway Patrol Officer':
        
#         chosen_model="CatBoost" # considered this as the best model

#         # HP Officer selecting a county
#         # county_names_df = cached_read_csv(geojson_paths["county_info"], encoding='ISO-8859-1')
#         # kansas_counties = county_names_df[county_names_df['State Name'] == 'KANSAS']
#         # valid_dmvt_df = cached_read_csv(geojson_paths["valid_dmvt"], encoding='ISO-8859-1')

#         # st.write(kansas_counties.head())

#         with st.sidebar:
#             county_list = sorted(set(kansas_counties['County Name'].astype(str).str.capitalize()))
#             county_list.insert(0, "Select a County")  # Insert placeholder at the top

#             hpo_county_mode=st.selectbox("Choose how you'd like to select a County", ["Select County Selection Mode","List Selection", "Map Visualization"],index=0)

#             if hpo_county_mode=="Select County Selection Mode":
#                 st.warning("Please select a County Selection Mode to proceed")
#                 st.stop()

#         mean_values_demographic_variables_from_valid_dmvt={"totPop":3534.0, "povper":13.0, "hhnov":70.0, "pctnvh":6.0, "avgcmm":20.0, 
#                                                            "trnfrq":2.0, "jb45dr":30864.0, "drvpoi":15.0, 'wlkpoi':227.0,}

#         # ================================= Highway Patrol Officer HPO: List Selection =================================
#         if hpo_county_mode=="List Selection":

#                 with st.sidebar:
#                     hpo_selected_county = st.selectbox(
#                         "Choose a County",
#                         options=county_list,
#                         index=0  # This ensures the placeholder is selected by default
#                     )
#                     # Prevent execution if a valid county hasn't been selected
#                     if hpo_selected_county == "Select a County":
#                         st.warning("Please select a county to view the map.")
#                         st.stop()

                    
#                     # Selection for how many census tracts to choose
#                     tract_mode = st.selectbox(
#                         "Choose you Area Selection Style",
#                         options=["Choose you Area Selection Style","Single Census Tract", "Choose a road (select area on map)"]
#                     )

#                     if tract_mode == "Choose you Area Selection Style":
#                         st.warning("Please select how many census tract you want to select, to view the map.")
#                         st.stop()

#                     # Show warning popup if "Multiple Area Selection" is selected
#                     if tract_mode == "Choose a road (select area on map)":
#                         st.warning("If you select multiple census tracts, you must input variables for each selected census tract.")

#                 # ================================= HPO: List Selection :: Single Census Tract =================================
#                 if tract_mode == "Single Census Tract":

#                     # --------- Sidebar inputs: fragment + form (no rerun while sliding) ---------
#                     @st.fragment
#                     def hpo_single_inputs_fragment():
#                         with st.form("hpo_single_inputs_form", clear_on_submit=False):
#                             inputs = {}
#                             # Same inputs as before, but rendered INSIDE the form so they don't rerun on slide
#                             inputs.update(input_section_v2(
#                                 "Input Weather Variables",
#                                 classification_weather_keys,
#                                 tabnet_classification_range_config,
#                                 classification_weather_labels,
#                                 container=st,   # IMPORTANT: write into the form context
#                             ))
#                             inputs.update(input_section_v2(
#                                 "Input Traffic Characteristics",
#                                 traffic_keys_classification,
#                                 tabnet_classification_range_config,
#                                 traffic_keys_classification_labels,
#                                 container=st,   # IMPORTANT
#                             ))
#                             submitted = st.form_submit_button("Submit Inputs")
#                         if submitted:
#                             st.session_state["hpo_single"] = inputs
#                             st.success("Inputs submitted. Now click **Predict Crash Counts** below the map.")


#                     # Render the fragment INSIDE the sidebar (required by Streamlit)
#                     with st.sidebar:
#                         hpo_single_inputs_fragment()

#                     # --------- Map & Data (kept outside fragment so they don't rerender while sliding) ---------
#                     # Base boundary
#                     folium.GeoJson(
#                         cached_load_json(geojson_paths["kansas"]), name='Kansas Boundary',
#                         style_function=lambda f: {'fillOpacity': 0, 'color': 'black', 'weight': 3}
#                     ).add_to(m)

#                     # Counties frame (reloaded via cache)
#                     county_names_df = cached_read_csv(geojson_paths["county_info"], encoding='ISO-8859-1')
#                     kansas_counties = county_names_df[county_names_df['State Name'] == 'KANSAS']

#                     # All counties outlines
#                     folium.GeoJson(
#                         combine_geojsons(kansas_counties), name="County Boundaries",
#                         style_function=lambda f: {'fillOpacity': 0, 'color': 'black', 'weight': 1},
#                         tooltip=GeoJsonTooltip(fields=['name'], aliases=['County:'], localize=True)
#                     ).add_to(m)

#                     # Selected county highlight + fit
#                     selected_row = kansas_counties[kansas_counties["County Name"].str.capitalize() == hpo_selected_county]
#                     if not selected_row.empty:
#                         selected_geojson = combine_geojsons(selected_row)
#                         bounds = get_bounds(selected_geojson['features'])
#                         m.fit_bounds(bounds)

#                         folium.GeoJson(
#                             selected_geojson, name="Selected County",
#                             # style_function=lambda f: {'fillOpacity': 0, 'color': "#0077FF", 'weight': 3.5},
#                             style_function=lambda f: {'fillColor': 'gold','fillOpacity': 0.025},
#                             highlight_function=lambda f: {'fillColor': '#0077FF','fillOpacity': 0.15, 'color': "gold", 'weight': 3.5},

#                             tooltip=GeoJsonTooltip(fields=['name'], aliases=['County:'], localize=True)
#                         ).add_to(m)

#                         county_name = str(selected_row.iloc[0]["County Name"])
#                         st.subheader(f"You are viewing '{county_name.capitalize()}' County")
#                     else:
#                         st.warning("Selected county not found.")
#                         st.stop()

#                     with st.spinner("Loading visualization... Please wait."):
#                         # Tracts & Roads
#                         folium.GeoJson(
#                             cached_load_json(geojson_paths["tracts"]), name='Census Tracts',
#                             style_function=lambda f: {'fillOpacity': 0, 'color': "#150202", 'weight': 0.7},
#                             highlight_function=lambda f: {'fillColor': 'brown', 'color': 'brown', 'weight': 3.5, 'dashArray': '12, 12'},
#                             tooltip=GeoJsonTooltip(fields=['NAMELSAD'], aliases=['Tract:'], localize=True)
#                         ).add_to(m)

#                         folium.GeoJson(
#                             cached_load_json(geojson_paths["roads"]), name='Road Network',
#                             style_function=lambda f: {'weight': 1.5},
#                             highlight_function=lambda f: {'color': 'blue', 'weight': 2.5, 'dashArray': '4, 4'},
#                             tooltip=GeoJsonTooltip(fields=['FULLNAME'], aliases=['Road Name:'], localize=True)
#                         ).add_to(m)

#                     # Display the map
#                     with st.container():

#                         clicked_info = st_folium(m, width=700, height=600)
#                         st.markdown(
#                             """
#                             <style>
#                             iframe[title="folium_map"] { margin-bottom: -30px; }
#                             </style>
#                             """,
#                             unsafe_allow_html=True
#                         )
#                         # st.markdown("")  # optional spacing

#                         # Show which tract user interacted with
#                         if clicked_info and clicked_info.get("last_active_drawing"):
#                             tract_props = clicked_info["last_active_drawing"]["properties"]
#                             countyfp = tract_props.get("COUNTYFP", None)
#                             tract_name = tract_props.get("NAMELSAD", "Unknown")
#                             tract_id= tract_props.get("NAME", None)


#                             ## This code is to get the mean values of demographic variables for the selected census tract from valid dmvt data, but some tract ids are not present in all_dataset_dmvt.csv, 
#                             ## so that's why went with customized mean values for demographic variables from valid dmvt data

#                             # selected_tract_rows_df = valid_dmvt_df[valid_dmvt_df['CENSUS_TRACT']==tract_id] #filtering rows based on census tract id from Valid DMVT data
#                             # grouped = selected_tract_rows_df.groupby(['CENSUS_TRACT'])[["totPop", "povper", "hhnov", "pctnvh", "avgcmm", "trnfrq", "jb45dr", "drvpoi", 'wlkpoi']].mean()
#                             # # Getting the mean values of demographic variables for the selected census tract from valid dmvt data
#                             # mean_data_for_demographic_variables = {
#                             #             col.lower(): float(val)   
#                             #             for col, val in grouped.iloc[0].items()
#                             #         }


#                             county_row = kansas_counties[
#                                 kansas_counties["County Code"].astype(str).str.zfill(3) == str(countyfp).zfill(3)
#                             ]
#                             if not county_row.empty:
#                                 _county_name = county_row.iloc[0]["County Name"]
#                                 st.success(f"**Selected {tract_name}** is in **{_county_name} County**")
#                             else:
#                                 st.warning("County not found for the selected tract.")

#                         # --------- Predict (uses last submitted inputs from session_state) ---------
#                         predict_crashes = st.button("Predict Crash Counts")
#                         if predict_crashes:
#                             chosen_model = "CatBoost"  # fixed for HPO Single-Tract path

#                             if "hpo_single" not in st.session_state:
#                                 st.warning("Please submit inputs first (use the **Submit Inputs** button in the sidebar).")
#                                 st.stop()

#                             ui_inputs = st.session_state["hpo_single"]

#                             # Prepare inputs for Classification model (with avg_temp + demographic defaults)
#                             classification_inputs = {}
#                             for key in classification_weather_keys + demographic_keys + traffic_keys_classification + ["avg_temp"]:
#                                 if key in ui_inputs:
#                                     classification_inputs[key] = ui_inputs[key]
#                                 elif key == "avg_temp":
#                                     classification_inputs[key] = (ui_inputs['min_temp'] + ui_inputs['max_temp']) / 2
#                                 elif key in demographic_keys:
#                                     classification_inputs[key] = mean_values_demographic_variables_from_valid_dmvt.get(key, 0) #mean_data_for_demographic_variables.get(key,0)  # 
#                                 else:
#                                     classification_inputs[key] = 0  # Default if not provided

#                             # Convert booleans to strings for API compatibility
#                             for k in ['is_weekend', 'is_holiday']:
#                                 if k in classification_inputs:
#                                     classification_inputs[k] = str(classification_inputs[k])

#                             if chosen_model.strip() in models_mapping:
#                                 request_data = {
#                                     "model_name": models_mapping[chosen_model],
#                                     "inputs": classification_inputs
#                                 }
#                             else:
#                                 st.error("Unknown model selection.")
#                                 st.stop()

#                             # Call API (classification for Random Forest)
#                             try:
#                                 response = requests.post(
#                                     "http://127.0.0.1:8000/predict_classification",
#                                     json=request_data,
#                                     timeout=30
#                                 )
#                                 if response.status_code == 200:
#                                     result = response.json()
#                                     st.success(f"Predicted Crashes: {result.get('predicted_crashes')}")
#                                 else:
#                                     st.error(f"API Error: {response.status_code} - {response.text}")
#                             except Exception as e:
#                                 st.error(f"Request Error: {e}")

#                 # ================================= HPO: List Selection :: Choose a road (select area on map) =================================
#                 elif tract_mode == "Choose a road (select area on map)":

#                     selected_row = kansas_counties[kansas_counties["County Name"].str.capitalize() == hpo_selected_county]
#                     county_fp = str(selected_row.iloc[0]["County Code"]).zfill(3)
#                     county_name = str(selected_row.iloc[0]["County Name"]).zfill(3)

#                     st.subheader(f"You are viewing '{county_name.capitalize()}' County")

#                     # Add ALL Kansas counties (background layer)
#                     all_counties_geojson = combine_geojsons(kansas_counties)

#                     with st.spinner("Loading visualization... Please wait."):
#                         folium.GeoJson(
#                             all_counties_geojson,
#                             name="All County Boundaries",
#                             style_function=lambda f: {'fillOpacity': 0, 'color': 'gray', 'weight': 1},
#                             tooltip=GeoJsonTooltip(fields=['name'], aliases=['County:'], localize=True)
#                         ).add_to(m)

#                         folium.GeoJson(cached_load_json(geojson_paths["tracts"]), name='All Census Tracts',
#                             style_function=lambda f: {'fillOpacity': 0, 'color': "#150202", 'weight': 0.7},
#                             highlight_function=lambda f: {'fillColor': 'brown', 'color': 'brown', 'weight': 3.5},
#                             tooltip=GeoJsonTooltip(fields=['NAMELSAD'], aliases=['Tract:'], localize=True)).add_to(m)

#                     if not selected_row.empty:
#                         selected_geojson = combine_geojsons(selected_row)
#                         with st.spinner("Loading visualization... Please wait."):
#                             folium.GeoJson(
#                                 selected_geojson,
#                                 name="Selected County",
#                                 style_function=lambda f: {'fillColor': 'gold','fillOpacity': 0.025},
#                                 highlight_function=lambda f: {'fillColor': '#0077FF','fillOpacity': 0.15, 'color': "gold", 'weight': 3.5},
#                                 tooltip=GeoJsonTooltip(fields=['name'], aliases=['County:'], localize=True)
#                             ).add_to(m)

#                     bounds = get_bounds(selected_geojson['features'])
#                     m.fit_bounds(bounds)

#                     census_geojson = load_geojson(geojson_paths["tracts"])
#                     tracts_filtered = {
#                         "type": "FeatureCollection",
#                         "features": [feat for feat in census_geojson["features"]
#                                     if feat["properties"].get("COUNTYFP") == county_fp]
#                     }

#                     with st.spinner("Loading visualization... Please wait."):
#                         # HPO Selected County's  Census Tracts Visualization
#                         folium.GeoJson(
#                             tracts_filtered,
#                             name='Census Tracts',
#                             style_function=lambda f: {'fillOpacity': 0, 'color': "#150202", 'weight': 0.7},
#                             highlight_function=lambda f: {'fillColor': 'brown', 'color': 'brown', 'weight': 3.5, 'dashArray': '12, 12'},
#                             tooltip=GeoJsonTooltip(fields=['NAMELSAD'], aliases=['Tract:'], localize=True)
#                         ).add_to(m)

#                         # HPO Selected County's  Roads Visualization
#                         folium.GeoJson(cached_load_json(geojson_paths["roads"]), name='Road Network',
#                             style_function=lambda f: {'weight': 0.8},
#                             highlight_function=lambda f: {'color': 'blue', 'weight': 1.4, 'dashArray': '4, 4'},
#                             tooltip=GeoJsonTooltip(fields=['FULLNAME'], aliases=['Road Name:'], localize=True)).add_to(m)

#                     Draw(
#                         draw_options={
#                             'polyline': False,
#                             'polygon': False,
#                             'circle': False,
#                             'marker': False,
#                             'circlemarker': False,
#                             'rectangle': True
#                                 },
#                             edit_options={'edit': False}
#                         ).add_to(m)

#                     folium.LayerControl().add_to(m)
#                     with st.container():

                    
#                         # Show the map only once (interactive, no gap)
#                         clicked_info = st_folium(m, width=700, height=600)
#                         st.markdown(
#                         """
#                         <style>
#                         iframe[title="folium_map"] {
#                             margin-bottom: -30px;
#                         }
#                         </style>
#                         """,
#                         unsafe_allow_html=True
#                     )
                        
#                         # --- Debug or placeholder to keep layout tight ---
#                         st.markdown("")  # helps reduce iframe margin

#                         # Print clicked census tract
#                         if clicked_info and clicked_info.get("last_active_drawing"):
#                                 print("Entered Multiple Census Tracts Mode V1")
#                                 tract_props = clicked_info["last_active_drawing"]["properties"]
                                
#                                 countyfp = tract_props.get("COUNTYFP", None)
#                                 tract_name = tract_props.get("NAMELSAD", "Unknown")
#                                 tract_geoid = tract_props.get("GEOID", None)

#                                 # Lookup county
#                                 county_row = kansas_counties[kansas_counties["County Code"].astype(str).str.zfill(3) == str(countyfp).zfill(3)]
#                                 predict_crashes = st.button("Predict Crash Counts")

#                                 # # Rectangle selection Code

#                                 drawn_bounds = clicked_info["last_active_drawing"]["geometry"]["coordinates"][0]  # GeoJSON format

#                                 # Convert GeoJSON coordinates to Shapely polygon
#                                 drawn_polygon = Polygon(drawn_bounds)

#                                 # Load census tract GeoJSON
#                                 census_geojson = load_geojson(geojson_paths["tracts"])
#                                 tracts_gdf = gpd.GeoDataFrame.from_features(census_geojson["features"])
#                                 tracts_gdf.set_crs(epsg=4326, inplace=True)

#                                 # Intersect with tracts
#                                 intersecting_tracts = tracts_gdf[tracts_gdf.intersects(drawn_polygon)]

#                                 if not intersecting_tracts.empty:
#                                     st.success(f"{len(intersecting_tracts)} census tracts intersect with your rectangle.")
#                                     st.table(intersecting_tracts[["NAMELSAD"]].rename(columns={"NAMELSAD": "Selected Census Tracts"}).reset_index(drop=True))
#                                     selected_multiple_census_tracts = list(intersecting_tracts["NAMELSAD"])
#                                     print(intersecting_tracts["NAMELSAD"].values)

#                                     # -------- NEW: reset state if the rectangle selection changed --------
#                                     last = st.session_state.get("hpo_area_selected_tracts")
#                                     if last != selected_multiple_census_tracts:
#                                         st.session_state["hpo_area_selected_tracts"] = selected_multiple_census_tracts
#                                         st.session_state["all_tract_user_inputs"] = {}       # clear old tract inputs
#                                         st.session_state.pop("tract_input_selector", None)   # reset tract dropdown
#                                 else:
#                                     st.warning("No census tracts found inside the drawn area.")
#                                     selected_multiple_census_tracts = []

#                                 folium.GeoJson(
#                                 intersecting_tracts.__geo_interface__,
#                                 name='Intersecting Tracts',
#                                 style_function=lambda f: {'color': 'green', 'weight': 2},
#                                 tooltip=GeoJsonTooltip(fields=['NAMELSAD'], aliases=['Tract:'])
#                                 ).add_to(m) 

#                                 # ---------- BATCHED INPUTS FOR SELECTED TRACTS: fragment + form ----------
#                                 # NOTE: we reimplement multiple_input_section to render inside a FORM (container=st).


#                                 @st.fragment
#                                 def hpo_area_inputs_fragment(tract_names):
#                                     # IMPORTANT: Do NOT put `with st.sidebar:` here; call this fragment inside a with st.sidebar block.
#                                     if len(tract_names) == 0:
#                                         st.warning("Please select at least one census tract.")
#                                         return

#                                     # 1) Tract dropdown OUTSIDE the form so it reruns the fragment immediately on change
#                                     selected_input_tract = st.selectbox(
#                                         "Select a Census Tract to enter inputs:",
#                                         tract_names,
#                                         key="tract_input_selector"
#                                     )

#                                     # Parse an ID for keying sliders (keeps your display text as-is)
#                                     parts = str(selected_input_tract).split()
#                                     tract_id = parts[2] if len(parts) >= 3 else str(selected_input_tract)

#                                     # Ensure the accumulator exists (dict of dicts)
#                                     if "all_tract_user_inputs" not in st.session_state:
#                                         st.session_state.all_tract_user_inputs = {}

#                                     # If we already have values for this tract, use them as defaults
#                                     existing_for_this_tract = st.session_state.all_tract_user_inputs.get(selected_input_tract, {})

#                                     # 2) Sliders INSIDE the form; values are only sent on submit
#                                     with st.form("hpo_area_inputs_form", clear_on_submit=False):
#                                         st.markdown("## Enter Input Variables")

#                                         user_inputs = {}
#                                         user_inputs.update(multiple_input_section(
#                                             "Input Weather Variables",
#                                             classification_weather_keys,
#                                             tabnet_classification_range_config,
#                                             tract_id=tract_id,
#                                             labels=classification_weather_labels,
#                                             container=st,
#                                             existing=existing_for_this_tract
#                                         ))
#                                         user_inputs.update(multiple_input_section(
#                                             "Input Traffic Characteristics",
#                                             traffic_keys_classification,
#                                             tabnet_classification_range_config,
#                                             tract_id=tract_id,
#                                             labels=traffic_keys_classification_labels,
#                                             container=st,
#                                             existing=existing_for_this_tract
#                                         ))

#                                         submitted = st.form_submit_button(f"Submit Inputs for {selected_input_tract}")

#                                     if submitted:
#                                         # Merge/overwrite just this tract's dict; preserves previously submitted tracts
#                                         st.session_state.all_tract_user_inputs[selected_input_tract] = user_inputs

#                                         # Progress feedback
#                                         if len(st.session_state.all_tract_user_inputs) == len(tract_names):
#                                             st.success("All inputs have been provided for all the selected census tracts. You can now proceed with the prediction.")
#                                         else:
#                                             st.success(
#                                                 f"Inputs saved for {selected_input_tract}. "
#                                                 "Select another tract from the dropdown to submit its inputs."
#                                             )

#                                     # (Keep your debug prints)
#                                     print("Saved Inputs:", st.session_state.all_tract_user_inputs)
#                                     if len(st.session_state.all_tract_user_inputs) == len(tract_names):
#                                         print("User Inputs for Selected Census Tracts:\n", st.session_state.all_tract_user_inputs)

#                                 # Render the fragment INSIDE the sidebar (caller side sets the container)
#                                 with st.sidebar:
#                                     # -------- NEW: drive the fragment with the CURRENT rectangle's tracts only --------
#                                     current_tracts = st.session_state.get("hpo_area_selected_tracts", selected_multiple_census_tracts)
#                                     hpo_area_inputs_fragment(current_tracts)

#                                 if predict_crashes:
#                                     chosen_model = "CatBoost"
#                                     # -------- NEW: restrict predictions to CURRENT rectangle selection --------
#                                     current_tracts = st.session_state.get("hpo_area_selected_tracts", [])
#                                     all_user_inputs_for_selected_tracts = st.session_state.get("all_tract_user_inputs", {})

#                                     prediction_data = []

#                                     for tract_name in current_tracts:
#                                         user_inputs = all_user_inputs_for_selected_tracts.get(tract_name, {})
#                                         classification_inputs = {}

#                                         # Prepare model input
#                                         for key in classification_weather_keys + demographic_keys + traffic_keys_classification + ["avg_temp"]:
#                                             if key in user_inputs:
#                                                 classification_inputs[key] = user_inputs[key]
#                                             elif key == "avg_temp":
#                                                 classification_inputs[key] = (classification_inputs['min_temp'] + classification_inputs['max_temp']) / 2
#                                             elif key in demographic_keys:
#                                                 classification_inputs[key] = mean_values_demographic_variables_from_valid_dmvt.get(key, 0)
#                                             else:
#                                                 classification_inputs[key] = 0

#                                         # Convert booleans to strings
#                                         for k in ['is_weekend', 'is_holiday']:
#                                             classification_inputs[k] = str(classification_inputs[k])

#                                         # Prepare request payload
#                                         if chosen_model.strip() in models_mapping:
#                                             request_data = {
#                                                 "model_name": models_mapping[chosen_model],
#                                                 "inputs": classification_inputs
#                                             }
#                                             print("Inputs passed to the Model:", classification_inputs)
#                                             try:
#                                                 # API call
#                                                 if request_data["model_name"] == "catBoost_regression_pickled":
#                                                     response = requests.post("http://127.0.0.1:8000/predict_regression", json=request_data)
#                                                 else:
#                                                     response = requests.post("http://127.0.0.1:8000/predict_classification", json=request_data)

#                                                 # Store prediction result
#                                                 if response.status_code == 200:
#                                                     result = response.json()
#                                                     predicted_crashes = result['predicted_crashes']
#                                                 else:
#                                                     predicted_crashes = f"API Error {response.status_code}"

#                                             except Exception as e:
#                                                 predicted_crashes = f"Request Error: {e}"

#                                             prediction_data.append({
#                                                 "Census Tract": tract_name,
#                                                 "Predicted Crashes": predicted_crashes
#                                             })

#                                     # Convert to DataFrame and display
#                                     predictions_df = pd.DataFrame(prediction_data)
#                                     st.markdown("### Crash Predictions")
#                                     st.table(predictions_df.reset_index(drop=True))

#         # ================================= HPO: Map Visualization =================================
#         elif hpo_county_mode == "Map Visualization":
#             # ---------------- Sidebar inputs: fragment + form (no rerun while sliding) ----------------


#             @st.fragment
#             def hpo_mapviz_inputs_fragment():
#                 with st.form("hpo_mapviz_inputs_form", clear_on_submit=False):
#                     inputs = {}
#                     # Same inputs you had before, but rendered INSIDE the form
#                     inputs.update(input_section_v2(
#                         "Input Weather Variables",
#                         classification_weather_keys,
#                         tabnet_classification_range_config,
#                         classification_weather_labels,
#                         container=st,  # <- IMPORTANT: write to the form context
#                     ))
#                     inputs.update(input_section_v2(
#                         "Input Traffic Characteristics",
#                         traffic_keys_classification,
#                         tabnet_classification_range_config,
#                         traffic_keys_classification_labels,
#                         container=st,  # <- IMPORTANT
#                     ))
#                     submitted = st.form_submit_button("Submit Inputs")
#                 if submitted:
#                     st.session_state["hpo_mapviz"] = inputs
#                     st.success("Inputs submitted. Now click **Predict Crash Counts** below the map.")

#             # Render the fragment INSIDE the sidebar (required)
#             with st.sidebar:
#                 hpo_mapviz_inputs_fragment()

#             # ---------------- Map (kept out of fragment, so it doesn't rerender while sliding) ----------------
#             with st.spinner("Loading visualization... Please wait."):
#                 folium.GeoJson(
#                     cached_load_json(geojson_paths["kansas"]), name='Kansas Boundary',
#                     style_function=lambda f: {'fillOpacity': 0, 'color': 'black', 'weight': 3}
#                 ).add_to(m)

#                 folium.GeoJson(
#                     cached_load_json(geojson_paths["tracts"]), name='Census Tracts',
#                     style_function=lambda f: {'fillOpacity': 0, 'color': "#150202", 'weight': 0.7},
#                     highlight_function=lambda f: {'fillColor': 'brown', 'color': 'brown', 'weight': 3.5, 'dashArray': '12, 12'},
#                     tooltip=GeoJsonTooltip(fields=['NAMELSAD'], aliases=['Tract:'], localize=True)
#                 ).add_to(m)

#                 folium.GeoJson(
#                     cached_load_json(geojson_paths["roads"]), name='Road Network',
#                     style_function=lambda f: {'weight': 0.8},
#                     highlight_function=lambda f: {'color': 'blue', 'weight': 1.4, 'dashArray': '4, 4'},
#                     tooltip=GeoJsonTooltip(fields=['FULLNAME'], aliases=['Road Name:'], localize=True)
#                 ).add_to(m)

#                 folium.LayerControl().add_to(m)
#             with st.container():

#                 clicked_info = st_folium(m, width=700, height=500)
#                 st.markdown(
#                     """
#                     <style>
#                     iframe[title="folium_map"] { margin-bottom: -30px; }
#                     </style>
#                     """,
#                     unsafe_allow_html=True
#                 )
#                 st.markdown("")  # keep layout tight

#                 # Optional selection feedback
#                 if clicked_info and clicked_info.get("last_active_drawing"):
#                     tract_props = clicked_info["last_active_drawing"]["properties"]
#                     countyfp = tract_props.get("COUNTYFP", None)
#                     tract_name = tract_props.get("NAMELSAD", "Unknown")

#                     county_row = kansas_counties[kansas_counties["County Code"].astype(str).str.zfill(3) == str(countyfp).zfill(3)]
#                     if not county_row.empty:
#                         county_name = county_row.iloc[0]["County Name"]
#                         st.success(f"**Selected {tract_name}** is in **{county_name} County**")
#                     else:
#                         st.warning("County not found for the selected tract.")

#                 # ---------------- Predict button: use last submitted inputs only ----------------
#                 if st.button("Predict Crash Counts"):
#                     chosen_model = "CatBoost"  # fixed for HPO
#                     if "hpo_mapviz" not in st.session_state:
#                         st.warning("Please submit inputs first (use the **Submit Inputs** button in the sidebar).")
#                     else:
#                         ui_inputs = st.session_state["hpo_mapviz"]

#                         # Build payload once, from submitted values
#                         classification_inputs = {}
#                         for key in classification_weather_keys + demographic_keys + traffic_keys_classification + ["avg_temp"]:
#                             if key in ui_inputs:
#                                 classification_inputs[key] = ui_inputs[key]
#                             elif key == "avg_temp":
#                                 classification_inputs[key] = (ui_inputs['min_temp'] + ui_inputs['max_temp']) / 2
#                             elif key in demographic_keys:
#                                 # If you have your mean values dict available here:
#                                 classification_inputs[key] = mean_values_demographic_variables_from_valid_dmvt.get(key, 0)
#                             else:
#                                 classification_inputs[key] = 0

#                         for k in ['is_weekend', 'is_holiday']:
#                             if k in classification_inputs:
#                                 classification_inputs[k] = str(classification_inputs[k])

#                         request_data = {
#                             "model_name": models_mapping[chosen_model],
#                             "inputs": classification_inputs
#                         }

#                         try:
#                             url = "http://127.0.0.1:8000/predict_classification"
#                             response = requests.post(url, json=request_data, timeout=30)
#                             if response.status_code == 200:
#                                 result = response.json()
#                                 st.success(f"Predicted Crashes: {result.get('predicted_crashes')}")
#                             else:
#                                 st.error(f"API Error: {response.status_code} - {response.text}")
#                         except Exception as e:
#                             st.error(f"Request Error: {e}")






#     # ================================= Researcher =================================
#     elif input_role == 'Researcher(Deep Dive)':
#         with st.sidebar:
#             st.header("Model Selection")
#             chosen_model = st.selectbox(
#                 "Choose the ML Alg to predict the crash count",
#                 options=['Random Forest', 'AdaBoost', 'Gradient Boost', 'XGBoost', 'LightGBM', 'CatBoost', 'CatBoost Regression', 'TabNet'],
#                 key="researcher_model_choice",
#             )


#         @st.fragment
#         def researcher_inputs_fragment():
#             with st.form("researcher_inputs_form", clear_on_submit=False):
#                 inputs = {}
#                 if chosen_model == "CatBoost Regression":
#                     inputs.update(input_section_v2("Input Weather Variables", weather_keys, range_config, weather_labels, container=st))
#                     inputs.update(input_section_v2("Input Demographic Variables", demographic_keys, range_config, demographic_labels, container=st))
#                     inputs.update(input_section_v2("Input Traffic Characteristics", traffic_keys_regression, range_config, traffic_regression_labels, container=st))
#                 else:
#                     inputs.update(input_section_v2("Input Weather Variables", classification_weather_keys, tabnet_classification_range_config, classification_weather_labels, container=st))
#                     inputs.update(input_section_v2("Input Demographic Variables", demographic_keys, tabnet_classification_range_config, demographic_labels, container=st))
#                     inputs.update(input_section_v2("Input Traffic Characteristics", traffic_keys_classification, tabnet_classification_range_config, traffic_keys_classification_labels, container=st))
#                 submitted = st.form_submit_button("Submit Inputs")
#             if submitted:
#                 st.session_state["researcher_inputs"] = inputs
#                 st.success("Inputs submitted. Now click **Predict Crash Counts** below the map.")

#         with st.sidebar:
#             researcher_inputs_fragment()

#         with st.spinner("Loading visualization... Please wait."):
#             # Map for Researcher
#             folium.GeoJson(cached_load_json(geojson_paths["kansas"]), name='Kansas Boundary',
#                         style_function=lambda f: {'fillOpacity': 0, 'color': 'black', 'weight': 3}).add_to(m)
#             folium.GeoJson(cached_load_json(geojson_paths["tracts"]), name='Census Tracts',
#                         style_function=lambda f: {'fillOpacity': 0, 'color': "#150202", 'weight': 0.7},
#                         highlight_function=lambda f: {'fillColor': 'brown', 'color': 'brown', 'weight': 3.5, 'dashArray': '12, 12'},
#                         tooltip=GeoJsonTooltip(fields=['NAMELSAD'], aliases=['Tract:'], localize=True)).add_to(m)
#             folium.GeoJson(cached_load_json(geojson_paths["roads"]), name='Road Network',
#                         style_function=lambda f: {'weight': 0.8},
#                         highlight_function=lambda f: {'color': 'blue', 'weight': 1.4, 'dashArray': '4, 4'},
#                         tooltip=GeoJsonTooltip(fields=['FULLNAME'], aliases=['Road Name:'], localize=True)).add_to(m)
#         st.markdown("<style>iframe[title='folium_map']{margin-bottom:-30px;}</style>", unsafe_allow_html=True)

#         # Default state for selected tract
#         if "selected_tract_id" not in st.session_state:
#             st.session_state.selected_tract_id = None
#         with st.container():
#             clicked_info = st_folium(m, width=700, height=600)


#             if clicked_info and clicked_info.get("last_active_drawing"):
#                         tract_props = clicked_info["last_active_drawing"]["properties"]
#                         countyfp = tract_props.get("COUNTYFP", None)
#                         tract_name = tract_props.get("NAMELSAD", "Unknown")

#                         # Store tract selection in session_state
#                         st.session_state.selected_tract_id = tract_name
        
#                         county_row = kansas_counties[kansas_counties["County Code"].astype(str).str.zfill(3) == str(countyfp).zfill(3)]
#                         if not county_row.empty:
#                             county_name = county_row.iloc[0]["County Name"]
#                             st.success(f"**Selected {tract_name}** is in **{county_name} County**")
#                         else:
#                             st.warning("County not found for the selected tract.")

#             if st.button("Predict Crash Counts", disabled=st.session_state.selected_tract_id is None):
#                 if "researcher_inputs" not in st.session_state:
#                     st.warning("Please submit inputs first.")
#                 else:
#                     ui_inputs = st.session_state["researcher_inputs"]
#                     if chosen_model == "CatBoost Regression":
#                         payload = {}
#                         for key in weather_keys + demographic_keys + traffic_keys_regression + ["avg_temp"]:
#                             if key in ui_inputs:
#                                 payload[key] = ui_inputs[key]
#                             elif key == "avg_temp":
#                                 payload[key] = (ui_inputs['min_temp'] + ui_inputs['max_temp']) / 2
#                             else:
#                                 payload[key] = 0
#                         for k in ['is_weekend', 'is_holiday']:
#                             if k in payload:
#                                 payload[k] = str(payload[k])
#                     else:
#                         payload = {}
#                         for key in classification_weather_keys + demographic_keys + traffic_keys_classification + ["avg_temp"]:
#                             if key in ui_inputs:
#                                 payload[key] = ui_inputs[key]
#                             elif key == "avg_temp":
#                                 payload[key] = (ui_inputs['min_temp'] + ui_inputs['max_temp']) / 2
#                             else:
#                                 payload[key] = 0
#                         for k in ['is_weekend', 'is_holiday']:
#                             if k in payload:
#                                 payload[k] = str(payload[k])

#                     request_data = {"model_name": models_mapping[chosen_model], "inputs": payload}
#                     url = ("http://127.0.0.1:8000/predict_regression"
#                         if request_data["model_name"] == "catBoost_regression_pickled"
#                         else "http://127.0.0.1:8000/predict_classification")
#                     try:
#                         r = requests.post(url, json=request_data, timeout=30)
#                         if r.status_code == 200:
#                             result = r.json()
#                             pred = result.get("predicted_crashes", result.get("predicted_crash_count"))
#                             st.success(f"Predicted Crashes: {pred}")
#                         else:
#                             st.error(f"API Error: {r.status_code} - {r.text}")
#                     except Exception as e:
#                         st.error(f"Request Error: {e}")

#     # -------------------- Reset Session --------------------
#     with st.sidebar:
#         if st.button("Reset Session"):
#             st.session_state.show_home_modal = True
#             st.rerun()








import streamlit as st
import geopandas as gpd
import pandas as pd
from streamlit_folium import st_folium
import folium
import json
import os
from folium.features import GeoJsonTooltip
from shapely.geometry import Polygon
from utils import *
from folium.plugins import Draw
import requests
from streamlit.components.v1 import html
from pathlib import Path















# Check session state
if "show_home_modal" not in st.session_state:
    st.session_state.show_home_modal = True

# If modal should be shown
if st.session_state.show_home_modal:
    with st.container():
        st.markdown("## 👋 Welcome to Crash Prediction App")
        st.markdown("This app allows you to **Predict crash counts using ML models**")

        # Disclaimer summary
        st.markdown(r"""**Disclaimer:**  
        The models behind this tool were trained on Kansas crash, weather, traffic, and demographic data from **2012–2016**, validated on **2017**, and tested on **2018–2019**. Using inputs from other geographical areas or years after 2019 may degrade performance and produce biased or unreliable results. By using this tool, you agree to the Terms of Usage below.
        """)

        # Terms of Usage with agreement checkbox
        with st.expander("Terms of Usage"):
            with open("C:/censustract/ui/terms_of_usage.md", "r", encoding="utf-8") as f:
                st.markdown(f.read())

            agree = st.checkbox("I have read and agree to the Terms of Usage.", key="agree_terms")

        # Link to paper
        st.markdown("""
        **For methods and limitations**, see the paper:  
        *Comparative Geospatial Analysis of Weather-Related Impacts on Crash Frequency with Explainable Machine Learning: A Case for Kansas Census Tracts* (Working Paper)
        """)

        # Show Continue button only after agreement
        if st.session_state.get("agree_terms", False):
            if st.button("Continue to App"):
                st.session_state.show_home_modal = False
                st.rerun()
        else:
            st.info("Please review and agree to the Terms of Usage to continue.")
else:
        
    ST_MAP_CENTER = [38.4987789, -98.3200779]

    st.header("Census Tract Application")

    with st.sidebar:

        role_options = ["Select a Role", "Highway Patrol Officer", "Researcher(Deep Dive)"]
        input_role = st.selectbox("Choose your Role", options=role_options, index=0)

        if input_role == "Select a Role":
            st.warning("Please select a role to proceed.")
            st.stop()

    models_mapping = {
                        "AdaBoost": 'AdaBoostClassifier_aggregate_model',
                        "CatBoost": 'CatBoostClassifier_aggregate_model',
                        "CatBoost Regression": 'catBoost_regression_pickled',
                        "Gradient Boost": 'GradientBoostingClassifier_aggregate_model',
                        "LightGBM": 'LGBMClassifier_aggregate_model',
                        "Random Forest": 'RandomForestClassifier_aggregate_model',
                        "TabNet": 'TabNetClassifier_aggregate_model',
                        "XGBoost": 'XGBClassifier_aggregate_model'
                    }


    m = folium.Map(location=ST_MAP_CENTER, zoom_start=7)

    # static_prediction_df = pd.read_csv(r"ui\data\static_crashes_week1.csv")


    # Base project directory (automatically detects the folder of this script)
    BASE_DIR = Path(__file__).resolve().parent.parent   # adjust .parent as needed

    # Config paths
    config_dir = BASE_DIR / "ui" / "configs"
    data_dir   = BASE_DIR / "data"

    # Load configs
    with open(config_dir / "range_config.json", "r") as f:
        range_config = json.load(f)

    with open(config_dir / "tabnet_classifcation_range_config.json", "r") as f:
        tabnet_classification_range_config = json.load(f)

    # Paths
    geojson_paths = {
        "kansas": data_dir / "kansas.geojson",
        "counties_base": data_dir / "ks_county_files",
        "county_info": data_dir / "FRPP_GLC__United_States_April_8_2024.csv",
        "tracts": data_dir / "Tiger_2020_Boundaries" / "Tiger_2020_Boundaries.geojson",
        "roads": data_dir / "tl_2024_20_prisecroads" / "tl_2024_20_prisecroads_geojson" / "tl_2024_20_prisecroads.geojson",
        # "valid_dmvt": data_dir / "all_dataset_dmvt.csv",
        # "static_crashes": data_dir / "static_crashes_week1.csv",
    }

    
    # with open(geojson_paths["tracts"], "r") as f:
    #     data = json.load(f)

    # print(data["features"][0].keys())                # should include 'properties'
    # print(data["features"][0]["properties"].keys())  # list of available fields




    user_inputs = {}

    county_names_df = cached_read_csv(geojson_paths["county_info"], encoding='ISO-8859-1')
    kansas_counties = county_names_df[county_names_df['State Name'] == 'KANSAS']    

    if input_role=='Highway Patrol Officer':
        
        chosen_model="CatBoost" # considered this as the best model

        # HP Officer selecting a county
        # county_names_df = cached_read_csv(geojson_paths["county_info"], encoding='ISO-8859-1')
        # kansas_counties = county_names_df[county_names_df['State Name'] == 'KANSAS']
        # valid_dmvt_df = cached_read_csv(geojson_paths["valid_dmvt"], encoding='ISO-8859-1')

        # st.write(kansas_counties.head())

        with st.sidebar:
            county_list = sorted(set(kansas_counties['County Name'].astype(str).str.capitalize()))
            county_list.insert(0, "Select a County")  # Insert placeholder at the top

            hpo_county_mode=st.selectbox("Choose how you'd like to select a County", ["Select County Selection Mode","List Selection", "Map Visualization"],index=0)

            if hpo_county_mode=="Select County Selection Mode":
                st.warning("Please select a County Selection Mode to proceed")
                st.stop()

        mean_values_demographic_variables_from_valid_dmvt={"totPop":3534.0, "povper":13.0, "hhnov":70.0, "pctnvh":6.0, "avgcmm":20.0, 
                                                           "trnfrq":2.0, "jb45dr":30864.0, "drvpoi":15.0, 'wlkpoi':227.0,}

        # ================================= Highway Patrol Officer HPO: List Selection =================================
        if hpo_county_mode=="List Selection":

                with st.sidebar:
                    hpo_selected_county = st.selectbox(
                        "Choose a County",
                        options=county_list,
                        index=0  # This ensures the placeholder is selected by default
                    )
                    # Prevent execution if a valid county hasn't been selected
                    if hpo_selected_county == "Select a County":
                        st.warning("Please select a county to view the map.")
                        st.stop()

                    
                    # Selection for how many census tracts to choose
                    tract_mode = st.selectbox(
                        "Choose you Area Selection Style",
                        options=["Choose you Area Selection Style","Single Census Tract", "Choose a road (select area on map)"]
                    )

                    if tract_mode == "Choose you Area Selection Style":
                        st.warning("Please select how many census tract you want to select, to view the map.")
                        st.stop()

                    # Show warning popup if "Multiple Area Selection" is selected
                    if tract_mode == "Choose a road (select area on map)":
                        st.warning("If you select multiple census tracts, you must input variables for each selected census tract.")




                # ================================= HPO: List Selection :: Single Census Tract =================================
                if tract_mode == "Single Census Tract":

                    # --------- Sidebar inputs: fragment + form (no rerun while sliding) ---------
                    @st.fragment
                    def hpo_single_inputs_fragment():
                        with st.form("hpo_single_inputs_form", clear_on_submit=False):
                            inputs = {}
                            # Same inputs as before, but rendered INSIDE the form so they don't rerun on slide
                            inputs.update(input_section_v2(
                                "Input Weather Variables",
                                classification_weather_keys,
                                tabnet_classification_range_config,
                                classification_weather_labels,
                                container=st,
                            ))
                            inputs.update(input_section_v2(
                                "Input Traffic Characteristics",
                                traffic_keys_classification,
                                tabnet_classification_range_config,
                                traffic_keys_classification_labels,
                                container=st,
                            ))
                            submitted = st.form_submit_button("Submit Inputs")
                        if submitted:
                            st.session_state["hpo_single"] = inputs
                            st.success("Inputs submitted. Now click **Predict Crash Counts** below the map.")

                    # Render the fragment INSIDE the sidebar (required by Streamlit)
                    with st.sidebar:
                        hpo_single_inputs_fragment()

                    # --------- Map & Data (kept outside fragment so they don't rerender while sliding) ---------
                    # Base boundary
                    folium.GeoJson(
                        cached_load_json(geojson_paths["kansas"]), name='Kansas Boundary',
                        style_function=lambda f: {'fillOpacity': 0, 'color': 'black', 'weight': 3}
                    ).add_to(m)

                    # --------- COUNTY HANDLING (replaced CSV + combine_geojsons with full_geojson_data.geojson) ---------
                    with open(data_dir / "full_geojson_data.geojson", "r", encoding="utf-8") as f:
                        counties_geojson = json.load(f)

                    # Draw all county outlines
                    folium.GeoJson(
                        counties_geojson, name="County Boundaries",
                        style_function=lambda f: {'fillOpacity': 0, 'color': 'black', 'weight': 1},
                        tooltip=GeoJsonTooltip(fields=['name'], aliases=['County:'], localize=True)
                    ).add_to(m)

                    # Normalize helper
                    def _norm(s: str) -> str:
                        return str(s).strip().casefold()

                    # Selected county highlight + fit (match on 'name' exactly, no " COUNTY" suffix)
                    selected_feature = next(
                        (
                            feat for feat in counties_geojson.get("features", [])
                            if _norm(feat.get("properties", {}).get("name", "")) == _norm(hpo_selected_county)
                        ),
                        None
                    )
                    

                    if selected_feature:
                        selected_geojson = {"type": "FeatureCollection", "features": [selected_feature]}
                        bounds = get_bounds(selected_geojson['features'])
                        m.fit_bounds(bounds)

                        folium.GeoJson(
                            selected_geojson, name="Selected County",
                            style_function=lambda f: {'fillColor': 'gold','fillOpacity': 0.25,},
                            highlight_function=lambda f: {'fillColor': '#0077FF','fillOpacity': 0.15, 'color': "gold", 'weight': 3.5},
                            tooltip=GeoJsonTooltip(fields=['name'], aliases=['County:'], localize=True)
                        ).add_to(m)

                        county_name = selected_feature["properties"].get("name", hpo_selected_county)
                        st.subheader(f"You are viewing '{county_name}' County")
                    # else:
                    #     print("Did not enter the if block")
                    # # else:
                    # #     st.warning("Selected county not found.")
                    # #     st.stop()

                    # --------- Tracts & Roads (unchanged) ---------
                    with st.spinner("Loading visualization... Please wait."):
                        folium.GeoJson(
                            cached_load_json(geojson_paths["tracts"]), name='Census Tracts',
                            style_function=lambda f: {'fillOpacity': 0, 'color': "#150202", 'weight': 0.7},
                            highlight_function=lambda f: {'fillColor': 'brown', 'color': 'brown',
                                                        'weight': 3.5, 'dashArray': '12, 12'},
                            tooltip=GeoJsonTooltip(fields=['NAMELSAD'], aliases=['Tract:'], localize=True)
                        ).add_to(m)

                        folium.GeoJson(
                            cached_load_json(geojson_paths["roads"]), name='Road Network',
                            style_function=lambda f: {'weight': 1.5},
                            highlight_function=lambda f: {'color': 'blue', 'weight': 2.5, 'dashArray': '4, 4'},
                            tooltip=GeoJsonTooltip(fields=['FULLNAME'], aliases=['Road Name:'], localize=True)
                        ).add_to(m)

                    # Display the map
                    with st.container():
                        clicked_info = st_folium(m, width=700, height=600)
                        st.markdown(
                            """
                            <style>
                            iframe[title="folium_map"] { margin-bottom: -30px; }
                            </style>
                            """,
                            unsafe_allow_html=True
                        )

                        if clicked_info and clicked_info.get("last_active_drawing"):
                            tract_props = clicked_info["last_active_drawing"]["properties"]
                            countyfp = tract_props.get("COUNTYFP", None)
                            tract_name = tract_props.get("NAMELSAD", "Unknown")
                            tract_id = tract_props.get("NAME", None)

                            county_row = kansas_counties[
                                kansas_counties["County Code"].astype(str).str.zfill(3) == str(countyfp).zfill(3)
                            ]
                            if not county_row.empty:
                                _county_name = county_row.iloc[0]["County Name"]
                                st.success(f"**Selected {tract_name}** is in **{_county_name} County**")
                            else:
                                st.warning("County not found for the selected tract.")

                        # --------- Predict ---------
                        predict_crashes = st.button("Predict Crash Counts")
                        if predict_crashes:
                            chosen_model = "CatBoost"  # fixed for HPO Single-Tract path
                            if "hpo_single" not in st.session_state:
                                st.warning("Please submit inputs first (use the **Submit Inputs** button in the sidebar).")
                                st.stop()

                            ui_inputs = st.session_state["hpo_single"]

                            classification_inputs = {}
                            for key in classification_weather_keys + demographic_keys + traffic_keys_classification + ["avg_temp"]:
                                if key in ui_inputs:
                                    classification_inputs[key] = ui_inputs[key]
                                elif key == "avg_temp":
                                    classification_inputs[key] = (ui_inputs['min_temp'] + ui_inputs['max_temp']) / 2
                                elif key in demographic_keys:
                                    classification_inputs[key] = mean_values_demographic_variables_from_valid_dmvt.get(key, 0)
                                else:
                                    classification_inputs[key] = 0

                            for k in ['is_weekend', 'is_holiday']:
                                if k in classification_inputs:
                                    classification_inputs[k] = str(classification_inputs[k])

                            if chosen_model.strip() in models_mapping:
                                request_data = {
                                    "model_name": models_mapping[chosen_model],
                                    "inputs": classification_inputs
                                }
                            else:
                                st.error("Unknown model selection.")
                                st.stop()

                            try:
                                response = requests.post(
                                    "http://127.0.0.1:8000/predict_classification",
                                    json=request_data,
                                    timeout=30
                                )
                                if response.status_code == 200:
                                    result = response.json()
                                    st.success(f"Predicted Crashes: {result.get('predicted_crashes')}")
                                else:
                                    st.error(f"API Error: {response.status_code} - {response.text}")
                            except Exception as e:
                                st.error(f"Request Error: {e}")









                # # ================================= HPO: List Selection :: Single Census Tract =================================
                # if tract_mode == "Single Census Tract":

                #     # --------- Sidebar inputs: fragment + form (no rerun while sliding) ---------
                #     @st.fragment
                #     def hpo_single_inputs_fragment():
                #         with st.form("hpo_single_inputs_form", clear_on_submit=False):
                #             inputs = {}
                #             # Same inputs as before, but rendered INSIDE the form so they don't rerun on slide
                #             inputs.update(input_section_v2(
                #                 "Input Weather Variables",
                #                 classification_weather_keys,
                #                 tabnet_classification_range_config,
                #                 classification_weather_labels,
                #                 container=st,   # IMPORTANT: write into the form context
                #             ))
                #             inputs.update(input_section_v2(
                #                 "Input Traffic Characteristics",
                #                 traffic_keys_classification,
                #                 tabnet_classification_range_config,
                #                 traffic_keys_classification_labels,
                #                 container=st,   # IMPORTANT
                #             ))
                #             submitted = st.form_submit_button("Submit Inputs")
                #         if submitted:
                #             st.session_state["hpo_single"] = inputs
                #             st.success("Inputs submitted. Now click **Predict Crash Counts** below the map.")


                #     # Render the fragment INSIDE the sidebar (required by Streamlit)
                #     with st.sidebar:
                #         hpo_single_inputs_fragment()

                #     # --------- Map & Data (kept outside fragment so they don't rerender while sliding) ---------
                #     # Base boundary
                #     folium.GeoJson(
                #         cached_load_json(geojson_paths["kansas"]), name='Kansas Boundary',
                #         style_function=lambda f: {'fillOpacity': 0, 'color': 'black', 'weight': 3}
                #     ).add_to(m)

                #     # Counties frame (reloaded via cache)
                #     county_names_df = cached_read_csv(geojson_paths["county_info"], encoding='ISO-8859-1')
                #     kansas_counties = county_names_df[county_names_df['State Name'] == 'KANSAS']

                #     # All counties outlines
                #     folium.GeoJson(
                #         combine_geojsons(kansas_counties), name="County Boundaries",
                #         style_function=lambda f: {'fillOpacity': 0, 'color': 'black', 'weight': 1},
                #         tooltip=GeoJsonTooltip(fields=['name'], aliases=['County:'], localize=True)
                #     ).add_to(m)








                #     geojson_data = combine_geojsons(kansas_counties)
                #     print("County's GeoJsons")
                #     # Top-level keys
                #     print(geojson_data.keys())

                #     # Inspect the first feature
                #     first_feature = geojson_data["type"]
                #     print(geojson_data)             # usually ['type', 'properties', 'geometry']
                #     # print(first_feature["properties"].keys())  # all available attributes for tooltips












                #     # Selected county highlight + fit
                #     selected_row = kansas_counties[kansas_counties["County Name"].str.capitalize() == hpo_selected_county]
                #     if not selected_row.empty:
                #         selected_geojson = combine_geojsons(selected_row)
                #         bounds = get_bounds(selected_geojson['features'])
                #         m.fit_bounds(bounds)

                #         folium.GeoJson(
                #             selected_geojson, name="Selected County",
                #             # style_function=lambda f: {'fillOpacity': 0, 'color': "#0077FF", 'weight': 3.5},
                #             style_function=lambda f: {'fillColor': 'gold','fillOpacity': 0.025},
                #             highlight_function=lambda f: {'fillColor': '#0077FF','fillOpacity': 0.15, 'color': "gold", 'weight': 3.5},
                #             tooltip=GeoJsonTooltip(fields=['name'], aliases=['County:'], localize=True)
                #         ).add_to(m)

                #         county_name = str(selected_row.iloc[0]["County Name"])
                #         st.subheader(f"You are viewing '{county_name.capitalize()}' County")
                #     else:
                #         st.warning("Selected county not found.")
                #         st.stop()

                #     with st.spinner("Loading visualization... Please wait."):
                #         # Tracts & Roads
                #         folium.GeoJson(
                #             cached_load_json(geojson_paths["tracts"]), name='Census Tracts',
                #             style_function=lambda f: {'fillOpacity': 0, 'color': "#150202", 'weight': 0.7},
                #             highlight_function=lambda f: {'fillColor': 'brown', 'color': 'brown', 'weight': 3.5, 'dashArray': '12, 12'},
                #             tooltip=GeoJsonTooltip(fields=['NAMELSAD'], aliases=['Tract:'], localize=True)
                #         ).add_to(m)

                #         folium.GeoJson(
                #             cached_load_json(geojson_paths["roads"]), name='Road Network',
                #             style_function=lambda f: {'weight': 1.5},
                #             highlight_function=lambda f: {'color': 'blue', 'weight': 2.5, 'dashArray': '4, 4'},
                #             tooltip=GeoJsonTooltip(fields=['FULLNAME'], aliases=['Road Name:'], localize=True)
                #         ).add_to(m)

                #     # Display the map
                #     with st.container():

                #         clicked_info = st_folium(m, width=700, height=600)
                #         st.markdown(
                #             """
                #             <style>
                #             iframe[title="folium_map"] { margin-bottom: -30px; }
                #             </style>
                #             """,
                #             unsafe_allow_html=True
                #         )
                #         # st.markdown("")  # optional spacing

                #         # Show which tract user interacted with
                #         if clicked_info and clicked_info.get("last_active_drawing"):
                #             tract_props = clicked_info["last_active_drawing"]["properties"]
                #             countyfp = tract_props.get("COUNTYFP", None)
                #             tract_name = tract_props.get("NAMELSAD", "Unknown")
                #             tract_id= tract_props.get("NAME", None)


                #             ## This code is to get the mean values of demographic variables for the selected census tract from valid dmvt data, but some tract ids are not present in all_dataset_dmvt.csv, 
                #             ## so that's why went with customized mean values for demographic variables from valid dmvt data

                #             # selected_tract_rows_df = valid_dmvt_df[valid_dmvt_df['CENSUS_TRACT']==tract_id] #filtering rows based on census tract id from Valid DMVT data
                #             # grouped = selected_tract_rows_df.groupby(['CENSUS_TRACT'])[["totPop", "povper", "hhnov", "pctnvh", "avgcmm", "trnfrq", "jb45dr", "drvpoi", 'wlkpoi']].mean()
                #             # # Getting the mean values of demographic variables for the selected census tract from valid dmvt data
                #             # mean_data_for_demographic_variables = {
                #             #             col.lower(): float(val)   
                #             #             for col, val in grouped.iloc[0].items()
                #             #         }


                #             county_row = kansas_counties[
                #                 kansas_counties["County Code"].astype(str).str.zfill(3) == str(countyfp).zfill(3)
                #             ]
                #             if not county_row.empty:
                #                 _county_name = county_row.iloc[0]["County Name"]
                #                 st.success(f"**Selected {tract_name}** is in **{_county_name} County**")
                #             else:
                #                 st.warning("County not found for the selected tract.")

                #         # --------- Predict (uses last submitted inputs from session_state) ---------
                #         predict_crashes = st.button("Predict Crash Counts")
                #         if predict_crashes:
                #             chosen_model = "CatBoost"  # fixed for HPO Single-Tract path

                #             if "hpo_single" not in st.session_state:
                #                 st.warning("Please submit inputs first (use the **Submit Inputs** button in the sidebar).")
                #                 st.stop()

                #             ui_inputs = st.session_state["hpo_single"]

                #             # Prepare inputs for Classification model (with avg_temp + demographic defaults)
                #             classification_inputs = {}
                #             for key in classification_weather_keys + demographic_keys + traffic_keys_classification + ["avg_temp"]:
                #                 if key in ui_inputs:
                #                     classification_inputs[key] = ui_inputs[key]
                #                 elif key == "avg_temp":
                #                     classification_inputs[key] = (ui_inputs['min_temp'] + ui_inputs['max_temp']) / 2
                #                 elif key in demographic_keys:
                #                     classification_inputs[key] = mean_values_demographic_variables_from_valid_dmvt.get(key, 0) #mean_data_for_demographic_variables.get(key,0)  # 
                #                 else:
                #                     classification_inputs[key] = 0  # Default if not provided

                #             # Convert booleans to strings for API compatibility
                #             for k in ['is_weekend', 'is_holiday']:
                #                 if k in classification_inputs:
                #                     classification_inputs[k] = str(classification_inputs[k])

                #             if chosen_model.strip() in models_mapping:
                #                 request_data = {
                #                     "model_name": models_mapping[chosen_model],
                #                     "inputs": classification_inputs
                #                 }
                #             else:
                #                 st.error("Unknown model selection.")
                #                 st.stop()

                #             # Call API (classification for Random Forest)
                #             try:
                #                 response = requests.post(
                #                     "http://127.0.0.1:8000/predict_classification",
                #                     json=request_data,
                #                     timeout=30
                #                 )
                #                 if response.status_code == 200:
                #                     result = response.json()
                #                     st.success(f"Predicted Crashes: {result.get('predicted_crashes')}")
                #                 else:
                #                     st.error(f"API Error: {response.status_code} - {response.text}")
                #             except Exception as e:
                #                 st.error(f"Request Error: {e}")












                # # ================================= HPO: List Selection :: Choose a road (select area on map) =================================
                # elif tract_mode == "Choose a road (select area on map)":

                #     selected_row = kansas_counties[kansas_counties["County Name"].str.capitalize() == hpo_selected_county]
                #     county_fp = str(selected_row.iloc[0]["County Code"]).zfill(3)
                #     county_name = str(selected_row.iloc[0]["County Name"]).zfill(3)

                #     st.subheader(f"You are viewing '{county_name.capitalize()}' County")

                #     # Add ALL Kansas counties (background layer)
                #     all_counties_geojson = combine_geojsons(kansas_counties)

                #     with st.spinner("Loading visualization... Please wait."):
                #         folium.GeoJson(
                #             all_counties_geojson,
                #             name="All County Boundaries",
                #             style_function=lambda f: {'fillOpacity': 0, 'color': 'gray', 'weight': 1},
                #             tooltip=GeoJsonTooltip(fields=['name'], aliases=['County:'], localize=True)
                #         ).add_to(m)

                #         folium.GeoJson(cached_load_json(geojson_paths["tracts"]), name='All Census Tracts',
                #             style_function=lambda f: {'fillOpacity': 0, 'color': "#150202", 'weight': 0.7},
                #             highlight_function=lambda f: {'fillColor': 'brown', 'color': 'brown', 'weight': 3.5},
                #             tooltip=GeoJsonTooltip(fields=['NAMELSAD'], aliases=['Tract:'], localize=True)).add_to(m)

                #     if not selected_row.empty:
                #         selected_geojson = combine_geojsons(selected_row)
                #         with st.spinner("Loading visualization... Please wait."):
                #             folium.GeoJson(
                #                 selected_geojson,
                #                 name="Selected County",
                #                 style_function=lambda f: {'fillColor': 'gold','fillOpacity': 0.025},
                #                 highlight_function=lambda f: {'fillColor': '#0077FF','fillOpacity': 0.15, 'color': "gold", 'weight': 3.5},
                #                 tooltip=GeoJsonTooltip(fields=['name'], aliases=['County:'], localize=True)
                #             ).add_to(m)

                #     bounds = get_bounds(selected_geojson['features'])
                #     m.fit_bounds(bounds)

                #     census_geojson = load_geojson(geojson_paths["tracts"])
                #     tracts_filtered = {
                #         "type": "FeatureCollection",
                #         "features": [feat for feat in census_geojson["features"]
                #                     if feat["properties"].get("COUNTYFP") == county_fp]
                #     }

                #     with st.spinner("Loading visualization... Please wait."):
                #         # HPO Selected County's  Census Tracts Visualization
                #         folium.GeoJson(
                #             tracts_filtered,
                #             name='Census Tracts',
                #             style_function=lambda f: {'fillOpacity': 0, 'color': "#150202", 'weight': 0.7},
                #             highlight_function=lambda f: {'fillColor': 'brown', 'color': 'brown', 'weight': 3.5, 'dashArray': '12, 12'},
                #             tooltip=GeoJsonTooltip(fields=['NAMELSAD'], aliases=['Tract:'], localize=True)
                #         ).add_to(m)

                #         # HPO Selected County's  Roads Visualization
                #         folium.GeoJson(cached_load_json(geojson_paths["roads"]), name='Road Network',
                #             style_function=lambda f: {'weight': 0.8},
                #             highlight_function=lambda f: {'color': 'blue', 'weight': 1.4, 'dashArray': '4, 4'},
                #             tooltip=GeoJsonTooltip(fields=['FULLNAME'], aliases=['Road Name:'], localize=True)).add_to(m)
                        







                # ================================= HPO: List Selection :: Choose a road (select area on map) =================================
                elif tract_mode == "Choose a road (select area on map)":

                    # --------- COUNTY HANDLING (use full_geojson_data.geojson instead of CSV + combine_geojsons) ---------
                    with open(data_dir / "full_geojson_data.geojson", "r", encoding="utf-8") as f:
                        counties_geojson = json.load(f)

                    # Normalize helper
                    def _norm(s: str) -> str:
                        return str(s).strip().casefold()

                    # Find the selected county feature
                    selected_feature = next(
                        (
                            feat for feat in counties_geojson.get("features", [])
                            if _norm(feat.get("properties", {}).get("name", "")) == _norm(hpo_selected_county)
                        ),
                        None
                    )

                    if selected_feature:
                        county_name = selected_feature["properties"].get("name", hpo_selected_county)
                        county_fp = selected_feature["properties"].get("COUNTYFP", "")

                        st.subheader(f"You are viewing '{county_name}' County")

                        with st.spinner("Loading visualization... Please wait."):
                            # All county outlines (background layer)
                            folium.GeoJson(
                                counties_geojson,
                                name="All County Boundaries",
                                style_function=lambda f: {'fillOpacity': 0, 'color': 'gray', 'weight': 1},
                                tooltip=GeoJsonTooltip(fields=['name'], aliases=['County:'], localize=True)
                            ).add_to(m)

                            # All census tracts layer (background)
                            folium.GeoJson(
                                cached_load_json(geojson_paths["tracts"]), name='All Census Tracts',
                                style_function=lambda f: {'fillOpacity': 0, 'color': "#150202", 'weight': 0.7},
                                highlight_function=lambda f: {'fillColor': 'brown', 'color': 'brown', 'weight': 3.5},
                                tooltip=GeoJsonTooltip(fields=['NAME'], aliases=['Tract:'], localize=True)
                            ).add_to(m)

                        # Highlight selected county
                        selected_geojson = {"type": "FeatureCollection", "features": [selected_feature]}
                        with st.spinner("Loading visualization... Please wait."):
                            folium.GeoJson(
                                selected_geojson,
                                name="Selected County",
                                style_function=lambda f: {'fillColor': 'gold', 'fillOpacity': 0.025},
                                highlight_function=lambda f: {'fillColor': '#0077FF','fillOpacity': 0.15, 'color': "gold", 'weight': 3.5},
                                tooltip=GeoJsonTooltip(fields=['name'], aliases=['County:'], localize=True)
                            ).add_to(m)

                        # Zoom to selected county bounds
                        bounds = get_bounds(selected_geojson['features'])
                        m.fit_bounds(bounds)

                        # Filter census tracts belonging to the selected county
                        census_geojson = load_geojson(geojson_paths["tracts"])
                        tracts_filtered = {
                            "type": "FeatureCollection",
                            "features": [
                                feat for feat in census_geojson["features"]
                                if feat["properties"].get("COUNTYFP") == county_fp
                            ]
                        }

                        with st.spinner("Loading visualization... Please wait."):
                            # HPO Selected County's Census Tracts Visualization
                            folium.GeoJson(
                                tracts_filtered,
                                name='Census Tracts',
                                style_function=lambda f: {'fillOpacity': 0, 'color': "#150202", 'weight': 0.7},
                                highlight_function=lambda f: {'fillColor': 'brown', 'color': 'brown', 'weight': 3.5, 'dashArray': '12, 12'},
                                tooltip=GeoJsonTooltip(fields=['NAMELSAD'], aliases=['Tract:'], localize=True)
                            ).add_to(m)

                            # HPO Selected County's Roads Visualization
                            folium.GeoJson(
                                cached_load_json(geojson_paths["roads"]), name='Road Network',
                                style_function=lambda f: {'weight': 0.8},
                                highlight_function=lambda f: {'color': 'blue', 'weight': 1.4, 'dashArray': '4, 4'},
                                tooltip=GeoJsonTooltip(fields=['FULLNAME'], aliases=['Road Name:'], localize=True)
                            ).add_to(m)


                    Draw(
                        draw_options={
                            'polyline': False,
                            'polygon': False,
                            'circle': False,
                            'marker': False,
                            'circlemarker': False,
                            'rectangle': True
                                },
                            edit_options={'edit': False}
                        ).add_to(m)

                    folium.LayerControl().add_to(m)
                    with st.container():

                    
                        # Show the map only once (interactive, no gap)
                        clicked_info = st_folium(m, width=700, height=600)
                        st.markdown(
                        """
                        <style>
                        iframe[title="folium_map"] {
                            margin-bottom: -30px;
                        }
                        </style>
                        """,
                        unsafe_allow_html=True
                    )
                        
                        # --- Debug or placeholder to keep layout tight ---
                        st.markdown("")  # helps reduce iframe margin

                        # Print clicked census tract
                        if clicked_info and clicked_info.get("last_active_drawing"):
                                print("Entered Multiple Census Tracts Mode V1")
                                tract_props = clicked_info["last_active_drawing"]["properties"]
                                
                                countyfp = tract_props.get("COUNTYFP", None)
                                tract_name = tract_props.get("NAMELSAD", "Unknown")
                                tract_geoid = tract_props.get("GEOID", None)

                                # Lookup county
                                county_row = kansas_counties[kansas_counties["County Code"].astype(str).str.zfill(3) == str(countyfp).zfill(3)]
                                predict_crashes = st.button("Predict Crash Counts")

                                # # Rectangle selection Code

                                drawn_bounds = clicked_info["last_active_drawing"]["geometry"]["coordinates"][0]  # GeoJSON format

                                # Convert GeoJSON coordinates to Shapely polygon
                                drawn_polygon = Polygon(drawn_bounds)

                                # Load census tract GeoJSON
                                census_geojson = load_geojson(geojson_paths["tracts"])
                                tracts_gdf = gpd.GeoDataFrame.from_features(census_geojson["features"])
                                tracts_gdf.set_crs(epsg=4326, inplace=True)

                                # Intersect with tracts
                                intersecting_tracts = tracts_gdf[tracts_gdf.intersects(drawn_polygon)]

                                if not intersecting_tracts.empty:
                                    st.success(f"{len(intersecting_tracts)} census tracts intersect with your rectangle.")
                                    st.table(intersecting_tracts[["NAMELSAD"]].rename(columns={"NAMELSAD": "Selected Census Tracts"}).reset_index(drop=True))
                                    selected_multiple_census_tracts = list(intersecting_tracts["NAMELSAD"])
                                    print(intersecting_tracts["NAMELSAD"].values)

                                    # -------- NEW: reset state if the rectangle selection changed --------
                                    last = st.session_state.get("hpo_area_selected_tracts")
                                    if last != selected_multiple_census_tracts:
                                        st.session_state["hpo_area_selected_tracts"] = selected_multiple_census_tracts
                                        st.session_state["all_tract_user_inputs"] = {}       # clear old tract inputs
                                        st.session_state.pop("tract_input_selector", None)   # reset tract dropdown
                                else:
                                    st.warning("No census tracts found inside the drawn area.")
                                    selected_multiple_census_tracts = []

                                folium.GeoJson(
                                intersecting_tracts.__geo_interface__,
                                name='Intersecting Tracts',
                                style_function=lambda f: {'color': 'green', 'weight': 2},
                                tooltip=GeoJsonTooltip(fields=['NAMELSAD'], aliases=['Tract:'])
                                ).add_to(m) 

                                # ---------- BATCHED INPUTS FOR SELECTED TRACTS: fragment + form ----------
                                # NOTE: we reimplement multiple_input_section to render inside a FORM (container=st).


                                @st.fragment
                                def hpo_area_inputs_fragment(tract_names):
                                    # IMPORTANT: Do NOT put `with st.sidebar:` here; call this fragment inside a with st.sidebar block.
                                    if len(tract_names) == 0:
                                        st.warning("Please select at least one census tract.")
                                        return

                                    # 1) Tract dropdown OUTSIDE the form so it reruns the fragment immediately on change
                                    selected_input_tract = st.selectbox(
                                        "Select a Census Tract to enter inputs:",
                                        tract_names,
                                        key="tract_input_selector"
                                    )

                                    # Parse an ID for keying sliders (keeps your display text as-is)
                                    parts = str(selected_input_tract).split()
                                    tract_id = parts[2] if len(parts) >= 3 else str(selected_input_tract)

                                    # Ensure the accumulator exists (dict of dicts)
                                    if "all_tract_user_inputs" not in st.session_state:
                                        st.session_state.all_tract_user_inputs = {}

                                    # If we already have values for this tract, use them as defaults
                                    existing_for_this_tract = st.session_state.all_tract_user_inputs.get(selected_input_tract, {})

                                    # 2) Sliders INSIDE the form; values are only sent on submit
                                    with st.form("hpo_area_inputs_form", clear_on_submit=False):
                                        st.markdown("## Enter Input Variables")

                                        user_inputs = {}
                                        user_inputs.update(multiple_input_section(
                                            "Input Weather Variables",
                                            classification_weather_keys,
                                            tabnet_classification_range_config,
                                            tract_id=tract_id,
                                            labels=classification_weather_labels,
                                            container=st,
                                            existing=existing_for_this_tract
                                        ))
                                        user_inputs.update(multiple_input_section(
                                            "Input Traffic Characteristics",
                                            traffic_keys_classification,
                                            tabnet_classification_range_config,
                                            tract_id=tract_id,
                                            labels=traffic_keys_classification_labels,
                                            container=st,
                                            existing=existing_for_this_tract
                                        ))

                                        submitted = st.form_submit_button(f"Submit Inputs for {selected_input_tract}")

                                    if submitted:
                                        # Merge/overwrite just this tract's dict; preserves previously submitted tracts
                                        st.session_state.all_tract_user_inputs[selected_input_tract] = user_inputs

                                        # Progress feedback
                                        if len(st.session_state.all_tract_user_inputs) == len(tract_names):
                                            st.success("All inputs have been provided for all the selected census tracts. You can now proceed with the prediction.")
                                        else:
                                            st.success(
                                                f"Inputs saved for {selected_input_tract}. "
                                                "Select another tract from the dropdown to submit its inputs."
                                            )

                                    # (Keep your debug prints)
                                    print("Saved Inputs:", st.session_state.all_tract_user_inputs)
                                    if len(st.session_state.all_tract_user_inputs) == len(tract_names):
                                        print("User Inputs for Selected Census Tracts:\n", st.session_state.all_tract_user_inputs)

                                # Render the fragment INSIDE the sidebar (caller side sets the container)
                                with st.sidebar:
                                    # -------- NEW: drive the fragment with the CURRENT rectangle's tracts only --------
                                    current_tracts = st.session_state.get("hpo_area_selected_tracts", selected_multiple_census_tracts)
                                    hpo_area_inputs_fragment(current_tracts)

                                if predict_crashes:
                                    chosen_model = "CatBoost"
                                    # -------- NEW: restrict predictions to CURRENT rectangle selection --------
                                    current_tracts = st.session_state.get("hpo_area_selected_tracts", [])
                                    all_user_inputs_for_selected_tracts = st.session_state.get("all_tract_user_inputs", {})

                                    prediction_data = []

                                    for tract_name in current_tracts:
                                        user_inputs = all_user_inputs_for_selected_tracts.get(tract_name, {})
                                        classification_inputs = {}

                                        # Prepare model input
                                        for key in classification_weather_keys + demographic_keys + traffic_keys_classification + ["avg_temp"]:
                                            if key in user_inputs:
                                                classification_inputs[key] = user_inputs[key]
                                            elif key == "avg_temp":
                                                classification_inputs[key] = (classification_inputs['min_temp'] + classification_inputs['max_temp']) / 2
                                            elif key in demographic_keys:
                                                classification_inputs[key] = mean_values_demographic_variables_from_valid_dmvt.get(key, 0)
                                            else:
                                                classification_inputs[key] = 0

                                        # Convert booleans to strings
                                        for k in ['is_weekend', 'is_holiday']:
                                            classification_inputs[k] = str(classification_inputs[k])

                                        # Prepare request payload
                                        if chosen_model.strip() in models_mapping:
                                            request_data = {
                                                "model_name": models_mapping[chosen_model],
                                                "inputs": classification_inputs
                                            }
                                            print("Inputs passed to the Model:", classification_inputs)
                                            try:
                                                # API call
                                                if request_data["model_name"] == "catBoost_regression_pickled":
                                                    response = requests.post("http://127.0.0.1:8000/predict_regression", json=request_data)
                                                else:
                                                    response = requests.post("http://127.0.0.1:8000/predict_classification", json=request_data)

                                                # Store prediction result
                                                if response.status_code == 200:
                                                    result = response.json()
                                                    predicted_crashes = result['predicted_crashes']
                                                else:
                                                    predicted_crashes = f"API Error {response.status_code}"

                                            except Exception as e:
                                                predicted_crashes = f"Request Error: {e}"

                                            prediction_data.append({
                                                "Census Tract": tract_name,
                                                "Predicted Crashes": predicted_crashes
                                            })

                                    # Convert to DataFrame and display
                                    predictions_df = pd.DataFrame(prediction_data)
                                    st.markdown("### Crash Predictions")
                                    st.table(predictions_df.reset_index(drop=True))

        # ================================= HPO: Map Visualization =================================
        elif hpo_county_mode == "Map Visualization":
            # ---------------- Sidebar inputs: fragment + form (no rerun while sliding) ----------------


            @st.fragment
            def hpo_mapviz_inputs_fragment():
                with st.form("hpo_mapviz_inputs_form", clear_on_submit=False):
                    inputs = {}
                    # Same inputs you had before, but rendered INSIDE the form
                    inputs.update(input_section_v2(
                        "Input Weather Variables",
                        classification_weather_keys,
                        tabnet_classification_range_config,
                        classification_weather_labels,
                        container=st,  # <- IMPORTANT: write to the form context
                    ))
                    inputs.update(input_section_v2(
                        "Input Traffic Characteristics",
                        traffic_keys_classification,
                        tabnet_classification_range_config,
                        traffic_keys_classification_labels,
                        container=st,  # <- IMPORTANT
                    ))
                    submitted = st.form_submit_button("Submit Inputs")
                if submitted:
                    st.session_state["hpo_mapviz"] = inputs
                    st.success("Inputs submitted. Now click **Predict Crash Counts** below the map.")

            # Render the fragment INSIDE the sidebar (required)
            with st.sidebar:
                hpo_mapviz_inputs_fragment()

            # ---------------- Map (kept out of fragment, so it doesn't rerender while sliding) ----------------
            with st.spinner("Loading visualization... Please wait."):
                folium.GeoJson(
                    cached_load_json(geojson_paths["kansas"]), name='Kansas Boundary',
                    style_function=lambda f: {'fillOpacity': 0, 'color': 'black', 'weight': 3}
                ).add_to(m)

                folium.GeoJson(
                    cached_load_json(geojson_paths["tracts"]), name='Census Tracts',
                    style_function=lambda f: {'fillOpacity': 0, 'color': "#150202", 'weight': 0.7},
                    highlight_function=lambda f: {'fillColor': 'brown', 'color': 'brown', 'weight': 3.5, 'dashArray': '12, 12'},
                    tooltip=GeoJsonTooltip(fields=['NAMELSAD'], aliases=['Tract:'], localize=True)
                ).add_to(m)

                folium.GeoJson(
                    cached_load_json(geojson_paths["roads"]), name='Road Network',
                    style_function=lambda f: {'weight': 0.8},
                    highlight_function=lambda f: {'color': 'blue', 'weight': 1.4, 'dashArray': '4, 4'},
                    tooltip=GeoJsonTooltip(fields=['FULLNAME'], aliases=['Road Name:'], localize=True)
                ).add_to(m)

                folium.LayerControl().add_to(m)
            with st.container():

                clicked_info = st_folium(m, width=700, height=500)
                st.markdown(
                    """
                    <style>
                    iframe[title="folium_map"] { margin-bottom: -30px; }
                    </style>
                    """,
                    unsafe_allow_html=True
                )
                st.markdown("")  # keep layout tight

                # Optional selection feedback
                if clicked_info and clicked_info.get("last_active_drawing"):
                    tract_props = clicked_info["last_active_drawing"]["properties"]
                    countyfp = tract_props.get("COUNTYFP", None)
                    tract_name = tract_props.get("NAMELSAD", "Unknown")

                    county_row = kansas_counties[kansas_counties["County Code"].astype(str).str.zfill(3) == str(countyfp).zfill(3)]
                    if not county_row.empty:
                        county_name = county_row.iloc[0]["County Name"]
                        st.success(f"**Selected {tract_name}** is in **{county_name} County**")
                    else:
                        st.warning("County not found for the selected tract.")

                # ---------------- Predict button: use last submitted inputs only ----------------
                if st.button("Predict Crash Counts"):
                    chosen_model = "CatBoost"  # fixed for HPO
                    if "hpo_mapviz" not in st.session_state:
                        st.warning("Please submit inputs first (use the **Submit Inputs** button in the sidebar).")
                    else:
                        ui_inputs = st.session_state["hpo_mapviz"]

                        # Build payload once, from submitted values
                        classification_inputs = {}
                        for key in classification_weather_keys + demographic_keys + traffic_keys_classification + ["avg_temp"]:
                            if key in ui_inputs:
                                classification_inputs[key] = ui_inputs[key]
                            elif key == "avg_temp":
                                classification_inputs[key] = (ui_inputs['min_temp'] + ui_inputs['max_temp']) / 2
                            elif key in demographic_keys:
                                # If you have your mean values dict available here:
                                classification_inputs[key] = mean_values_demographic_variables_from_valid_dmvt.get(key, 0)
                            else:
                                classification_inputs[key] = 0

                        for k in ['is_weekend', 'is_holiday']:
                            if k in classification_inputs:
                                classification_inputs[k] = str(classification_inputs[k])

                        request_data = {
                            "model_name": models_mapping[chosen_model],
                            "inputs": classification_inputs
                        }

                        try:
                            url = "http://127.0.0.1:8000/predict_classification"
                            response = requests.post(url, json=request_data, timeout=30)
                            if response.status_code == 200:
                                result = response.json()
                                st.success(f"Predicted Crashes: {result.get('predicted_crashes')}")
                            else:
                                st.error(f"API Error: {response.status_code} - {response.text}")
                        except Exception as e:
                            st.error(f"Request Error: {e}")






    # ================================= Researcher =================================
    elif input_role == 'Researcher(Deep Dive)':
        with st.sidebar:
            st.header("Model Selection")
            chosen_model = st.selectbox(
                "Choose the ML Alg to predict the crash count",
                options=['Random Forest', 'AdaBoost', 'Gradient Boost', 'XGBoost', 'LightGBM', 'CatBoost', 'CatBoost Regression', 'TabNet'],
                key="researcher_model_choice",
            )


        @st.fragment
        def researcher_inputs_fragment():
            with st.form("researcher_inputs_form", clear_on_submit=False):
                inputs = {}
                if chosen_model == "CatBoost Regression":
                    inputs.update(input_section_v2("Input Weather Variables", weather_keys, range_config, weather_labels, container=st))
                    inputs.update(input_section_v2("Input Demographic Variables", demographic_keys, range_config, demographic_labels, container=st))
                    inputs.update(input_section_v2("Input Traffic Characteristics", traffic_keys_regression, range_config, traffic_regression_labels, container=st))
                else:
                    inputs.update(input_section_v2("Input Weather Variables", classification_weather_keys, tabnet_classification_range_config, classification_weather_labels, container=st))
                    inputs.update(input_section_v2("Input Demographic Variables", demographic_keys, tabnet_classification_range_config, demographic_labels, container=st))
                    inputs.update(input_section_v2("Input Traffic Characteristics", traffic_keys_classification, tabnet_classification_range_config, traffic_keys_classification_labels, container=st))
                submitted = st.form_submit_button("Submit Inputs")
            if submitted:
                st.session_state["researcher_inputs"] = inputs
                st.success("Inputs submitted. Now click **Predict Crash Counts** below the map.")

        with st.sidebar:
            researcher_inputs_fragment()

        with st.spinner("Loading visualization... Please wait."):
            # Map for Researcher
            folium.GeoJson(cached_load_json(geojson_paths["kansas"]), name='Kansas Boundary',
                        style_function=lambda f: {'fillOpacity': 0, 'color': 'black', 'weight': 3}).add_to(m)
            folium.GeoJson(cached_load_json(geojson_paths["tracts"]), name='Census Tracts',
                        style_function=lambda f: {'fillOpacity': 0, 'color': "#150202", 'weight': 0.7},
                        highlight_function=lambda f: {'fillColor': 'brown', 'color': 'brown', 'weight': 3.5, 'dashArray': '12, 12'},
                        tooltip=GeoJsonTooltip(fields=['NAMELSAD'], aliases=['Tract:'], localize=True)).add_to(m)
            folium.GeoJson(cached_load_json(geojson_paths["roads"]), name='Road Network',
                        style_function=lambda f: {'weight': 0.8},
                        highlight_function=lambda f: {'color': 'blue', 'weight': 1.4, 'dashArray': '4, 4'},
                        tooltip=GeoJsonTooltip(fields=['FULLNAME'], aliases=['Road Name:'], localize=True)).add_to(m)
        st.markdown("<style>iframe[title='folium_map']{margin-bottom:-30px;}</style>", unsafe_allow_html=True)

        # Default state for selected tract
        if "selected_tract_id" not in st.session_state:
            st.session_state.selected_tract_id = None
        with st.container():
            clicked_info = st_folium(m, width=700, height=600)


            if clicked_info and clicked_info.get("last_active_drawing"):
                        tract_props = clicked_info["last_active_drawing"]["properties"]
                        countyfp = tract_props.get("COUNTYFP", None)
                        tract_name = tract_props.get("NAMELSAD", "Unknown")

                        # Store tract selection in session_state
                        st.session_state.selected_tract_id = tract_name
        
                        county_row = kansas_counties[kansas_counties["County Code"].astype(str).str.zfill(3) == str(countyfp).zfill(3)]
                        if not county_row.empty:
                            county_name = county_row.iloc[0]["County Name"]
                            st.success(f"**Selected {tract_name}** is in **{county_name} County**")
                        else:
                            st.warning("County not found for the selected tract.")

            if st.button("Predict Crash Counts", disabled=st.session_state.selected_tract_id is None):
                if "researcher_inputs" not in st.session_state:
                    st.warning("Please submit inputs first.")
                else:
                    ui_inputs = st.session_state["researcher_inputs"]
                    if chosen_model == "CatBoost Regression":
                        payload = {}
                        for key in weather_keys + demographic_keys + traffic_keys_regression + ["avg_temp"]:
                            if key in ui_inputs:
                                payload[key] = ui_inputs[key]
                            elif key == "avg_temp":
                                payload[key] = (ui_inputs['min_temp'] + ui_inputs['max_temp']) / 2
                            else:
                                payload[key] = 0
                        for k in ['is_weekend', 'is_holiday']:
                            if k in payload:
                                payload[k] = str(payload[k])
                    else:
                        payload = {}
                        for key in classification_weather_keys + demographic_keys + traffic_keys_classification + ["avg_temp"]:
                            if key in ui_inputs:
                                payload[key] = ui_inputs[key]
                            elif key == "avg_temp":
                                payload[key] = (ui_inputs['min_temp'] + ui_inputs['max_temp']) / 2
                            else:
                                payload[key] = 0
                        for k in ['is_weekend', 'is_holiday']:
                            if k in payload:
                                payload[k] = str(payload[k])

                    request_data = {"model_name": models_mapping[chosen_model], "inputs": payload}
                    url = ("http://127.0.0.1:8000/predict_regression"
                        if request_data["model_name"] == "catBoost_regression_pickled"
                        else "http://127.0.0.1:8000/predict_classification")
                    try:
                        r = requests.post(url, json=request_data, timeout=30)
                        if r.status_code == 200:
                            result = r.json()
                            pred = result.get("predicted_crashes", result.get("predicted_crash_count"))
                            st.success(f"Predicted Crashes: {pred}")
                        else:
                            st.error(f"API Error: {r.status_code} - {r.text}")
                    except Exception as e:
                        st.error(f"Request Error: {e}")

    # -------------------- Reset Session --------------------
    with st.sidebar:
        if st.button("Reset Session"):
            st.session_state.show_home_modal = True
            st.rerun()
