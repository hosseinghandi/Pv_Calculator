import rhinoscriptsyntax as rs
import ghpythonlib.components as gh
import ghpythonlib.component as ghc
from collections import namedtuple
import math 

#Inputs 
ghenv.Component.Params.Input[0].Description = 'The geomtery of the PV panels'
ghenv.Component.Params.Input[1].Description = 'The grid of points that is be used to perform the incident radiation analysis.'
ghenv.Component.Params.Input[2].Description = 'The result(s) from the simulation is needed'
ghenv.Component.Params.Input[3].Description = 'The pv-data package by (PV_Data_Provide) should be connected here'
ghenv.Component.Params.Input[4].Description = 'Generating producation for each building (result in KWh/year)'
ghenv.Component.Params.Input[5].Description = 'The reduction coefficient presents a percentage of the roof that can be used to install PV system considering other obstructs such as AC system device. The default value is set to 50 percentage.' 
''
ghenv.Component.Params.Input[6].Description = "You can define your PV system using the 'PV_system_definer' component."
"By default, the system is configured with the following values:\nEfficiency: 20%\nPanel Dimensions: 1.75m (length) × 1m (width)\nPV Capacity: 350 Wp"
ghenv.Component.Params.Input[7].Description = 'Total energy consumpation in(KWh) of the buildings on which the pv panel are installed to calculate the energy compensentation.'
#Output       
ghenv.Component.Params.Output[0].Description = 'The result of PV panel installation based on the requested data on KWh/year.'

#componenet introducation 
                
ghenv.Component.Name = 'PV_estimator'
ghenv.Component.NickName = 'PV_estimator'
ghenv.Component.Message = '23.5.2025'
ghenv.Component.Category = 'PV_panel'
ghenv.Component.Description = 'This component provides final information for user.'
                

information = []

def build_summary(PV_PACK, PV_SYSTEM, pv_layout, GTI, losses, production, energy_compensation):
    return (
        f"Photovoltaic (PV) System Performance Summary\n\n"
        f"Note: The presented results are based on average system loss assumptions applied uniformly across all evaluated buildings to streamline the assessment process. "
        f"Consequently, these figures may slightly overestimate real-world performance. For more accurate projections, individual building assessments are recommended.\n\n"
        f"{PV_PACK.location_info[0]}"
        f"2.PV System Installation Details:\n\n"
        f"Total Rooftop area:{sum(pv_layout.roofs_area):.2f}m².\n"
        f"Reducation coefficient:{PV_PACK.reducation_coe * 100}% of total roof area.\n"
        f"Rooftop area utilized :{sum(pv_layout.possibile_roofs_installation):.2f}m².\n"
        f"Effective area of the panels: {sum(pv_layout.pv_effective_area):.2f} m²\n"
        f"Number of Installed Panels: {sum(pv_layout.possibile_panels_installation)} units\n"
        f"Panel Dimensions: {PV_SYSTEM.length} m × {PV_SYSTEM.width} m\n"
        f"Total Installed Capacity: {(sum(pv_layout.possibile_panels_installation) * (PV_SYSTEM.power_rating / 1000)):.2f} kWp\n\n"
        f"3. PV Panel technical Specifications:\n"
        f"Panel Capacity: {int(PV_SYSTEM.power_rating)} Wp\n"
        f"Efficiency: {int(PV_SYSTEM.module_efficiency * 100)}%\n\n"
        f"Energy production:\n"
        f"The maximum Global Tilted Irradiance(GTI):{GTI:.2f} kWh/m²/year\n"
        f"System losses: {(1 - losses) * 100:.3f}% (average value applied across all buildings).\n"
        f"Estimated Annual Energy Production: {production / 1000000:.3f} GWh/year.\n"
        f"Energy compensation percentage:{energy_compensation}"
    )





