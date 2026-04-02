# Pv_Calculator
**Parametric PV production analysis tool for Grasshopper/Rhino with multi-scenario performance evaluation.**

<img width="1314" height="742" alt="Workflow Diagram" src="https://github.com/user-attachments/assets/5f2f8263-5a3c-442d-9806-cda198ad3857" />

---

## Overview
This repository presents an **open-access parametric workflow for photovoltaic (PV) energy production assessment in Grasshopper for Rhino**, developed to support **architectural and urban design decision-making during early design stages**.

The workflow is specifically tailored for **architecture, urban planning, and solar-integrated design**, where conventional PV tools often fail to capture:

- 3D spatial complexity
- context-sensitive shadow effects
- urban morphology influence
- fast multi-scenario comparisons

The tool bridges the gap between **simple web-based PV estimators** and **highly technical simulation platforms** by combining:

- minimal essential inputs
- built-in default values for rapid use
- advanced customization for expert users
- spatially precise urban shading analysis
- worldwide applicability through EPW weather files
- open Python-based development for research extensibility

Built on **Grasshopper + Ladybug + custom Python components**, the workflow enables designers and researchers to evaluate PV rooftop potential under complex urban conditions.

---

## Outputs
The tool supports multiple output scales, including:

- **Annual production**
- **Monthly production**
- **Single-building results**
- **Neighborhood-scale quick assessments**
- **Rapid scenario testing** by changing key variables such as:
  - PV system properties
  - roof reduction factor
  - tilt angle
  - energy demand
  - system efficiency

Once the radiation simulation is completed, **scenario analysis becomes extremely fast**, allowing efficient design exploration.

---

## Quick Start Guide

Start by opening the example file, then adjust the inputs based on the workflow steps described below.

### 1. Provide the required inputs
- Load the **EPW weather file**
- Connect the **3D building geometry**
- Set the **PV tilt angle**
- Choose **annual or monthly analysis**

### 2. Initialize the project
Run the **`PV_initializer`** component.

This step will:
- validate the geometry
- extract climate data
- prepare roof surfaces for simulation

### 3. Run the solar simulation
- Connect optional surrounding **context geometry**
- Switch the **Boolean toggle to `True`**
- Ladybug calculates **rooftop solar radiation**

### 4. Define the PV system
Set:
- panel dimensions
- efficiency
- nominal power
- reduction coefficient
- optional building energy demand

### 5. Calculate PV production
Run the **`PV_estimator`** component.

Choose the desired output:
- quick overall result
- single-building production
- monthly production profile

### 6. Review the results
Use the outputs to:
- review annual and monthly energy yield
- compare building-level performance
- support early-stage design decisions
- test multiple design scenarios quickly

---

## Main Features
-  Worldwide weather compatibility via EPW
-  Urban shading-aware rooftop analysis
- Fast scenario comparison
-  Single-building and district scale outputs
-  Open Python workflow
-  Grasshopper-native
-  Ladybug-integrated
-  Monthly and annual production outputs

---

## Research Purpose
This tool is developed as a **research-oriented open workflow** to improve the accessibility of PV simulations for architects and urban designers, while maintaining sufficient technical depth for advanced users and researchers.

---

## Citation and Project Use
If you use this tool in research, publications, teaching, or professional projects, please cite the repository and kindly inform the author.

**Author:** Hossein Ghandi  

Feedback, case studies, and derived applications are highly appreciated and help support future development of the workflow.
