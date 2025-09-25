from pydantic import BaseModel, Field

# # Schema for Classification Models:

class CrashInputRegression(BaseModel):

# # Schema for CatBoost Regression Model: This is Working, already tested


    # Weather Variables
    avg_temp: float = None  # Will be set in validator
    max_temp: int = Field(..., ge=0, le=120)
    min_temp: int = Field(..., ge=-20, le=84)
    precip: float = Field(..., ge=0.0, le=9.0)
    snow: float = Field(..., ge=0.0, le=19.0)
    snow_depth: float = Field(..., ge=0.0, le=19.0)
    avg_humid: float = Field(..., ge=12.66, le=100.0)
    avg_wndSpd: int = Field(..., ge=0, le=33)
    
    # Demographic Variables
    totPop: float = Field(..., ge=0)
    povper: float = Field(..., ge=0.0, le=62.0)
    hhnov: float = Field(..., ge=0.0, le=590.0)
    pctnvh: float = Field(..., ge=0.0, le=100.0)
    avgcmm: float = Field(..., ge=2.0, le=43.0)
    trnfrq: float = Field(..., ge=0.0, le=100.0)  # Not present in dict, kept original
    jb45dr: float = Field(..., ge=99.0, le=270000.0)
    drvpoi: float = Field(..., ge=2.0, le=49.0)
    wlkpoi: float = Field(..., ge=10.0, le=853.0)


    # Traffic Variables
    dvmt: float = Field(..., ge=0)
    is_weekend: int = None
    prev_yr_crash: float = Field(..., ge=0, le=500) # This input used only in the Regression model, but not in Classification models
    is_holiday: int = None



    ## Below inputs are used only in the Classification models, but not in Regression models:

    # afternoon_count: Optional[float] = Field(None, ge=0, le=500) # Should add this input as models are trained on it
    # day_count: Optional[float] = Field(None, ge=0, le=500) # Should add this input as models are trained on it
    # morning_count: Optional[float] = Field(None, ge=0, le=500) # Should add this input as models are trained on it
    # night_count: Optional[float] = Field(None, ge=0, le=500) # Should add this input as models are trained on it


# # Schema for Classification Models:

class CrashInputClassification(BaseModel):

    # Weather Variables
    avg_temp: float = None  # Will be set in validator
    max_temp: int = Field(..., ge=0, le=120)
    min_temp: int = Field(..., ge=-20, le=84)
    precip: float = Field(..., ge=0.0, le=9.0)
    snow: float = Field(..., ge=0.0, le=19.0)
    snow_depth: float = Field(..., ge=0.0, le=19.0)
    avg_humid: float = Field(..., ge=12.66, le=100.0)
    avg_wndSpd: float = Field(..., ge=0, le=33.0)

    # Demographic Variables
    totPop: float = Field(..., ge=0)
    povper: float = Field(..., ge=0.0, le=62.0)
    hhnov: float = Field(..., ge=0.0, le=590.0)
    pctnvh: float = Field(..., ge=0.0, le=100.0)
    avgcmm: float = Field(..., ge=2.0, le=43.0)
    trnfrq: float = Field(..., ge=0.0, le=100.0)  # Not present in dict, kept original
    jb45dr: float = Field(..., ge=99.0, le=270000.0)
    drvpoi: float = Field(..., ge=2.0, le=49.0)
    wlkpoi: float = Field(..., ge=10.0, le=853.0)

    # Traffic Variables
    dvmt: float = Field(..., ge=0.0, le=1610.0)
    is_weekend: int = Field(..., ge=0, le=1)
    # prev_yr_crash: float = Field(..., ge=0.0, le=390.0)
    is_holiday: int = Field(..., ge=0, le=1)
    afternoon_count: float = Field(..., ge=0.0, le=500.0)  # Should add this input as models are trained on it
    day_count: float = Field(..., ge=0.0, le=500.0)  # Should add this input as models are trained on it
    morning_count: float = Field(..., ge=0.0, le=500.0)  # Should add this input as models are trained on it
    night_count: float = Field(..., ge=0.0, le=500.0)  # Should add this input as models are trained on it
    yearly_total_count: float = Field(..., ge=0.0, le=500.0)  # Should add this input as models are trained on it
    # Note: prev_year_total_count is not used in the model, so it is commented  out
    # prev_year_total_count: Optional[float] = Field(None, ge=0.0, le=500.0)  # Should remove this input as model is not trained on it xxx----xxx




    # # Weather Variables
    # avg_temp: float = None  # Will be set in validator
    # max_temp: int = Field(..., ge=0, le=120)
    # min_temp: int = Field(..., ge=-20, le=100)
    # precip: float = Field(..., ge=0, le=10)
    # snow: float = Field(..., ge=0, le=36)
    # snow_depth: float = Field(..., ge=0, le=60)
    # rel_humidity: float = Field(..., ge=0, le=100)
    # wind_speed: int = Field(..., ge=0, le=100)
    
    # # Demographic Variables
    # tot_pop: Optional[float] = Field(None, ge=0)
    # poverty_percent: Optional[float] = Field(None, ge=0, le=100)
    # no_vehicle_households: Optional[float] = Field(None, ge=0)
    # no_car_percent: Optional[float] = Field(None, ge=0, le=100)
    # avg_commute_time: Optional[float] = Field(None, ge=0, le=120)
    # freq_transit_per_sq_mi: Optional[float] = Field(None, ge=0, le=100)
    # jobs_within_45min: Optional[float] = Field(None, ge=0)
    # avg_drive_time_poi: Optional[float] = Field(None, ge=0, le=60)
    # avg_walk_time_poi: Optional[float] = Field(None, ge=0, le=60)


    # # Traffic Variables
    # daily_vehicle_miles: Optional[float] = Field(None, ge=0)
    # is_weekend: Optional[int] = None
    # # prev_year_total_count: Optional[float] = Field(None, ge=0, le=500) # Should remove this input as model is not trained on it xxx----xxx
    # afternoon_count: Optional[float] = Field(None, ge=0, le=500) # Should add this input as models are trained on it
    # day_count: Optional[float] = Field(None, ge=0, le=500) # Should add this input as models are trained on it
    # morning_count: Optional[float] = Field(None, ge=0, le=500) # Should add this input as models are trained on it
    # night_count: Optional[float] = Field(None, ge=0, le=500) # Should add this input as models are trained on it
    # yearly_total_count: Optional[float] = Field(None, ge=0, le=500) # Should add this input as models are trained on it
    # is_holiday: Optional[int] = None



class ModelSelection(BaseModel):
    model_name: str
    inputs: CrashInputClassification

class ModelSelection_Regression(BaseModel):
    model_name: str
    inputs: CrashInputRegression
