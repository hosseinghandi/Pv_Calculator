"""Grasshopper Script Instance"""
import System
import Rhino
import Grasshopper

import rhinoscriptsyntax as rs
import System
import Rhino
import Grasshopper
import json
import rhinoscriptsyntax as rs
import ghpythonlib.components as gh
import ghpythonlib.component as ghc
import rhinoscriptsyntax as rh 
from Rhino.Geometry import Brep
import math 
import csv
from datetime import datetime, timedelta
from collections import namedtuple
from ghpythonlib.treehelpers import list_to_tree


# Role of the component:
# A) Gets building geometry and picks out the roof of the building to prepare a calculation surface on which Ladybug should simulate.
# B) Gets EPW weather file and extracts necessary data for simulation and corresponding calculations.
# C-D) If the user provided the inclination of the panels, calculates the Solar Elevation Angle to calculate the panel distances.
#      Moreover, takes the period preference of the user to create a proper data list,
#      based on which the data is passed to other components.

# Description of the inputs
ghenv.Component.Params.Input[0].Description = (
'Rhino Breps representing the buildings for which PV panel output will be calculated. '
'Please ensure the input is flattened and that you are providing valid geometry '
'(must be a solid, valid polySurface).'
)
ghenv.Component.Params.Input[1].Description = (
'An EPW file path as a string pointing to the file location on your system.'
)
ghenv.Component.Params.Input[2].Description = (
'Inclination of the PV panels in degrees. If no inclination is provided, the algorithm '
'assumes a horizontal installation strategy.\n'
'Default value: 0 (horizontal)'
)
ghenv.Component.Params.Input[3].Description = (
'Set to "True" to enable monthly analysis. '
'If not provided, the entire year will be considered by Ladybug.'
)

# Description of the Outputs
ghenv.Component.Params.Output[0].Description = (
'The selected roof surface(s) for which PV panel output will be calculated.'
)
ghenv.Component.Params.Output[1].Description = (
'This output should be connected to the PV_output_calculator component.'
)

# Description of component
ghenv.Component.Name = 'PV_Initializer'
ghenv.Component.NickName = 'PV_Initializer'
ghenv.Component.Category = 'PV_Panel'
ghenv.Component.Description = (
'Extracts building roof geometry and EPW weather data to prepare '
'the necessary inputs for PV energy simulation via PV_output_calculator.'
)
def cal_elevation(latitude, longitude, timezone):
    try:
        if all([latitude is not None, longitude is not None, timezone is not None]):
            #The row distance in PV fields is customarily determined by the shadow length on 21 December at solar noon
            #For more data check https://doi.org/10.3390/en14133850 
            date_time = datetime(2024, 12, 21, 12, 0, 0) 
            lat_rad = math.radians(latitude)
            N = date_time.timetuple().tm_yday

            # Solar Declination (δ)
            delta = 23.45 * math.sin(math.radians((360 / 365) * (N - 81)))
            # Hour Angle (γ)
            
            lstm = 15 * float(timezone)
            TC1 = 4*(longitude-lstm)
            B = math.radians((360 / 365) * (N - 81))
            EOT = 9.87 * math.sin(2 * B) - 7.53 * math.cos(B) - 1.5 * math.sin(B)
            TC = TC1 + EOT
            LT = 12 
            LST = LT + (TC / 60)
            gamma = 15 * (LST - 12)

            # Solar Elevation Angle (α)
            return (
                math.degrees(math.asin(
                    math.sin(lat_rad) * math.sin(math.radians(delta)) +
                    math.cos(lat_rad) * math.cos(math.radians(delta)) * math.cos(math.radians(gamma))
                )))
        else: raise ValueError("Latitude, longitude, or timezone is missing.")
    except Exception as e:
        raise RuntimeError(f"Solar elevation calculation failed: {e}")

