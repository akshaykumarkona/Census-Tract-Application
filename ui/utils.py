import os
import json
from shapely.geometry import shape as shapely_shape
from shapely.ops import unary_union
import pandas as pd
import streamlit as st


geojson_paths = {
        "kansas": r'ui/data/kansas.geojson',
        "counties_base": r"ui/data/ks_county_files",
        "county_info": r'ui/data/FRPP_GLC__United_States_April_8_2024.csv',
        "tracts": r'ui/data/Tiger_2020_Boundaries/Tiger_2020_Boundaries.geojson',
        "roads": r"ui/data/tl_2024_20_prisecroads/tl_2024_20_prisecroads_geojson/tl_2024_20_prisecroads.geojson",
        # "static_crashes": r"ui/data/static_crashes_week1.csv"
    }


@st.cache_data
def load_geojson(path):
    with open(path, 'r') as f:
        return json.load(f)
    
@st.cache_data
def get_county_path(name):
    return os.path.join(geojson_paths["counties_base"], name.capitalize() + ".geo.json")

@st.cache_data
def combine_geojsons(counties):
    combined = []
    for _, row in counties.iterrows():
        path = get_county_path(row['County Name'])
        if os.path.exists(path):
            with open(path) as f:
                geo = json.load(f)
                combined.extend(geo.get("features", []))
    return {"type": "FeatureCollection", "features": combined}

@st.cache_data
def get_bounds(geojson_features):
    shapes = [shapely_shape(feat['geometry']) for feat in geojson_features]
    unioned = unary_union(shapes)
    return [[unioned.bounds[1], unioned.bounds[0]], [unioned.bounds[3], unioned.bounds[2]]]  # [[south, west], [north, east]]

@st.cache_data
def cached_read_csv(path, encoding="utf-8"):
    return pd.read_csv(path, encoding=encoding)

@st.cache_data
def cached_load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)














# Pretty formats per key (fallback chosen by step)
SLIDER_FORMATS = {
    # integers
    "max_temp": "%d", "min_temp": "%d", "avg_humid": "%d",
    "dvmt": "%d", "prev_yr_crash": "%d",
    "afternoon_count": "%d", "day_count": "%d",
    "morning_count": "%d", "night_count": "%d",
    "yearly_total_count": "%d", "is_weekend": "%d", "is_holiday": "%d",
    # floats
    "precip": "%.2f", "snow": "%.2f", "snow_depth": "%.2f",
    "avg_wndSpd": "%.2f",
}

def _infer_format(step, key):
    if key in SLIDER_FORMATS:
        return SLIDER_FORMATS[key]
    return "%d" if float(step).is_integer() else "%.2f"

def _minmax_row(tgt, left, right):
    tgt.markdown(
        f"<div style='display:flex;justify-content:space-between;"
        f"font-size:0.8rem;opacity:0.7;margin-top:-6px;'>"
        f"<span>{left:g}</span><span>{right:g}</span></div>",
        unsafe_allow_html=True
    )


def input_section_v2(title, keys, range_dict, label_map=None, container=None):
    tgt = container or st
    tgt.subheader(title)
    sliders = {}
    for k in keys:
        label = (label_map or {}).get(k, k)
        mn, mx, stp = range_dict[k]
        # force numeric in case JSON loads strings
        mn, mx, stp = float(mn), float(mx), float(stp)
        fmt = _infer_format(stp, k)
        default_val = mn if k in ['is_weekend', 'is_holiday'] else (mn + mx) / 2.0

        if fmt == "%d":
            sliders[k] = tgt.slider(label, int(mn), int(mx), int(default_val),
                                    step=int(stp), format=fmt, key=f"{title}_{k}")
            _minmax_row(tgt, int(mn), int(mx))
        else:
            sliders[k] = tgt.slider(label, mn, mx, float(default_val),
                                    step=stp, format=fmt, key=f"{title}_{k}")
            _minmax_row(tgt, mn, mx)
    return sliders

def multiple_input_section(title, keys, config_ranges, tract_id, labels, container, existing=None):
    container.subheader(title)
    sliders = {}
    existing = existing or {}
    for k in keys:
        mn, mx, stp = config_ranges.get(k, (0, 100, 1))
        mn, mx, stp = float(mn), float(mx), float(stp)
        fmt = _infer_format(stp, k)
        midpoint = mn if k in ['is_weekend', 'is_holiday'] else (mn + mx) / 2.0
        default_val = float(existing.get(k, midpoint))
        lbl = f"{labels.get(k, k.replace('_',' ').title())} (Tract ID: {tract_id})"

        if fmt == "%d":
            sliders[k] = container.slider(lbl, int(mn), int(mx), int(default_val),
                                          step=int(stp), format=fmt, key=f"{k}_{tract_id}")
            _minmax_row(container, int(mn), int(mx))
        else:
            sliders[k] = container.slider(lbl, mn, mx, float(default_val),
                                          step=stp, format=fmt, key=f"{k}_{tract_id}")
            _minmax_row(container, mn, mx)
    return sliders



