def pv_layout(roof,PV_PACK,PV_SYSTEM):
    
    def distance_within_panel(PV_PACK, PV_SYSTEM):
        if PV_PACK.altitude[0][0] != 0:
            LEN = PV_SYSTEM.length
            tilted_panel_length = []
            distance_value = LEN*math.sin(math.radians(PV_PACK.altitude[0][1]))/math.tan(math.radians(PV_PACK.altitude[0][0]))
            
            tilted_panel_length= LEN * math.cos(math.radians(PV_PACK.altitude[0][1]))
            pvTotalAreaNeeded = (distance_value + tilted_panel_length) * (PV_SYSTEM.width)
        else:
            distance_value = 0
            pvTotalAreaNeeded = PV_SYSTEM.width*PV_SYSTEM.length  
  
        return distance_value, pvTotalAreaNeeded
        
    def Pv_installation(roof,distance,PV_PACK,PV_SYSTEM):
        roof= gh.CullIndex(roof,-1,True) if distance[0] > 0 else roof
        roofs_area = []
        possibile_roofs_installation = []
        possibile_panels_installation = [] 
        pv_effective_area = []
        pv_occupied_area = []
        if gh.ListLength(roof) != 1:
            for i in range(len(roof)):
                roofs_area.append((gh.Area(roof[i])[0]))
                possibile_roofs_installation.append((gh.Area(roof[i])[0])*PV_PACK.reducation_coe)
                possibile_panels_installation.append(int((possibile_roofs_installation[i] / distance[1]))) #distance 1 is pv_needed_area
                pv_effective_area.append(possibile_panels_installation[i] * (PV_SYSTEM.width*PV_SYSTEM.length)) # the actual or effective pv area
                pv_occupied_area.append(possibile_panels_installation[i] * distance[1])
        else:
            roofs_area.append((gh.Area(roof)[0]))
            possibile_roofs_installation.append((gh.Area(roof)[0])*PV_PACK.reducation_coe)
            possibile_panels_installation.append(int((possibile_roofs_installation[0]/ distance[1]))) #distance 1 is pv_needed_area
            pv_effective_area.append(possibile_panels_installation[0] * (PV_SYSTEM.width*PV_SYSTEM.length)) # the actual or effective pv area
            pv_occupied_area.append(possibile_panels_installation[0] * distance[1])
            
        return roofs_area, possibile_roofs_installation, possibile_panels_installation, pv_effective_area, pv_occupied_area
    distance = distance_within_panel(PV_PACK, PV_SYSTEM)
    pv_installation_data = Pv_installation(roof,distance,PV_PACK,PV_SYSTEM)

    PV = namedtuple("PV", [
    "spacing_row_distance", 
    "pv_needed_area", 
    "roofs_area", 
    "possibile_roofs_installation",
    "possibile_panels_installation",
    "pv_effective_area",
    "pv_occupied_area"
    ])

    pv = PV(
        distance[0],
        distance[1],
        pv_installation_data[0],
        pv_installation_data[1],
        pv_installation_data[2], 
        pv_installation_data[3], 
        pv_installation_data[4]
    )
    return pv



