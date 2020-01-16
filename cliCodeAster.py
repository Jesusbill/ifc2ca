from __future__ import division
import json
import codecs

FILENAME = r'/home/jesusbill/Dev-Projects/github.com/Jesusbill/ifc2ca/inputDataCA.json'
# FILENAMESALOME = r'/media/jesusbill/DATA/Dropbox/Aether/Aetherium3/dataSalome.json'
FILENAMEASTER = r'/home/jesusbill/Dev-Projects/github.com/Jesusbill/ifc2ca/CA_input_00.comm'
# FILENAMEEXCEL = r'/media/jesusbill/DATA/Dropbox/Aether/Aetherium3/test01.xlsx'
# FILENAME = r'D:\Dropbox\Aether\Aetherium3/data.json'
# FILENAMESALOME = r'D:\Dropbox\Aether\Aetherium3/dataSalome.json'
# FILENAMEASTER = r'D:\Dropbox\Aether\Aetherium3/CA_test01_input_02.comm'
# FILENAMEEXCEL = r'D:\Dropbox\Aether\Aetherium3/test01.xlsx'


###################################################################
#######################     CONTAINER 4     #######################
###################################################################

def createCommFile():

    AccelOfGravity = 9.806 # m/sec^2

    # Read data from input file
    with open(FILENAME) as dataFile:
        data = json.load(dataFile)

    units = data['units']
    elements = data['elements']
    mesh = data['mesh']
    restraints = data['restraints']

    buildElements_1D = []
    buildElements_1D.extend(elements)

    buildElements = []
    buildElements.extend(buildElements_1D)

    # Define file to write command file for code_aster
    f = open(FILENAMEASTER, 'w')

    f.write('# Command file generated for ifcOpenShell/BlenderBim\n')
    f.write('# Aether Engineering - www.aethereng.com\n')
    f.write('\n')

    f.write('# Linear analysis with beam elements\n')

    f.write(
'''
# STEP: INITIALIZE STUDY
DEBUT(
    PAR_LOT = 'OUI',
)
'''
    )

    f.write(
'''
# STEP: READ MED FILE
mesh = LIRE_MAILLAGE(
    FORMAT = 'MED'
)
'''
    )

    f.write(
'''
# STEP: DEFINE MODEL
model = AFFE_MODELE(
    MAILLAGE = mesh,
    AFFE = (
        _F(
            TOUT = 'OUI',
            PHENOMENE = 'MECANIQUE',
            MODELISATION = '3D'
        ),
        _F(
            GROUP_MA = 'lines',
            PHENOMENE = 'MECANIQUE',
            MODELISATION = 'POU_D_E'
        )
    )
)\n
'''
    )


    f.write('# STEP: DEFINE MATERIALS')

    for i,elem in enumerate(buildElements):
        template = \
'''
{matNameID} = DEFI_MATERIAU(
    ELAS = _F(
        E = {E},
        NU = {NU},
        RHO = {RHO}
    )
)
'''

        context = {
            'matNameID': 'matF'+ '_%s' % i,
            'E': float(elem['material']['E']),
            'NU': float(elem['material']['NU']),
            'RHO': float(elem['material']['RHO'])
        }

        f.write(template.format(**context))


    f.write(
'''
material = AFFE_MATERIAU(
    MAILLAGE = mesh,
    AFFE = ('''
    )

    for i,elem in enumerate(buildElements):

        template = \
        '''
        _F(
            GROUP_MA = '{group_name}',
            MATER = {matNameID},
        ),'''

        context = {
            'group_name': str(elem['name']),
            'matNameID': 'matF'+ '_%s' % i
        }

        f.write(template.format(**context))

    f.write(
'''
    )
)
'''
    )


    f.write(
'''
# STEP: DEFINE ELEMENTS
element = AFFE_CARA_ELEM(
    MODELE = model,
    POUTRE = ('''
    )

    for i,elem in enumerate(buildElements_1D):

        template = \
        '''
        _F(
            GROUP_MA = '{group_name}',
            SECTION = 'RECTANGLE',
            CARA = ('HY', 'HZ'),
            VALE = {sectionDimensions}

        ),'''

        context = {
            'group_name': str(elem['name']),
            'sectionDimensions': (elem['section']['HY'], elem['section']['HZ'])
        }

        f.write(template.format(**context))

    f.write(
'''
    ),
    ORIENTATION = ('''
    )

    for i,elem in enumerate(buildElements_1D):

        template = \
        '''
        _F(
            GROUP_MA = '{group_name}',
            CARA = ('ANGL_VRIL',),
            VALE = {rotation},

        ),'''

        context = {
            'group_name': str(elem['name']),
            'rotation': (elem['rotation'],)
        }

        f.write(template.format(**context))

    f.write(
'''
    )
)\n
'''
    )


    f.write('# STEP: DEFINE GROUND BOUNDARY CONDITIONS')

    f.write(
'''
grdSupps = AFFE_CHAR_MECA(
    MODELE = model,
    DDL_IMPO = ('''
    )

    for i,restraint in enumerate(restraints):
        f.write(
        '''
        _F(
            GROUP_NO = '%s',''' % (str(restraint['name']))
        )
        for dof in restraint['input']:
            if restraint['input'][dof]:
                f.write(
        '''
            %s = 0,''' % (str(dof))
                )
        f.write(
        '''
        ),'''
        )
    f.write(
    '''
    )
)'''
    )


    template = \
