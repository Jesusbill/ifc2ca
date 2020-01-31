# ifc2ca
Files and scripts for a Proof of Concept regarding the use of Code_Aster in IFC-driven FEM analyses within the ifcOpenShell/BlenderBim Project

### File Organisation
#### Scripts:
- [`ifc2ca.py`](ifc2ca.py): a python script to extract and create the `json` file from an `ifc` file. This file will be synchronized with the one in [`BlenderBIM`](https://github.com/IfcOpenShell/IfcOpenShell/tree/v0.6.0/src/ifcblenderexport)
- [`scriptSalome.py`](scriptSalome.py): a python script to run in the Salome_Meca environment. Creates the geometry and the mesh of the structure
- [`cliCodeAster.py`](cliCodeAster.py): a python cli to create the input file (`.comm`) for Code_Aster. Use `run.py` to facilitate the use

#### Proof of Concept: A cantilever beam under its own weight
###### Input
- [`inputDataCA.json`](inputDataCA.json): json data file of a cantilever beam under its own weight
- [`bldMesh.med`](CodeAsterModel-CantileverBeam/bldMesh.med): mesh file exported from Salome_Meca after executing `scriptSalome`
- [`CA_input_00.comm`](CodeAsterModel-CantileverBeam/CA_input_00.comm): command file generated from `cliCodeAster`

###### Output
- [`result.mess`](CodeAsterModel-CantileverBeam/result.mess): message log file of the interpreted commands in Code_Aster
- [`result.rmed`](CodeAsterModel-CantileverBeam/result.rmed): result file on the mesh of the structure to visualize in Salome_Meca

### Current Status
_As of 16/01/20:_
- Only line geometries for structural elements and point geometries for supports are considered
- The structure is analysed for gravity loads with a single linear static analysis