def info_provider_general (PV_PACK, PV_SYSTEM, RST,enegry_consumption, pv_layout): 
    isinclined = 1 if PV_PACK.altitude[0][0] != 0 else 0
    if isinclined:
        if not (len(RST)/12).is_integer():
            GTI = max(RST)
            GHI= gh.CullIndex(RST, RST.index(GTI),True)
            GHI_MAX = max(GHI)
            result_average = gh.Average(GHI)
            pv_actual_area = sum(pv_layout.pv_effective_area)
            losses = 1-((abs(GHI_MAX - result_average)/((GHI_MAX+ result_average)/2)) + 0.145)
            production = ((pv_actual_area) * float(losses) * float(GTI) * float(PV_SYSTEM.module_efficiency))
            energy_compensation = "N/A" if enegry_consumption is None else round((min(enegry_consumption / production, 1.0)*100),2)
            information.append( build_summary(PV_PACK, PV_SYSTEM, pv_layout, GTI, losses, production, energy_compensation))
        else:
            result_corrected_tree = []
            current_month = 0 
            actual_list = int(len(RST)/12)
            #making proper list 
            for _ in range(12):
                result_corrected_tree.extend([RST[current_month : actual_list+current_month]])
                current_month += actual_list
            #in kwh/m2
            inclined_ghi = []
            horizontal_ghi_max = []
            horizontal_ghi_avg = []
            for monthly_ghi in result_corrected_tree:
                #inclined surface GHI
                inclined_ghi.append(monthly_ghi[-1])
                #recognize the inclined surface and taken out the values to calculate shading loss
                horizontal_ghi_value = monthly_ghi[ : actual_list-1] 
                horizontal_ghi_max.append(max(horizontal_ghi_value))
                horizontal_ghi_avg.append(gh.Average(horizontal_ghi_value))
                
            pv_actual_area = sum(pv_layout.pv_effective_area)
            pv_efficiency= PV_SYSTEM.module_efficiency
            
            for max_ghi_monthly,avg_ghi_monthly in zip(horizontal_ghi_max,horizontal_ghi_avg) :
                losses_monthly = 1-((abs(max_ghi_monthly - avg_ghi_monthly)/
                ((max_ghi_monthly+ avg_ghi_monthly)/2)) + 0.145)
                #in mwh
                information.append(round(pv_actual_area * float(losses_monthly) * 
                float(max_ghi_monthly) * float(pv_efficiency),2)) 
    else:
        if not (len(RST)/12).is_integer():
            GHI_MAX = max(RST)
            result_average = gh.Average(RST)
            pv_actual_area = sum(pv_layout.pv_effective_area)
            losses = 1-((abs(GHI_MAX - result_average)/((GHI_MAX+ result_average)/2)) + 0.145)
            production = ((pv_actual_area) * float(losses) * float(GHI_MAX) * float(PV_SYSTEM.module_efficiency))
            energy_compensation = "N/A" if enegry_consumption is None else  round((min(production / energy_compensation, 1.0)*100),2)

            information.append(build_summary(PV_PACK, PV_SYSTEM, pv_layout, GHI_MAX, losses, production, energy_compensation))
        else:
             #if yes that is monthly request 
            # making the list legibile with GH
            result_corrected_tree = []
            current_month = 0 
            actual_list = int(len(RST)/12)
            #making proper list 
            for _ in range(12):
                result_corrected_tree.extend([RST[current_month : actual_list+current_month]])
                current_month += actual_list
            #in kwh/m2
            horizontal_ghi_max = []
            horizontal_ghi_avg = []
            for monthly_ghi in result_corrected_tree:
                #recognize the inclined surface and taken out the values to calculate shading loss
                horizontal_ghi_value = monthly_ghi[ : actual_list] 
                horizontal_ghi_max.append(max(horizontal_ghi_value))
                horizontal_ghi_avg.append(gh.Average(horizontal_ghi_value))

            total_area =sum(pv_layout.pv_effective_area)
            pv_efficiency= PV_SYSTEM.module_efficiency
            
            for max_ghi_monthly,avg_ghi_monthly in zip(horizontal_ghi_max,horizontal_ghi_avg) :
                losses_monthly = 1-((abs(max_ghi_monthly - avg_ghi_monthly)/
                ((max_ghi_monthly+ avg_ghi_monthly)/2)) + 0.145)
                #in mwh
                information.append(round(total_area * float(losses_monthly) * 
                float(max_ghi_monthly) * float(pv_efficiency),2)) 


