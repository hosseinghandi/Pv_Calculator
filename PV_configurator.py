#solar_panel= {0: ["Mono-Si" ,1.75]}
import ghpythonlib.component as ghc

                
#decription of the inputs 
ghenv.Component.Params.Input[0].Description = "A rating your module is given to determine how much sunlight it absorbs and converted into usable electricity as percentage"
ghenv.Component.Params.Input[1].Description = 'Module lenfth e.g., 1.1m (unite meter)'
ghenv.Component.Params.Input[2].Description = 'Module width e.g., 1.1m (unite meter)'
ghenv.Component.Params.Input[3].Description = 'The Nominal Maximum Power of PV systems is given in W by manufacturer.'

               
ghenv.Component.Params.Output[0].Description = 'The defined PV system data'
                
ghenv.Component.Name = 'PV_configurator'
ghenv.Component.NickName = 'PV_configurator'
ghenv.Component.Message = '23.5.2025'
ghenv.Component.Category = 'PV_panel'
ghenv.Component.Description = 'This component make an user defined PV system.'
                


PV_system = []

def main():
 

    try:
        if (module_efficiency == None and module_capacity == None):
            raise ValueError("It is necesary to provide either module-efficency or module-capacity.")
            
        module_cap = module_length*module_width*(module_efficiency*1000) if module_capacity is None else module_capacity
        
        module_eff = ((module_cap/1000)/(module_length*module_width)) if module_efficiency is None else module_efficiency
        if module_eff > .30:
            raise ValueError("The module efficency seems too high, Please control the inputs")
        
        if (module_length == None or module_width == None):
            raise ValueError("The dimensions are mandatory")

        if None not in ((module_eff, module_length, module_width, module_cap)):
            lowerbound, biggerbound = module_cap - 10 , module_cap + 10
            modul_cap_calculated = int((module_length*module_width*module_eff)*1000)

            if not (lowerbound <= modul_cap_calculated <= biggerbound):
                raise ValueError("The inputs value are not corrisponding beacuse the dimension and the module efficiency\n"
                "indicate that the module capcaity should be around {} Wp but the input value is {} Wp.".format(
                int(modul_cap_calculated), int(module_cap)))
        
        PV_system.append((round(module_eff,2), module_length, module_width, module_cap))




    except ValueError as e:
        ghc.add_warning(str(e))    

main()