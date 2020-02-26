## IFC2CA

This `json` file contains the basic information needed to define a structural model and perform a gravity analysis under its own weight. This schema is used to understand the data needed so that they cna be identified in an `ifc` file. The latest schema of the extracted file is constantly changing, the interested user can see the respective file in each example.

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
- `loads`: An Array of loads applied on the structure
  - `fx`/`fy`/`fz`: force in x, y, z global directions
  - `mx`/`my`/`mz`: moment in x, y, z global directions
- `loadCases`: An Array of load cases, which are groups of loads within the same condition (i.e. permanent, accidental, seismic, etc)
  - `load`: reference to the load (load id)
  - `multiplier`: multiplier of the load in the load case
- `loadCaseCombinations`: An Array of load case combinations, which are groups of load cases
  - `loadCase`: reference to the load case (load case id)
  - `multiplier`: multiplier of the load case in the load case combination

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
                "youngModulus": 2.1e08,
                "poissonRatio": 0.2,
                "massDensity": 7.8
            },
            "section": {
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
            "name": "Support001",
            "geometryType": "point",
            "geometry": [0, 0, 0],
            "appliedCondition": {
                "dx": true,
                "dy": true,
                "dz": true,
                "drx": true,
                "dry": true,
                "drz": true
            }
        }
    ],
    "loads": [
        {
            "name": "Load001",
            "geometryType": "straightLine",
            "geometry": [
                [0 , 0, 0],
                [3, 0, 0]
            ],
            "appliedLoad": {
                "fx": 0,
                "fy": 0,
                "fz": -2,
                "mx": 0,
                "mx": 0,
                "mx": 0
            }
        },
        {
            "name": "Load002",
            "geometryType": "point",
            "geometry": [2, 0, 0],
            "appliedLoad": {
                "fx": 0,
                "fy": 0,
                "fz": -5,
                "mx": 0,
                "mx": 0,
                "mx": 0
            }
        }
    ],
    "loadCases": [
        {
            "name": "LoadCase001",
            "loads": [
                {
                    "load": "Load001",
                    "multiplier": 1
                }
            ]
        },
        {
            "name": "LoadCase002",
            "loads": [
                {
                    "load": "Load002",
                    "multiplier": 1
                }
            ]
        }
    ],
    "loadCaseCombinations": [
        {
            "name": "LoadCaseCombination001",
            "loadCases": [
                {
                    "loadCase": "LoadCase001",
                    "multiplier": 1.3
                },
                {
                    "loadCase": "LoadCase002",
                    "multiplier": 1.5
                }
            ]
        }
    ]
}
```