def info_provider_single(PV_PACK, RST , PTS , ROF, pv_layout,PV_SYSTEM):
    
    if (len(RST)/12).is_integer():
        ghc.add_error("Single building simualtion is designed for general analysis for a year, hence for monthly it is not possibile")
    else:
        sum_va = []
        isinclined = 1 if PV_PACK.altitude[0][0] != 0 else 0
        #can be improved
        if isinclined:
            GTI = max(RST)
            #eliminate the last item which is the inlined panel
            PTS_corrected, ROF_corrected, RES_corrected= gh.CullIndex(PTS, -1,True) , gh.CullIndex(ROF,-1,True), gh.CullIndex(RST,-1,True)
            for i in ROF_corrected:
                pat = []
                geo= gh.Extrude(i , gh.UnitZ(2))
                value = []
                for pt  in  PTS_corrected:
                    pat.append(gh.PointInBrep( geo , pt , False))
                for y in range(len(pat)):
                    if pat[y] == 1:
                        value.append(RST[y])
                sum_va.append(gh.Average(value))
            GHI=max(RES_corrected)
            if sum_va:
                for x,i in enumerate(sum_va):
                    loss = (abs(GHI - i)/((GHI + i)/2))+.145
                    pv_actual_area = pv_layout.pv_effective_area
                    building_pro = []
                    building_pro.append(int((pv_actual_area[x]) * (abs(loss-1)) * float(GHI) * float(PV_SYSTEM.module_efficiency)))
                    information.append(sum(building_pro))
        else:
            for i in ROF:
                pat = []
                geo= gh.Extrude(i , gh.UnitZ(2))
                value = []
                for pt  in  PTS:
                    pat.append(gh.PointInBrep( geo , pt , False))
                for y in range(len(pat)):
                    if pat[y] == 1:
                        value.append(RST[y])
                sum_va.append(gh.Average(value))
            GHI=max(RST)
            if sum_va:
                for x,i in enumerate(sum_va):
                    loss = (abs(GHI - i)/((GHI + i)/2))+.145
                    pv_actual_area = pv_layout.pv_effective_area
                    building_pro = []
                    building_pro.append(int((pv_actual_area[x]) * (abs(loss-1)) * float(GHI) * float(PV_SYSTEM.module_efficiency)))
                    information.append(sum(building_pro))


def main():
    
    rst = ghc.add_warning('_result is failed to collect data !') if gh.ListLength(_result) == 1 else _result
    geo = ghc.add_warning('_geometry is failed to collect data !') if len(_roofs) == 0 else _roofs
    pts = ghc.add_warning('_points is failed to collect data!') if gh.ListLength(_points) < 1 else _points
    reduction_coe = 0.5 if reduction_coefficient is None else reduction_coefficient/100
    consumption = None if Energy_consumption_total is None else float(Energy_consumption_total)
    single_pro = 0 if _generate_single_building_ is None else _generate_single_building_

    pv_data_pack = ghc.add_warning('_pv_data_pack input  is failed to collect data !') if gh.ListLength(_pv_data_pack) == 0 else _pv_data_pack
    PV_data_pack = namedtuple("data_pack", [
    "location_info","altitude", "reducation_coe"])
    pv_data_pack = PV_data_pack(pv_data_pack[0], pv_data_pack[1], reduction_coe)

    PVSystem = namedtuple("pvSystem", [
        "module_efficiency", "length", "width", "power_rating"
    ])
    
    default_model = PVSystem(0.21, 1.564 , 1.144, 360)
    pvSystem = default_model if PV_system is None else PVSystem(*PV_system)
    
    
    if ((gh.NullItem(rst)[0] != False) and (gh.NullItem(geo)[0]) != False):
        Pv_installation_data = pv_layout(geo,pv_data_pack,pvSystem)
        if (single_pro == 0): 
            info_provider_general (pv_data_pack, pvSystem,rst,consumption,Pv_installation_data)
        else :
            info_provider_single(pv_data_pack, rst , pts , geo, Pv_installation_data,pvSystem)
    else:
        ghc.add_warning('Run the simulation to estimate the producation')


main()