def epw_open(epw_path ) : 
    if not epw_path:
        raise ValueError("No EPW file path provided.")
    try :
        with open(epw_path, 'r') as epw:
            reader = csv.reader(epw)
            location = next(reader)
            location_data =(location [1] , location [6] , location [7])
            latitude = float(location [6])
            longitude = float(location [7])
            timezone = float(location[8])
            
            # Skip the first 8 lines of EPW file since they are not necessary data
            for _ in range(7):
                next(reader)
                
            model_year = []
            for row in reader:
                model_year.append(str(row[0]))
            #take necessary info for location, lat and long
            model_year_bounds = str(gh.Bounds(model_year)).split(",")
            return ((
                f"1. Environmental and Geographical:\n\n"
                f"Location: {location_data[0]}\n"
                f"Latitude: {float(location_data[1]):.2f}\n"
                f"Longitude: {float(location_data[2])}\n"
                f"Weather Data Source: EPW file based on model years "
                f"{model_year_bounds[0]}-{model_year_bounds[1]}\n\n"
            ),(latitude, longitude, timezone)
            )
    except FileNotFoundError :
        raise FileNotFoundError(f"EPW file not found at path: {epw_path}")
    except Exception as e:
        raise RuntimeError(f"[epw_open] Something went wrong: {e}")

def addTiltSurface(roofs , ang ) :
    try:
        if (roofs):
            if len(roofs) == 1:
                cen = gh.ConstructPoint(0,0,max(gh.Deconstruct(gh.Area(roofs)[1])) + 20) 
            else:
                cen = gh.ConstructPoint(0,0,max(gh.Deconstruct(gh.Area(roofs)[1])[2]) + 20)

            plane = gh.Rectangle(cen, 2, 2, 0)[0]
            ax = gh.Explode(plane, True)[0][0]
            tiltPlane = gh.RotateAxis(plane, gh.Radians(ang), ax)[0]
            return tiltPlane
        else: raise ValueError("The roof input is missed")
    except Exception as e:
        raise RuntimeError(f"Something went wrong: {e}")

def roof_picker(buildings , ang ) :
    roofs=[]
    try:
        if len(buildings) > 0:
            for building in buildings:
                dec = gh.DeconstructBrep(building)
                for i in range(len(dec[0])):
                    cent = gh.Area(dec[0][i])[1]
                    norm = gh.EvaluateSurface((dec[0][i]) ,cent)[1]
                    if norm[2]==1:
                        if cent[2] > 0 :
                            roofs.append(dec[0][i])
                    if norm[2]==-1 and cent[2] > 0:
                        roofs.append(dec[0][i])
        else: raise ValueError("Building geometry could not be deconstructed!")
        
        # If inclined, add a single inclined surface to calculate Global Tilted Irradiance (GTI).
        # This method is used to save simulation time, considering the trade-off for inaccuracy which can be 
        # acceptable for early stage of design.
        if ang > 0:
            tilt_panel = gh.BoundarySurfaces(addTiltSurface(roofs, ang))
            roofs.append(tilt_panel)
            print (tilt_panel)
        return roofs
    except Exception as e:
        raise RuntimeError(f"Something went wrong while handling buildings: {e}")

def data_maker(period):
    required_hours = [] 
    if period: 
        monthly_hours = (744 , 672, 744 , 720, 744, 720, 744, 744, 720, 744, 720, 744 )
        prev_index = 0
        for month in range(12) : 
            required_hours.append(list(range(prev_index, monthly_hours[month] + prev_index)))
            prev_index += monthly_hours[month]
        required_hours = list_to_tree(required_hours)
    return required_hours

roofs, pv_data_pack, period_hoys = None, None, None
try:
    
    # handel default values 
    ang = 0 if angle_ == None else angle_
    period = False if monthly_period is None else monthly_period
    
    # handel primary data 
    locationInfo, locationData = epw_open(_EPW_file)
    latitude, longitude,timezone = locationData
    solar_elevation_angle = cal_elevation(latitude, longitude,timezone) if ang > 0 else 0
    
    # output
    roofs = roof_picker(_buildings,ang)
    pv_data_pack = json.dumps({
        "locationInfo": locationInfo,
        "spacing" : (solar_elevation_angle, ang),
        "period" : f"{ 'yearly' if not period else 'monthly'}"
    })
    period_hoys = None if not period else data_maker(period)

except Exception as e:
    ghc.add_warning(f"{e}")


