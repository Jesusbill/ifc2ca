import json
import ifcopenshell

class IFC2CA:
    def __init__(self, filename):
        self.filename = filename
        self.file = None
        self.result = {}
        self.supports = []

    def convert(self):
        self.file = ifcopenshell.open(self.filename)
        for model in self.file.by_type('IfcStructuralAnalysisModel'):
            self.result = {
                'title': model.Name,
                'units': self.get_units(),
                'elements': self.get_elements(model),
                'mesh': { 'meshSize': 0.2 }, # TODO: unhardcode
                'supports': self.get_supports(),
                'connections': self.get_connections()
            }

            print('Number of elements: ', len(self.result['elements']))
            print('Number of supports: ', len(self.result['supports']))
            print('Number of connections: ', len(self.result['connections']))

    def get_units(self):
        # TODO: unhardcode
        units = {}
        for unit in self.file.by_type('IfcUnitAssignment')[0].Units:
            if unit.UnitType == 'LENGTHUNIT':
                units['length'] = 'm'
        units['force'] = 'N'
        units['angle'] = 'deg'
        return units

    def get_elements(self, model):
        elements = []
        for group in model.IsGroupedBy:
            for element in group.RelatedObjects:
                if not element.is_a('IfcStructuralMember'):
                    continue
                data = self.get_element_data(element)
                if data:
                    elements.append(data)
        return elements

    def get_element_data(self, element):
        if element.is_a('IfcStructuralCurveMember'):
            representation = self.get_representation(element, 'Edge')
            material_profile = self.get_material_profile(element)
            if not representation or not material_profile:
                print(representation, material_profile)
                return
            for connection in element.ConnectedBy:
                if connection.RelatedStructuralConnection:
                    self.supports.append(connection.RelatedStructuralConnection)
            return {
                'ifcName': element.is_a() + '|' + str(element.id()),
                'name': element.Name,
                'id': element.GlobalId,
                'geometryType': self.get_geometry_type(representation),
                'geometry': self.get_geometry(representation),
                'rotation': 0, # TODO: unhardcode
                'material': self.get_material_properties(material_profile.Material),
                'profile': self.get_profile_properties(material_profile.Profile),
                'elementType': 'EulerBeam' # TODO: unhardcode
            }

        elif element.is_a('IfcStructuralSurfaceMember'):
            representation = self.get_representation(element, 'Face')
            material = self.get_material_profile(element)
            if not representation:
                print(representation)
                return
            for connection in element.ConnectedBy:
                if connection.RelatedStructuralConnection:
                    self.supports.append(connection.RelatedStructuralConnection)
            return {
                'ifcName': element.is_a() + '|' + str(element.id()),
                'name': element.Name,
                'id': element.GlobalId,
                'thickness': element.Thickness,
                # 'geometryType': self.get_geometry_type(representation),
                'geometry': self.get_geometry(representation),
                'material': self.get_material_properties(material),
                # 'elementType': 'EulerBeam' # TODO: unhardcode
            }

    def get_supports(self):
        supports = []
        for support in self.supports:
            if support.GlobalId in [s['id'] for s in supports]:
                continue
            if len(support.ConnectsStructuralMembers) != 1:
                continue
            supports.append({
                'ifcName': support.is_a() + '|' + str(support.id()),
                'name': support.Name,
                'id': support.GlobalId,
                'geometryType': self.get_support_geometry_type(support),
                'geometry': self.get_support_geometry(support),
                'appliedCondition': self.get_support_input(support),
                'relatedElements': self.get_support_members(support)
            })
        return supports

    def get_connections(self):
        supports = []
        for support in self.supports:
            if support.GlobalId in [s['id'] for s in supports]:
                continue
            if len(support.ConnectsStructuralMembers) <= 1:
                continue
            supports.append({
                'ifcName': support.is_a() + '|' + str(support.id()),
                'name': support.Name,
                'id': support.GlobalId,
                'geometryType': self.get_support_geometry_type(support),
                'geometry': self.get_support_geometry(support),
                'appliedCondition': self.get_support_input(support),
                'relatedElements': self.get_support_members(support)
            })
        return supports

    def get_support_geometry_type(self, support):
        if support.is_a('IfcStructuralPointConnection'):
            return 'point'

    def get_support_geometry(self, support):
        # TODO: make more robust
        # if support.ObjectPlacement:
        #     return support.ObjectPlacement.RelativePlacement.Location.Coordinates
        representation = self.get_support_representation(support)
        item = representation.Items[0]
        if item.is_a('IfcVertexPoint'):
            return self.get_coordinate(item.VertexGeometry)

    def get_support_input(self, support):
        if support.AppliedCondition:
            return {
                'dx': support.AppliedCondition.TranslationalStiffnessX.wrappedValue,
                'dy': support.AppliedCondition.TranslationalStiffnessY.wrappedValue,
                'dz': support.AppliedCondition.TranslationalStiffnessZ.wrappedValue,
                'drx': support.AppliedCondition.RotationalStiffnessX.wrappedValue,
                'dry': support.AppliedCondition.RotationalStiffnessY.wrappedValue,
                'drz': support.AppliedCondition.RotationalStiffnessZ.wrappedValue
            }
        return None

    def get_support_members(self, support):
        answer = []
        for s in support.ConnectsStructuralMembers:
            if s.is_a('IfcRelConnectsStructuralMember'):
                answer.append({
                    'ifcName': s.is_a() + '|' + str(s.id()),
                    'element': s.RelatingStructuralMember.is_a() + '|' + str(s.RelatingStructuralMember.id()),
                    'geometryPointIndex': None
                })

            if s.is_a('IfcRelConnectsWithEccentricity'):
                answer.append({
                    'ifcName': s.is_a() + '|' + str(s.id()),
                    'element': s.RelatingStructuralMember.is_a() + '|' + str(s.RelatingStructuralMember.id()),
                    'geometryPointIndex': 1 if s.ConnectionConstraint.EccentricityInX < 0 else 2,
                    'linkLength': abs(s.ConnectionConstraint.EccentricityInX)
                })

        return answer

    def get_support_representation(self, element):
        if not element.Representation:
            return None
        for representation in element.Representation.Representations:
            rep = self.get_specific_representation(representation, 'Reference', 'Vertex')
            if rep:
                return rep
        else:
            # print('Trying without rep identifier')
            for representation in element.Representation.Representations:
                rep = self.get_specific_representation(representation, None, 'Vertex')
                if rep:
                    return rep

    def get_representation(self, element, rep_type):
        if not element.Representation:
            return None
        for representation in element.Representation.Representations:
            rep = self.get_specific_representation(representation, 'Reference', rep_type)
            if rep:
                return rep
        else:
            # print('Trying without rep identifier')
            for representation in element.Representation.Representations:
                rep = self.get_specific_representation(representation, None, rep_type)
                if rep:
                    return rep

    def get_specific_representation(self, representation, rep_id, rep_type):
        if representation.RepresentationIdentifier == rep_id \
                and representation.RepresentationType == rep_type:
            return representation
        if representation.RepresentationType == 'MappedRepresentation':
            return self.get_specific_representation(
                representation.Items[0].MappingSource.MappedRepresentation,
                rep_id, rep_type)

    def get_geometry_type(self, representation):
        if representation.Items[0].is_a('IfcEdgeCurve'):
            return 'curvedLine' # TODO: Is this correct?
        return 'straightLine'

    def get_geometry(self, representation):
        # Maybe IfcOpenShell can use create_shape here to simplify this, but
        # supposedly structural models are very simple anyway, so perhaps we
        # can do without it.
        item = representation.Items[0]
        if item.is_a('IfcEdge'):
            return [
                self.get_coordinate(item.EdgeStart.VertexGeometry),
                self.get_coordinate(item.EdgeEnd.VertexGeometry)
            ]

        if item.is_a('IfcFaceSurface'):
            edges = item.Bounds[0].Bound.EdgeList
            coords = []
            for edge in edges:
                coords.append(self.get_coordinate(edge.EdgeElement.EdgeStart.VertexGeometry))
            return coords

    def get_coordinate(self, point):
        if point.is_a('IfcCartesianPoint'):
            return point.Coordinates

    def get_material_profile(self, element):
        if not element.HasAssociations:
            return None
        for association in element.HasAssociations:
            if not association.is_a('IfcRelAssociatesMaterial'):
                continue
            material = association.RelatingMaterial
            if material.is_a('IfcMaterialProfileSet'):
                # For now, we only deal with a single profile
                return material.MaterialProfiles[0]
            if material.is_a('IfcMaterialProfileSetUsage'):
                return material.ForProfileSet.MaterialProfiles[0]
            if material.is_a('IfcMaterial'):
                return material

    def get_material_properties(self, material):
        psets = material.HasProperties

        if self.get_pset_properties(psets, 'Pset_MaterialMechanical'):
            mechProps = self.get_pset_properties(psets, 'Pset_MaterialMechanical')
        else:
            mechProps = self.get_pset_properties(psets, None)

        if self.get_pset_properties(psets, 'Pset_MaterialCommon'):
            commonProps = self.get_pset_properties(psets, 'Pset_MaterialCommon')
        else:
            commonProps = self.get_pset_properties(psets, None)

        return {
            'ifcName': material.is_a() + '|' + str(material.id()),
            'mechProps': mechProps,
            'commonProps':commonProps
        }

    def get_pset_property(self, psets, pset_name, prop_name):
        for pset in psets:
            if pset.Name == pset_name or pset_name is None:
                for prop in pset.Properties:
                    if prop.Name == prop_name:
                        return prop.NominalValue.wrappedValue

    def get_pset_properties(self, psets, pset_name):
        for pset in psets:
            if pset.Name == pset_name or pset_name is None:
                d = {}
                for prop in pset.Properties:
                    propName = prop.Name[0].lower() + prop.Name[1:]
                    d[propName] = prop.NominalValue.wrappedValue
                return d

    def get_profile_properties(self, profile):
        if profile.is_a('IfcRectangleProfileDef'):
            return {
                'ifcName': profile.is_a() + '|' + str(profile.id()),
                'profileType': 'rectangular',
                'profileVariation': 'constant',
                'xDim': profile.XDim,
                'yDim': profile.YDim
            }

        if profile.is_a('IfcIShapeProfileDef'):
            psets = profile.HasProperties
            return {
                'ifcName': profile.is_a() + '|' + str(profile.id()),
                'profileType': 'iSymmetrical',
                'mechProps': self.get_pset_properties(psets, 'Pset_ProfileMechanical'),
                'commonProps': {
                    'flangeThickness': profile.FlangeThickness,
                    'webThickness': profile.WebThickness,
                    'overallDepth': profile.OverallDepth,
                    'overallWidth': profile.OverallWidth,
                    'filletRadius': profile.FilletRadius,
                    'profileName': profile.ProfileName,
                    'profileType': profile.ProfileType
                }
            }

fileName = 'building_01'
ifc2ca = IFC2CA('ifcModels/' + fileName + '.ifc')
ifc2ca.convert()
# print(json.dumps(ifc2ca.result, indent=4))
# with open('ifc2ca.json', 'w') as f:
with open(('ifcModels/' + fileName + '.json') , 'w') as f:
    f.write(json.dumps(ifc2ca.result, indent = 4))
