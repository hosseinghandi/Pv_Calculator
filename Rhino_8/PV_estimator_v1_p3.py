"""Grasshopper Script Instance"""
import System
import Rhino
import Grasshopper

import rhinoscriptsyntax as rs
import ghpythonlib.components as gh
import ghpythonlib.component as ghc
from collections import namedtuple
import math 
import json


class MyComponent(Grasshopper.Kernel.GH_ScriptInstance):
    def RunScript(self,
            _roofs: System.Collections.Generic.List[Rhino.Geometry.GeometryBase],
            _points: System.Collections.Generic.List[Rhino.Geometry.Point3d],
            _result: System.Collections.Generic.List[float],
            _pv_data_pack: str,
            _generate_single_building_: bool,
            reduction_coefficient: float,
            PV_system: str):
        # Role of the component:
        # This component plays an important role to wrap all the data and calculate the PV output assumption
        # the workflow here is :
        # Get the result and point on which the simulation has been conducted -> 
        # evalute the roof area and all user inputs to provide required data for the formula of Pv Out calculation ->
        # once you calculate it be ready for any scenario changes ->
        # Provide data based on the user request : ->
        #A) General information 
        #B) Monthly information 
        #C) annual information 
        #d) single building Production information
        
        
        # Description of the inputs
        ghenv.Component.Params.Input[0].Description = 'The geometry of the PV panels'
        ghenv.Component.Params.Input[1].Description = 'The grid of points that is be used to perform the incident radiation analysis.'
        ghenv.Component.Params.Input[2].Description = 'The result(s) from the simulation is needed'
        ghenv.Component.Params.Input[3].Description = 'The pv-data package by (PV_Data_Provider) should be connected here'
        ghenv.Component.Params.Input[4].Description = 'Generating Production for each building (result in KWh/year)'
        ghenv.Component.Params.Input[5].Description = 'The reduction coefficient presents a percentage of the roof that can be used to install PV system considering other obstructs such as AC system device. The default value is set to 50 percentage.' 
        ''
        ghenv.Component.Params.Input[6].Description = "You can define your PV system using the 'PV_system_definer' component."
        "By default, the system is configured with the following values:\nEfficiency: 20%\nPanel Dimensions: 1.75m (length) × 1m (width)\nPV Capacity: 350 Wp"
        
        # Description of the Outputs      
        ghenv.Component.Params.Output[0].Description = 'The result of PV panel installation based on the requested data on KWh/year.'
        
        # Description of component            
        ghenv.Component.Name = 'PV_estimator'
        ghenv.Component.NickName = 'PV_estimator'
        ghenv.Component.Message = '23.5.2025'
        ghenv.Component.Category = 'PV_panel'
        ghenv.Component.Description = 'This component provides final information for user.'

        
        def find_distance(pv_pack ,pv_system):
            # find the distance within PV panels and total area needed for each panel based on the inclination
            tilted_panel_length = 0
            panel_area_required = 0
            distance_within_PV = 0
            # data extraction 
            inclination = pv_pack["spacing"][1]
            spacing = pv_pack["spacing"][0]
            length = pv_system["length"]
            width = pv_system["width"]

            if inclination:
                # check https://www.mdpi.com/1996-1073/14/13/3850 for calcualtion formula information
                distance_within_PV = length*math.sin(math.radians(inclination))/math.tan(math.radians(spacing))
                tilted_panel_length= length * math.cos(math.radians(inclination))
                panel_area_required = (distance_within_PV + tilted_panel_length) * (width)
            else:
                distance_within_PV = 0
                panel_area_required = length * width  
            return tilted_panel_length, panel_area_required, distance_within_PV


        def cal_PV_installation(roofs ,panel_area_required ,distance_within_PV,pv_pack ,pv_system ):
            roofs = list(roofs)
            roofs = roofs[:-1] if distance_within_PV > 0 else roofs
            roofs_area = []
            possible_roofs_installation = []
            possible_panels_installation = [] 
            # pv effective area refers to actual area of the pv panel not the distance it occupies 
            # while pv occupied area refers to total area needed for each single pv including spacing if applied
            pv_effective_area = []
            pv_occupied_area = []
            # if there is just one roof make it list to be able to iterate over it
            # if gh.ListLength(roofs) 
            if gh.ListLength(roofs) == 1:
                roofs = [roofs]

            for i, roof in enumerate(roofs):
                width, length = pv_system["width"], pv_system["length"]
                roof_area = gh.Area(roof)[0]
                roofs_area.append(roof_area)
                possible_roofs_installation.append(roof_area * (reduction_coe))
                possible_panels_installation.append(int((possible_roofs_installation[i] / panel_area_required))) 
                pv_effective_area.append(possible_panels_installation[i] * (length * width)) 
                pv_occupied_area.append(possible_panels_installation[i] * panel_area_required)

            return roofs_area, possible_roofs_installation, possible_panels_installation, pv_effective_area, pv_occupied_area


        def create_PV_layout(roofs,pv_pack ,pv_system):
            pv_pack = json.loads(pv_pack)
            (tilted_panel_length, panel_area_required, distance_within_PV) = find_distance(pv_pack,pv_system)

            (roofs_area, 
            possible_roofs_installation, 
            possible_panels_installation,
            pv_effective_area, pv_occupied_area) = cal_PV_installation(roofs,panel_area_required, distance_within_PV, pv_pack, pv_system)




        def get_Losses(res):
            result_average = gh.Average(res)
            return 1-((abs(max(res) - result_average)/((max(res)+ result_average)/2)) + 0.145)


        def cal_Production(res, pv_effective_area, eff, maxVal) :
            losses = get_Losses(res)
            if isinstance(pv_effective_area, list):
                eff_Area = sum(pv_effective_area)
            else:
                eff_Area = pv_effective_area
            
            return round((eff_Area * float(losses) * float(maxVal) * float(eff)),2)


        def  info_provider_general_yearly(res,pv_effective_area , eff, isinclined):
            if isinclined :
                res = list(res)
                GTI = max(res)
                GHI= res[:-1]
                return cal_Production(GHI,pv_effective_area, eff, GTI)
            else: return cal_Production(res,pv_effective_area, eff, max(res))
            

        def structure_monthly_result(res):
            res = list(res)
            result_corrected_tree = []
            monthly_count = int(len(res) / 12)
            for i in range(12):
                start = i * monthly_count
                end = start + monthly_count
                result_corrected_tree.append(res[start:end])
            return result_corrected_tree


        def info_provider_general_monthly(res,pv_effective_area , eff , isinclined):
            result_corrected_tree = structure_monthly_result(res)
            #in kwh/m2
            monthly_Production = []
            for monthly_ghi in result_corrected_tree:
                maxValue = max(monthly_ghi)
                if isinclined:
                    maxValue = monthly_ghi[-1]
                    monthly_ghi = monthly_ghi[: -1]
                monthly_Production.append(cal_Production(monthly_ghi,pv_effective_area, eff, maxValue))
            return monthly_Production

        def handelProducationValue(prod):
            if prod >= 1000000:
                return f"{prod / 1000000:.2f} GWh/year"

            elif prod >= 1000:
                return f"{prod / 1000:.2f} MWh/year"

            else:
                return f"{prod:.2f} kWh/year"


        def build_summary(
            roofs_area ,
            possible_roofs_installation ,
            pv_effective_area, 
            possible_panels_installation,
            reduction_coe,
            pv_pack, 
            PV_system, 
            maxValue, 
            losses, 
            production, 
            isInclined,
            distance_within_PV
            ):
            
            if (isInclined):
                solarPower = f"The maximum Global Tilted Irradiance:{maxValue:.2f} kWh/m²/year\n"
                spacing = f"PanelTilt Angle: {pv_pack['spacing'][1]}°\nRow Spacing: {distance_within_PV:.2f} m \n" 
            else:
                solarPower = f"The maximum Global Horizontal Irradiance:{maxValue:.2f} kWh/m²/year\n"

            return (
                f"Photovoltaic (PV) System Performance Summary\n\n"
                f"Note: The presented results are based on average system loss assumptions applied uniformly across all evaluated buildings to streamline the assessment process. "
                f"Consequently, these figures may slightly overestimate real-world performance. For more accurate projections, individual building assessments are recommended.\n\n"
                f"{pv_pack['locationInfo']}"
                f"2.PV System Installation Details:\n\n"
                f"Total Rooftop area:{sum(roofs_area):.2f}m².\n"
                f"Reduction coefficient:{reduction_coe * 100}% of total roof area.\n"
                f"Rooftop area utilized :{sum(possible_roofs_installation):.2f}m².\n"
                f"Effective area of the panels: {sum(pv_effective_area):.2f} m²\n"
                f"Number of Installed Panels: {sum(possible_panels_installation)} units\n"
                f"{'' if not isInclined else spacing}"
                f"Panel Dimensions: {PV_system['length']} m × {PV_system['width']} m\n"
                f"Total Installed Capacity: {(sum(possible_panels_installation) * (PV_system['cap'] / 1000)):.2f} kWp\n\n"
                f"3. PV Panel teachnical Specifications:\n"
                f"Panel Capacity: {int(PV_system['cap'])} Wp\n"
                f"Efficiency: {int(PV_system['eff'] * 100)}%\n\n"
                f"Energy production:\n"
                f"{solarPower}"
                f"System losses: {(1 - losses) * 100:.2f}% (average value applied across all buildings).\n"
                f"Estimated Annual Energy Production: {handelProducationValue(production)}.\n"
            )


        def info_provider_single_building(
            roofs, 
            pts , 
            res , 
            pv_effective_area, 
            eff, 
            isInclined):
            Production = []
            # Handle inclined case 
            if isInclined:
                # take out placeholder panel for getting GTI
                res = res[: - 1]
                pts = pts[: - 1]
                roofs = roofs[: - 1]
            # Global max irradiance
            GHI = max(res)
            for i, roof in enumerate(roofs):
                # Extrude roof to capture points
                geo = gh.Extrude(roof, gh.UnitZ(1))
                values = []
                for j, pt in enumerate(pts):
                    if gh.PointInBrep(geo, pt, False) == 1:
                        values.append(res[j])

                if not values:
                    Production.append(0)
                else:
                    Production.append(
                        cal_Production(values, pv_effective_area[i], eff, GHI)
                    )
            return Production


        def checkRequiredInputs(roofs, pts, res, pv_pack):
            errors = []
            message = ""
            if gh.ListLength(res) <= 1 :
                errors.append("Result list is empty or failed to collect.")
            if not roofs or gh.ListLength(roofs) == 0 :
                errors.append("Roof geometry is missing.")
            if not pts or gh.ListLength(pts) < 1:
                errors.append("Analysis points are missing.")
            if not pv_pack :
                errors.append("PV data pack from 'PV_initializer' is required.")
            if reduction_coefficient > 1 or reduction_coefficient == 0 :
                errors.append(f"reduction_coefficient is a value from 0 to 1 which presents but got {reduction_coefficient}.")
            if errors:
                numbered_errors = [ (f"{i+1}-{err}") for i, err in enumerate(errors) ]
                message = (
                        "\nRequired Inputs Missing:\n"
                        + "\n".join(numbered_errors)
                        + "\n\nPlease check the following inputs' error."
                    )
                raise RuntimeError(message)
                
        information = None
        try:
            checkRequiredInputs(_roofs, _points, _result, _pv_data_pack)
            # default values 
            reduction_coe = 0.5 if reduction_coefficient is None else reduction_coefficient  
            # Loading Json and default assignment
            PV_system = {"eff":0.21,"length": 1.564 , "width" : 1.144, "cap": 360} if PV_system is None else json.loads(PV_system)
            pv_pack = json.loads(_pv_data_pack)
            single_pro = False if _generate_single_building_ is None else _generate_single_building_

            (tilted_panel_length, 
            panel_area_required, 
            distance_within_PV) = find_distance(pv_pack,PV_system)

            (roofs_area, possible_roofs_installation, possible_panels_installation,
            pv_effective_area, pv_occupied_area) = cal_PV_installation(_roofs,panel_area_required, distance_within_PV, pv_pack, PV_system)

            isInclined = True if pv_pack["spacing"][1] != 0 else False
            isMonthly = pv_pack["period"] == "monthly" 
            if single_pro:
                if isMonthly : raise RuntimeError("Monthly production calculation is not available for a single building.")
                information = info_provider_single_building(_roofs, _points, _result, pv_effective_area, PV_system["eff"], isInclined)
                
            if not isMonthly and not single_pro:
                production = info_provider_general_yearly(_result,pv_effective_area, PV_system["eff"],isInclined)
                information = build_summary(
                    roofs_area,
                    possible_roofs_installation,pv_effective_area, possible_panels_installation,
                    reduction_coe,
                    pv_pack, 
                    PV_system, 
                    max(_result), 
                    get_Losses(_result), 
                    production, 
                    isInclined,
                    distance_within_PV)
            elif (isMonthly and not single_pro): 
                information = info_provider_general_monthly(_result,pv_effective_area, PV_system["eff"],isInclined)


        except Exception as e:
            ghc.add_warning(f"{e}")
                            
        return information


    # Preview overrides 
    def get_ClippingBox(self):
        return Rhino.Geometry.BoundingBox.Empty

    def DrawViewportWires(self, args):
        pass

    def DrawViewportMeshes(self, args):
        pass

    # Solve overrides 
    def BeforeRunScript(self):
        pass

    def AfterRunScript(self):
        pass
