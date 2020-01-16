## IFC2CA

This `json` file contains the basic information needed to define a simple cantilever steel beam and perform a gravity analysis under its own weight.

We define a single element in the `elements` Array with thte following properties:
- `geometry`: an Array of arrays of 3D point coordinates [m]
- `rotation`: an angle to rotate the local axes of the element along the X local axis. We can talk if you need more info regarding this orientation in Code_Aster [deg]
 - X local axis is defined as the axis from the first to the second point of the line geometry.
 - Y local axis is defined as the horizontal axis perpendicular to X
 - Z local axis completes the triad
- `material`: properties of an isotropic material
 - `E`: modulus of elasticity [kPa]
 - `NU`: poisson ratio [-]
 - `RHO`: density [ton/m3]
- `section`: properties of a rectangular section
 - `HY`: length along the Y local axis [m]
 - `HZ`: length along the Z local axis [m]
 - `sectionVariation`: `constant` section along the length of the element
- `meshSize`: discretization length of the geometry [m]
- `restraints`: an Array of objects to define the supports of the structure
 - `geometryType`: `point` geometry
 - `geometry`: the 3D point coordinates [m]
 - `input`: imposed directions (degrees-of-freedom) where there is no displacement/rotation allowed. In this example we restraint all displacements and directions of the first point of the beam

```json
{
    "title": "Cantilever beam under its own weight",
    "units": {
        "length": "m",
        "force": "kN",
        "angle": "deg"
    },
    "elements": [
        {
            "name": "Beam001",
            "geometryType": "straightLine",
            "geometry": [
                [0 , 0, 0],
                [3, 0, 0]
            ],
            "rotation": 0,
            "material": {
                "materialType": "isotropic",
                "E": 2.1e08,
                "NU": 0.2,
                "RHO": 7.8
            },
            "section": {
                "sectionType": "rectangular",
                "sectionVariation": "constant",
                "HY": 0.2,
                "HZ": 0.4
            },
            "elementType": "EulerBeam"
        }
    ],
    "mesh": {
        "meshSize": 0.2
    },
    "restraints": [
        {
            "name": "Restraint001",
            "geometryType": "point",
            "geometry": [0, 0, 0],
            "input": {
                "DX": true,
                "DY": true,
                "DZ": true,
                "DRX": true,
                "DRY": true,
                "DRZ": true
            }
        }
    ]
}
```
