from __future__ import division
import sys, os
import copy
import time
import codecs
import json
import salome
import salome_notebook

# from PyQt5 import QtGui, QtCore, QtWidgets
# (FILENAME, fileType) = QtWidgets.QFileDialog.getOpenFileName(None,
#                             'Salome Script - Choose File', '.',
#                             'Json Data File (*.json)')

FILENAME = r'/home/jesusbill/Dev-Projects/github.com/Jesusbill/ifc2ca/ifc2ca.json'
# FILENAMESALOME = r'/home/jesusbill/Dev-Projects/github.com/Jesusbill/ifc2ca/inputDataCA_Salome.json'

# Read data from input file
with open(FILENAME) as dataFile:
    data = json.load(dataFile)

units = data['units']
elements = data['elements']
mesh = data['mesh']
supports = data['supports']

meshSize = mesh['meshSize']

dec = 7  # 4 decimals for length in mm
tol = 10**(-dec-3+1)

tolLoc = tol*10*2

salome.salome_init()
theStudy = salome.myStudy
notebook = salome_notebook.NoteBook(theStudy)

#################    Functions    #################
def makeLine(pl):
    '''Function to define a Line from
        a polyline (list of 2 points)'''

    (x, y, z) = pl[0]
    P1 = geompy.MakeVertex(x, y, z)
    (x, y, z) = pl[1]
    P2 = geompy.MakeVertex(x, y, z)

    return geompy.MakeLineTwoPnt(P1, P2)

def makePoint(pl):
    '''Function to define a Point from
        a polyline (list of 1 point)'''

    (x, y, z) = pl
    return geompy.MakeVertex(x, y, z)

def getGroupName(name):
    if len(name) <= 24:
        return name
    else:
        info = name.split('|')
        return str(info[0][:24 - len(info[1]) - 1] + '_' + info[1])

#####################################################

###
### GEOM component
###
import GEOM
from salome.geom import geomBuilder
import math
import SALOMEDS

gg = salome.ImportComponentGUI('GEOM')
geompy = geomBuilder.New(theStudy)

O = geompy.MakeVertex(0, 0, 0)
OX = geompy.MakeVectorDXDYDZ(1, 0, 0)
OY = geompy.MakeVectorDXDYDZ(0, 1, 0)
OZ = geompy.MakeVectorDXDYDZ(0, 0, 1)
geompy.addToStudy( O, 'O' )
geompy.addToStudy( OX, 'OX' )
geompy.addToStudy( OY, 'OY' )
geompy.addToStudy( OZ, 'OZ' )

buildElements_1D = []
buildElements_1D.extend(elements)

buildElements = []
buildElements.extend(buildElements_1D)

### Define entities ###
start_time = time.time()
print ('Defining Object Geometry')
init_time = start_time

lineObjs = [None for _ in range(len(buildElements_1D))]
# For each straightLine object
for i,line in enumerate(buildElements_1D):
    # Make line
    lineObjs[i] = makeLine(line['geometry'])
    geompy.addToStudy(lineObjs[i], getGroupName(str(line['ifcName'])))

lineSetObj = geompy.MakePartition(lineObjs, [], [], [], geompy.ShapeType["EDGE"], 0, [], 1)
geompy.addToStudy(lineSetObj, 'lines')

pointObjs = [None for _ in range(len(supports))]
# For each straightLine object
for i,point in enumerate(supports):
    # Make point
    pointObjs[i] = makePoint(point['geometry'])
    geompy.addToStudy(pointObjs[i], getGroupName(str(point['ifcName'])))

# pointSetObj = geompy.MakePartition(pointObjs, [], [], [], geompy.ShapeType["EDGE"], 0, [], 1)
# geompy.addToStudy(pointSetObj, 'points')

# Make assemble of Building Object
bldObjs = []
bldObjs.extend(lineObjs)
bldObjs.extend(pointObjs)

bldComp = geompy.MakePartition(bldObjs, [], [], [], geompy.ShapeType["EDGE"], 0, [], 1)
geompy.addToStudy(bldComp, 'bldComp')

elapsed_time = time.time() - init_time
init_time += elapsed_time
print ('Building Geometry Defined in %g sec' % (elapsed_time))

for i,line in enumerate(buildElements_1D):
    # Make line
    lineObjs[i] = geompy.GetInPlace(bldComp, lineObjs[i])
    geompy.addToStudyInFather(bldComp, lineObjs[i], getGroupName(str(line['ifcName'])))

for i,point in enumerate(supports):
    # Make point
    pointObjs[i] = geompy.GetInPlace(bldComp, pointObjs[i])
    geompy.addToStudyInFather(bldComp, pointObjs[i], getGroupName(str(point['ifcName'])))

lineSetObj = geompy.GetInPlace(bldComp, lineSetObj)
geompy.addToStudyInFather(bldComp, lineSetObj, 'lines')

# pointSetObj = geompy.GetInPlace(bldComp, pointSetObj)
# geompy.addToStudyInFather(bldComp, pointSetObj, 'points')

elapsed_time = time.time() - init_time
init_time += elapsed_time
print ('Building Geometry Groups Defined in %g sec' % (elapsed_time))

###
### SMESH component
###

import SMESH
from salome.smesh import smeshBuilder
from salome.StdMeshers import StdMeshersBuilder

print ('Defining Mesh Components')

smesh = smeshBuilder.New(theStudy)
Mesh_1 = smesh.Mesh(bldComp)
Regular_1D = Mesh_1.Segment()
Local_Length_1 = Regular_1D.LocalLength(meshSize, None, tolLoc)

isDone = Mesh_1.Compute()

## Set names of Mesh objects
smesh.SetName(Regular_1D.GetAlgorithm(), 'Regular_1D')
smesh.SetName(Local_Length_1, 'Local_Length_1')
# smesh.SetName(NETGEN_2D_ONLY.GetAlgorithm(), 'NETGEN_2D_ONLY')
# smesh.SetName(NETGEN_2D_Pars, 'NETGEN_2D_Pars')
# smesh.SetName(Quadrangle_2D.GetAlgorithm(), 'Quadrangle_2D')
# smesh.SetName(Quadrangle_Pars, 'Quadrangle Parameters_1')
smesh.SetName(Mesh_1.GetMesh(), 'bldMesh')

elapsed_time = time.time() - init_time
init_time += elapsed_time
print ('Meshing Operations Completed in %g sec' % (elapsed_time))

# Define groups in Mesh

for i,line in enumerate(buildElements_1D):
    tempgroup = Mesh_1.GroupOnGeom(lineObjs[i], getGroupName(str(line['ifcName'])), SMESH.EDGE)
    smesh.SetName(tempgroup, getGroupName(str(line['ifcName'])))

for i,point in enumerate(supports):
    tempgroup = Mesh_1.GroupOnGeom(pointObjs[i], getGroupName(str(point['ifcName'])), SMESH.NODE)
    smesh.SetName(tempgroup, getGroupName(str(point['ifcName'])))

tempgroup = Mesh_1.GroupOnGeom(lineSetObj, 'lines', SMESH.EDGE)
smesh.SetName(tempgroup, 'lines')

elapsed_time = time.time() - init_time
init_time += elapsed_time
print ('Mesh Groups Defined in %g sec' % (elapsed_time))

if salome.sg.hasDesktop():
    salome.sg.updateObjBrowser(1)
    # salome.sg.updateObjBrowser()

elapsed_time = init_time - start_time
print ('ALL Operations Completed in %g sec' % (elapsed_time))
