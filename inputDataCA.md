## IFC2CA

This `json` file contains the basic information needed to define a simple cantilever steel beam and perform a gravity analysis under its own weight.

We define a single element in the `elements` Array with thte following properties:
- `geometry`: an Array of arrays of 3D point coordinates [m]
- `rotation`: an angle to rotate the local axes of the element along the X local axis. We can talk if you need more info regarding this orientation in Code_Aster [deg]
 - X local axis is defined as the axis from the first to the second point of the line geometry.
 - Y local axis is defined as the horizontal axis perpendicular to X
 - Z local axis completes the triad
- `material`: properties of an isotropic material
 - `youngModulus`: modulus of elasticity [kPa]
 - `poissonRatio`: poisson ratio [-]
 - `massDensity`: density [ton/m3]
- `section`: properties of a rectangular section
 - `xDim`: length along the Y local axis in Code_Aster [m]
 - `yDim`: length along the Z local axis in Code_Aster [m]
 - `sectionVariation`: `constant` section along the length of the element
- `meshSize`: discretization length of the geometry [m]
- `supports`: an Array of objects to define the supports of the structure
 - `geometryType`: `point` geometry
 - `geometry`: the 3D point coordinates [m]
 - `appliedCondition`: imposed directions (degrees-of-freedom) where there is no displacement/rotation allowed. In this example we support all displacements and directions of the first point of the beam

```json
{
    "title": "My Model",
    "units": {
        "length": "m",
        "force": "N",
        "angle": "deg"
    },
    "elements": [
        {
            "ifcName": "IfcStructuralCurveMember|133",
            "name": "My Beam",
            "id": "0zncXJTUL98AfSMYRuKE89",
            "geometryType": "straightLine",
            "geometry": [
                [
                    0.0,
                    0.0,
                    0.0
                ],
                [
                    3.0,
                    0.0,
                    0.0
                ]
            ],
            "rotation": 0,
            "material": {
                "ifcName": "IfcMaterial|95",
                "materialType": "isotropic",
                "youngModulus": 210000000.0,
                "poissonRatio": 0.2,
                "massDensity": 7.8
            },
            "section": {
                "ifcName": "IfcRectangleProfileDef|102",
                "sectionType": "rectangular",
                "sectionVariation": "constant",
                "xDim": 0.2,
                "yDim": 0.4
            },
            "elementType": "EulerBeam"
        }
    ],
    "mesh": {
        "meshSize": 0.2
    },
    "supports": [
        {
            "ifcName": "IfcStructuralPointConnection|148",
            "name": "Empty",
            "id": "3McamcLqfFVfX$dKFdSJsP",
            "geometryType": "point",
            "geometry": [
                0.0,
                0.0,
                0.0
            ],
            "appliedCondition": {
                "dx": true,
                "dy": true,
                "dz": true,
                "drx": true,
                "dry": true,
                "drz": true
            }
        }
    ]
}
```
