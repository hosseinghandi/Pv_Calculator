"""Grasshopper Script Instance"""
import System
import Rhino
import Grasshopper

import rhinoscriptsyntax as rs
import ghpythonlib.component as ghc
import json

class MyComponent(Grasshopper.Kernel.GH_ScriptInstance):
    def RunScript(self,
            module_efficiency: float,
            module_length: float,
            module_width: float,
            module_capacity: float):
        # Component metadata
        ghenv.Component.Name = 'PV_configurator'
        ghenv.Component.NickName = 'PV_configurator'
        ghenv.Component.Category = 'PV_panel'
        ghenv.Component.Description = 'Configure custom photovoltaic (PV) module properties.'
        
        # Input descriptions
        ghenv.Component.Params.Input[0].Description = 'Module efficiency (0–1)'
        ghenv.Component.Params.Input[1].Description = 'Module length (m)'
        ghenv.Component.Params.Input[2].Description = 'Module width (m)'
        ghenv.Component.Params.Input[3].Description = 'Module capacity (Wp)'
        
        # Output description
        ghenv.Component.Params.Output[0].Description = 'PV system data'

        def validateInputs(eff : float, cap: float, width :float, length : float):
            errors = []
            message = ""
            
            if cap is None and eff is None:
                errors.append("Either module efficiency or module capacity must be provided.")
            if width is None or length is None:
                errors.append("Length and width are required.")
            if eff is not None and (eff <= 0 or eff > 0.30):
                errors.append(f"Efficiency seems incorrct got {eff}.")    
            if width is not None and width <= 0:
                errors.append("Module width must be greater than 0.")

            if length is not None and length <= 0:
                errors.append("Module length must be greater than 0.")
            if errors:
                numbered_errors = [ (f"{i +1 }-{err}") for i, err in enumerate(errors) ]
                message = (
                        "\nRequired Inputs Missing:\n"
                        + "\n".join(numbered_errors)
                        + "\n\nPlease check the follwoing inputs' error."
                    )
                raise RuntimeError(message)




        def calc_system(eff : float, cap: float, width :float, length : float):
            # power (kWp) = 1 kW/m2 * area * efficiency
            area = width * length
            if cap is None:
                cap = area * eff * 1000
            elif eff is None:
                eff = cap / (area  * 1000)
            
            return eff, cap

        def check_Feasibility(eff : float, cap: float, width :float, length : float):
            calculated = (round((length * width * eff * 1000), 2))
            if abs(cap - calculated) > 0.1:
                raise ValueError(f"The capacity provided seems not to be correct expected {calculated}W but got {cap}W")

        try :
            validateInputs(module_efficiency, module_capacity, module_width, module_length)
            eff, cap = calc_system(module_efficiency, module_capacity, module_width, module_length)
            
            if module_capacity is not None:
                check_Feasibility(eff , cap, module_width, module_length)
            
            PV_system = json.dumps({
                "eff": (round(eff, 2)),
                "length":module_length,
                "width": module_width, 
                "cap": (round(cap, 2))
            })
        except Exception as e:
            ghc.add_warning(f"{e}")
            PV_system = None
        
        return PV_system


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
