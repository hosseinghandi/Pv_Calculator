import ghpythonlib.components as gh
import ghpythonlib.component as ghc
import rhinoscriptsyntax as rh 
import math 
import csv
from datetime import datetime, timedelta
from collections import namedtuple
from ghpythonlib.treehelpers import list_to_tree
  
#role : this component takes building geometry, an EPW weather file, 
# and panel inclination to prepare data for solar output calculation.

#decription of the inputs 
ghenv.Component.Params.Input[0].Description = 'Rhino Breps representing for which PV panel output will be calculated. Please make sure that the input is flatten and you are introducing proper geometry (must be solid valid polySurface).'
ghenv.Component.Params.Input[1].Description = 'An _EPW_file path as a string on your system'
ghenv.Component.Params.Input[2].Description = 'Inclination of the PV panels as a number. If you do not indicate inclination, the algorithm recognizes the installation strategy as horizontal.\nThe default value is 0 or horizontal.\n'
'Note: latitude of any location, as rule of thumb, is considered the best inclination. '
ghenv.Component.Params.Input[3].Description = ' Set to "true" if monthly analysis is required. if not inserted, the whole year will be considered by Ladybug'
                        
ghenv.Component.Params.Output[0].Description = 'Picked roof(s) for which PV panel output will be calculated'
ghenv.Component.Params.Output[1].Description = 'This output should be connected to pv_output_calculator.'
                
ghenv.Component.Name = 'PV_initializer'
ghenv.Component.NickName = 'PV_initializer'
ghenv.Component.Category = 'PV_panel'
ghenv.Component.Description = 'This component provides necessary data to proceed with (PV_output_calculator).'
                
#passing data
roofs = []
location_info = []
alt_spacing = []

def epw_open(input_file, ang): 
    #index related to information needed as list
    if(input_file):
    #check the value from EPW file
        with open(input_file, 'r') as epw:
            reader = csv.reader(epw)
            location = next(reader)
            location_data =(location [1] , location [6] , location [7])
            latitude = float(location [6])
            longitude = float(location [7])
            timezone = float(location[8])
            
            # Skip the first 8 lines of EPW file to provie other required information
            for _ in range(7):
                next(reader)
                
            model_year = []
            for row in reader:
                model_year.append(str(row[0]))
            #take necessary info for location, lat and long
            model_year_bounds = str(gh.Bounds(model_year)).split(",")
            location_info.append(
                f"1. Environmental and Geographical:\n\n"
                f"Location: {location_data[0]}\n"
                f"Latitude: {float(location_data[1]):.2f}\n"
                f"Longitude: {float(location_data[2])}\n"
                f"Weather Data Source: EPW file based on model years "
                f"{model_year_bounds[0]}-{model_year_bounds[1]}\n\n"
            )

        def formula_alt(latitude, longitude,timzone):
            date_time = datetime(2024, 12, 31, 12, 0, 0) 
            lat_rad = math.radians(latitude)
            # Day of the year
            N = date_time.timetuple().tm_yday
            # Solar Declination (δ)
            delta = 23.45 * math.sin(math.radians((360 / 365) * (N - 81)))
            # Hour Angle (γ)
            Lstm = 15 * float(timzone)
            TC1 = 4*(longitude-Lstm)
            B = math.radians((360 / 365) * (N - 81))
            EOT = 9.87 * math.sin(2 * B) - 7.53 * math.cos(B) - 1.5 * math.sin(B)
            TC = TC1 + EOT
            LT = 12 # winter December 21 at solar noon 
            LST = LT + (TC / 60)
            gamma = 15 * (LST - 12)
            
            # Solar Elevation Angle (α)
            alt_spacing.append((
                math.degrees(math.asin(
                    math.sin(lat_rad) * math.sin(math.radians(delta)) +
                    math.cos(lat_rad) * math.cos(math.radians(delta)) * math.cos(math.radians(gamma))
                )),
                ang
            ))

    if ang > 0:
        formula_alt(latitude, longitude, timezone)
    else: 
        alt_spacing.append((0,0))

def roof_picker(BUI,ang):
    for brep in BUI:
        dec = gh.DeconstructBrep(brep)
        for i in range(len(dec[0])):
            cent = gh.Area(dec[0][i])[1]
            norm = gh.EvaluateSurface((dec[0][i]) ,cent)[1]
            if norm[2]==1:
                if cent[2] > 0 :
                    roofs.append(dec[0][i])
            if norm[2]==-1 and cent[2] > 0:
                roofs.append(dec[0][i])
    if ang > 0:
        if len(BUI) == 1:
            cen = gh.ConstructPoint(0,0,max(gh.Deconstruct(gh.Area(roofs)[1])) + 20) 
        else:
            cen = gh.ConstructPoint(0,0,max(gh.Deconstruct(gh.Area(roofs)[1])[2]) + 20)

        plane = gh.Rectangle(cen, 2, 2, 0)[0]
        ax = gh.Explode(plane, True)[0][0]
        tiltPlane= gh.RotateAxis(plane, gh.Radians(ang), ax)[0]
        roofs.append(gh.BoundarySurfaces(tiltPlane))

def data_maker(period):
    required_hours = [] 
    if period: 
        monthly_hours = (744 , 672, 744 , 720, 744, 720, 744, 744, 720, 744, 720, 744 )
        prevIndx = 0
        for month in range(12) : 
            required_hours.append(list(range(prevIndx, monthly_hours[month] + prevIndx)))
            prevIndx += monthly_hours[month]
        required_hours = list_to_tree(required_hours)
    return required_hours

monthly_period = False if monthly_period is None else monthly_period
period_hoys = data_maker(monthly_period)
pv_data_pack = location_info,alt_spacing


def main():
    # inputs' value 
    angel = 0 if angle_ == None else angle_
    input_file = ghc.add_error('_EPW_file is failed to collect data!') if _EPW_file == None else _EPW_file
    if gh.ListLength(_buildings) == 0 :
        ghc.add_warning('The input _building is failed to collect data or there is a problem with inserted Geometry!') 
    else :
        epw_open(input_file, angel)
        roof_picker(_buildings,angel)

main()
