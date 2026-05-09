<img width="1325" height="741" alt="Workflow" src="https://github.com/user-attachments/assets/be55c28a-24f2-4f00-8ad7-6532fdb63c1c" />

## PV panel ☀️
A parametric workflow for evaluating photovoltaic energy production using Grasshopper, combining climate data with 3D urban geometry.

## Overview and project Goals
This tool is designed for early-stage architectural and urban design. Built as an open-access workflow in Grasshopper, it enables quick and accessible estimation of solar energy potential using simple inputs .The goal was to reduce tedious modeling and complex technical inputs required to evaluate solar panel energy, making the process easier and more accessible.



##  Getting Started
To get started, open the provided example files and follow the included instructions.

## Prerequisites
Before using this workflow, make sure you have the following installed:
 
1. **Rhino 8** 
2. **Ladybug Tools**
3. An **EPW climate file** for your location — download free from [climate.onebuilding.org](https://climate.onebuilding.org)

**instruction** :
1. download this repository
2. Open the `.gh` file in Grasshopper
3. Provide your building or urban geometry as Valid close Brep
4. Connect your EPW climate file to the designated input
5. Set the inclination degree and monthly output if needed — default values are assigned automatically
6. Run the Ladybug simulation and connect the results and analysis points to PV_estimatore
7. Connect your roof geometry to PV_estimatore and set the reduction coefficient if required — default is set to 50%
8. Set PV system parameters if needed — defaults are provided for quick testing
9. To study each building individually, toggle the single building study option 

## Tech 
- Grasshopper (Rhino 3D)
- Python (GHPython scripting)
- Ladybug Tools
- EPW climate data (EnergyPlus Weather format)
 
##  Main Features
- Simplified PV calculation workflow for early-stage design
- Minimal required inputs with built-in default values to reduce setup complexity
- Urban shading analysis using 3D geometry with integrated Ladybug tools
- EPW-based climate data, making it usable worldwide
- Scalable from single buildings to urban-scale analysis
- Fast comparison of multiple scenarios after the initial simulation, reducing repeated heavy computations
  
##  Challenges I Faced
- Simplifying complex PV simulation logic into a user-friendly workflow
- Integrating urban shading and geographic data into an accessible tool for large-scale simulations
- Balancing ease of use with scientific accuracy
- Designing a system that works across different scales, from buildings to urban areas


## 📚 Research Purpose
This tool is developed as a **research-oriented open workflow** to improve the accessibility of PV simulations for architects and urban designers, while maintaining sufficient technical depth for advanced users and researchers.

---

## 🧾Citation and Project Use
If you use this tool in research, publications, teaching, or professional projects, please cite the repository and kindly inform the author.

**Author:**
Hossein Ghandi 🧑‍💻
📧 Email: [ghandih22@email.com](mailto:ghandih22@email.com)

Feedback, case studies, and derived applications are highly appreciated and help support future development of the workflow.