# # Localized inputs section that can render inside a form or any container
# def input_section_v2(title, keys, range_dict, label_map=None, container=None):
#     tgt = container or st
#     tgt.subheader(title)
#     sliders = {}
#     for k in keys:
#         label = label_map[k] if label_map and k in label_map else k
#         min_val, max_val, step = range_dict[k]
#         default_val = (min_val + max_val) / 2.0
#         if any(isinstance(v, float) for v in (min_val, max_val, step)):
#             sliders[k] = tgt.slider(label, float(min_val), float(max_val), float(default_val),
#                                     step=float(step), key=f"{title}_{k}")
#         else:
#             sliders[k] = tgt.slider(label, int(min_val), int(max_val), int(default_val),
#                                     step=int(step), key=f"{title}_{k}")
#     return sliders




# # ---------- Helper: render one group of sliders with per-tract keys and existing defaults ----------
# def multiple_input_section(title, keys, config_ranges, tract_id, labels, container, existing=None):
#     container.subheader(title)
#     sliders = {}
#     existing = existing or {}
#     for k in keys:
#         min_val, max_val, step = config_ranges.get(k, (0, 100, 1))
#         # numeric types for Streamlit sliders
#         min_val = float(min_val); max_val = float(max_val); step = float(step)
#         # default from saved values (if any), else midpoint (or min for boolean-ish)
#         midpoint = float(min_val) if k in ['is_weekend', 'is_holiday'] else float((min_val + max_val) / 2)
#         default_val = float(existing.get(k, midpoint))
#         label_text = labels.get(k, k.replace('_', ' ').title())
#         sliders[k] = container.slider(
#             f"{label_text} (Tract ID: {tract_id})",
#             min_value=min_val,
#             max_value=max_val,
#             value=default_val,
#             step=step,
#             key=f"{k}_{tract_id}"
#         )
#     return sliders






# Inputs Keys For Backend:
classification_weather_keys = ["max_temp", "min_temp", "precip", "snow", "snow_depth", "avg_humid", "avg_wndSpd"]
weather_keys = ["max_temp", "min_temp", "precip", "snow", "snow_depth", "avg_humid", "avg_wndSpd"]
demographic_keys = ["totPop", "povper", "hhnov", "pctnvh", "avgcmm", "trnfrq", "jb45dr", "drvpoi", "wlkpoi"]
traffic_keys = ["dvmt", "prev_yr_crash", "is_weekend", "is_holiday"]
traffic_keys_classification = ["dvmt", "is_weekend", "afternoon_count", "day_count", "morning_count", "night_count", "yearly_total_count", "is_holiday"]
traffic_keys_regression = ["dvmt", "is_weekend", "prev_yr_crash", "is_holiday"]


## Inputs Labels For UI:
classification_weather_labels = {
    "max_temp": "Maximum Temperature (°F)",
    "min_temp": "Minimum Temperature (°F)",
    "precip": "Precipitation (mm)",
    "snow": "Snowfall (mm)",
    "snow_depth": "Snow Depth (mm)",
    "avg_humid": "Average Humidity (%)",
    "avg_wndSpd": "Average Wind Speed (m/s)"
}

weather_labels = {
    "max_temp": "Maximum Temperature (°F)",
    "min_temp": "Minimum Temperature (°F)",
    "precip": "Precipitation (mm)",
    "snow": "Snowfall (mm)",
    "snow_depth": "Snow Depth (mm)",
    "avg_humid": "Average Humidity (%)",
    "avg_wndSpd": "Average Wind Speed (m/s)"
}

demographic_labels = {
    "totPop": "Total Population",
    "povper": "Poverty Percentage (%)",
    "hhnov": "Approximate Households without Vehicle (Count)",
    "pctnvh": "Households with No-Vehicle (%)",
    "avgcmm": "Average Commute Time (mins)",
    "trnfrq": "Frequency of Transit per Square Mile",
    "jb45dr": "Jobs within 45-min Drive",
    "drvpoi": "Approximate Average Time to Points of Interest (Driveable) (mins)",
    "wlkpoi": "Approximate Average Time to Points of Interest (Walkable) (mins)"
}

traffic_labels = {
    "dvmt": "Daily Vehicle Miles Traveled",
    "prev_yr_crash": "Crashes in Previous Year",
    "is_weekend": "Is Weekend (0 = Weekday, 1 = Weekend)",
    "is_holiday": "Is Holiday (0 = No, 1 = Yes)"
}

traffic_keys_classification_labels = {
    "dvmt": "Daily Vehicle Miles Traveled",
    "is_weekend": "Is Weekend (Yes=1, No=0)",
    "afternoon_count": "Afternoon Traffic Count",
    "day_count": "Daytime Traffic Count",
    "morning_count": "Morning Traffic Count",
    "night_count": "Night Traffic Count",
    "yearly_total_count": "Total Yearly Traffic Count",
    "is_holiday": "Is Holiday (Yes=1, No=0)"
}

traffic_regression_labels = {
    "dvmt": "Daily Vehicle Miles Traveled",
    "is_weekend": "Is Weekend (0 = Weekday, 1 = Weekend)",
    "prev_yr_crash": "Crashes in Previous Year",
    "is_holiday": "Is Holiday (0 = No, 1 = Yes)"
}










