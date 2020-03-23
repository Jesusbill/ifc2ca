# ifc2ca
Files and scripts for the use of Code_Aster in IFC-driven FEM analyses within the ifcOpenShell/BlenderBim Project

### File Organisation
#### Scripts:
- [`ifc2ca.py`](ifc2ca.py): a python script to extract and create the `json` file from an `ifc` file. This file will be synchronized with the one in [`BlenderBIM`](https://github.com/IfcOpenShell/IfcOpenShell/tree/v0.6.0/src/ifcblenderexport/ifc2ca.py)
- [`scriptSalome.py`](scriptSalome.py): a python script to run in the Salome_Meca environment. Creates the geometry and the mesh of the structure
- [`scriptCodeAster.py`](scriptCodeAster.py): a python script to create the input file (`.comm`) for Code_Aster

---

#### Examples
- [`cantilever_01`](examples/cantilever_01) (model created by Dion Moult)
- [`beam_01`](examples/beam_01) (model created by Tandeep Singh)
- [`portal_01`](examples/portal_01) (model created by buildingSmart)
- [`building-frame_01`](examples/building-frame_01) (model created by Tandeep Singh)
- [`building_01`](examples/building_01) (model created by Tandeep Singh)

All example folders contain the following files:

Input
- `{example_name}.json`: json data file of the example
- `bldMesh.med`: mesh file exported from Salome_Meca after executing `scriptSalome`
- `CA_input_00.comm`: command file generated from `scriptCodeAster`

Output
- `result.mess`: message log file of the interpreted commands in Code_Aster
- `result.rmed`: result file on the mesh of the structure to visualize in Salome_Meca

---

### Current Status
_As of 22/02/20:_
- Added beam and building examples
- Added support for I sections and calculation of section properties if not provided (assuming fillet radius is zero)
- Added support for surface members (shells)
- Refactored the `ifc2ca.py` script
- Added support for rigid links
- Added advanced meshing script to correctly simulate connections and independent meshing of structural elements (no common nodes)

_As of 26/02/20:_
- Added portal example
- Changed `section` to `profile` and added I profile
- Modified material and profile schema with mechanical and common properties
- Added geometry identification for point connection from representation
- Added connections along with supports based on the number of elements a connection is applied to
- Applied conditions with elastic stiffness values is still not implemented. Only True/False values are accepted.

_As of 09/02/20:_
- Loads, load cases and load case combinations added in the example `inputDataCA.json` file
- Implementation in BlenderBIM under way

 ![note](examples/cantilever_01/cantileverBeamProblemDescription.png)

_As of 16/01/20:_
- Only line geometries for structural elements and point geometries for supports are considered
- The structure is analysed for gravity loads with a single linear static analysis