'''
# STEP: DEFINE LOAD
exPESA = AFFE_CHAR_MECA(
    MODELE = model,
    PESANTEUR = _F(
        GRAVITE = {AccelOfGravity},
        DIRECTION = (0.,0.,-1.),
    ),
)
'''
    context = {
        'AccelOfGravity': AccelOfGravity,
    }

    f.write(template.format(**context))


    f.write(
'''
# STEP: RUN ANALYSIS
res_Bld = MECA_STATIQUE(
    MODELE = model,
    CHAM_MATER = material,
    CARA_ELEM = element,
    EXCIT = (
        _F(
            CHARGE = grdSupps,
        ),
        _F(
            CHARGE = exPESA,
        )
    )
)
'''
    )


#     f.write(
# '''
# # STEP: POST-PROCESSING
# res_Bld = CALC_CHAMP(
#     reuse = res_Bld,
#     RESULTAT = res_Bld,
#     CONTRAINTE = ('SIEF_ELNO', 'SIGM_ELNO', 'EFGE_ELNO',),
#     FORCE = ('REAC_NODA', 'FORC_NODA',),
# )
# '''
#     )
#
#     template = \
# '''
# # STEP: MASS EXTRACTION FOR EACH ASSEMBLE
# FaceMass = POST_ELEM(
# 	TITRE = 'TotMass',
#     MODELE = model,
#     CARA_ELEM = element,
#     CHAM_MATER = material,
#     MASS_INER = _F(
#         GROUP_MA = {massList},
#     ),
# )\n'''
#
#     context = {
#         'massList': massList,
#     }
#
#     f.write(template.format(**context))
#
#     f.write(
# '''
# IMPR_TABLE(
#     UNITE = 10,
# 	TABLE = FaceMass,
#     SEPARATEUR = ',',
#     NOM_PARA = ('LIEU', 'MASSE', 'CDG_X', 'CDG_Y', 'CDG_Z'),
# 	# FORMAT_R = '1PE15.6',
# )
# '''
#     )
#
#     f.write(
# '''
# # STEP: REACTION EXTRACTION AT THE BASE
# Reacs = POST_RELEVE_T(
#     ACTION = _F(
#         INTITULE = 'sumReac',
#         GROUP_NO = 'grdSupps',
#         RESULTAT = res_Bld,
#         NOM_CHAM = 'REAC_NODA',
#         RESULTANTE = ('DX','DY','DZ',),
#         # MOMENT = ('DRX','DRY','DRZ',),
#         # POINT = (0,0,0,),
#         OPERATION = 'EXTRACTION',
#     ),
# )
# '''
#     )
#
#     f.write(
# '''
# IMPR_TABLE(
#     UNITE = 10,
#     TABLE = Reacs,
#     SEPARATEUR = ',',
#     NOM_PARA = ('INTITULE', 'RESU', 'NOM_CHAM', 'INST', 'DX','DY','DZ'),
#     # FORMAT_R = '1PE12.3',
# )
# '''
#     )
#
    f.write(
'''
# STEP: DEFORMED SHAPE EXTRACTION
IMPR_RESU(
    FORMAT = 'MED',
	UNITE = 80,
	RESU = _F(
 		RESULTAT = res_Bld,
 		NOM_CHAM = ('DEPL',), # 'REAC_NODA', 'FORC_NODA',
 		NOM_CHAM_MED = ('Bld_DISP',), #  'Bld_REAC', 'Bld_FORC',
    ),
)
'''
    )

    f.write(
'''
# STEP: CONCLUDE STUDY
FIN()
'''
    )

    f.close()
