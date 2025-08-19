# -*- coding: utf-8 -*-
"""
Created on Fri Aug 15 12:36:24 2025

@author: Vicon-OEM
"""

# file of all report generator page settings
class KinPageSettings:
    def __init__(self):
        # kinematics settings
        self.LeftAngleNames = ['LeftTrunkTilt','LeftTrunkObliquity', 'LeftTrunkRotation', 
                          'LeftPelvicTilt', 'LeftPelvicObliquity', 'LeftPelvicRotation',
                          'LeftHipFlexExt', 'LeftHipAbAdduct', 'LeftHipRotation',
                          'LeftKneeFlexExt', 'LeftKneeValgVar', 'LeftKneeRotation',
                          'LeftDorsiPlanFlex', 'LeftFootProgression', 'LeftFootRotation']
        
        self.RightAngleNames = ['RightTrunkTilt','RightTrunkObliquity', 'RightTrunkRotation', 
                          'RightPelvicTilt', 'RightPelvicObliquity', 'RightPelvicRotation',
                          'RightHipFlexExt', 'RightHipAbAdduct', 'RightHipRotation',
                          'RightKneeFlexExt', 'RightKneeValgVar', 'RightKneeRotation',
                          'RightDorsiPlanFlex', 'RightFootProgression', 'RightFootRotation']
        
        self.AngleTitles =    ['Trunk Tilt','Trunk Obliquity', 'Trunk Rotation', 
                          'Pelvic Tilt', 'Pelvic Obliquity', 'Pelvic Rotation',
                          'Hip Flexion-Extension', 'Hip Ab/Adduction', 'Hip Rotation',
                          'Knee Flexion-Extension', 'Knee Varus/Valgus', 'Knee Rotation',
                          'Ankle Plantar-Dorsiflexion', 'Foot Progression', 'Ankle Rotation']
        
        self.AnglesYLabels =   ['Ant-Post', 'Up-Down', 'Int-Ext', 
                          'Ant-Post', 'Up-Down', 'Int-Ext', 
                          'Flex-Ext', 'Add-Abd', 'Int-Ext', 
                          'Flex-Ext', 'Var-Val', 'Int-Ext', 
                          'Dors-Plnt', 'Int-Ext', 'Int-Ext']
        
        self.AngleUpperLimit = [40,15,45,
                           40,15,45,
                           60,15,45,
                           80,30,15,
                           30,45,45]
        
        self.AngleLowerLimit = [-10,-15,-30,
                           -10,-15,-30,
                           -15,-15,-30,
                           -20,-30,-60,
                           -45,-45,-30]
        
        self.YAxisTickLabels = [[-10,0,10,20,30,40],[-15,-10,-5,0,5,10,15],[-30,-15,0,15,30,45],
                           [-10,0,10,20,30,40],[-15,-10,-5,0,5,10,15],[-30,-15,0,15,30,45],
                           [-15,0,15,30,45,60],[-15,-10,-5,0,5,10,15],[-30,-15,0,15,30,45],
                           [-20,0,20,40,60,80],[-30,-20,-10,0,10,20,30],[-60,-45,-30,-15,0,15],
                           [-45,-30,-15,0,15,30],[-45,-30,-15,0,15,30,45],[-30,-15,0,15,30,45]]
        
        self.YLabelOffsetsXTop = [-2,-3,-3,
                             -2,-3,-3,
                             -2,-3,-3,
                             -2,-3,-3,
                             -2,-3,-3]
        
        self.YLabelOffsetsYTop = [33.5,11.5,35,
                             33.5,11.5,35,
                             50.0,11.5,35,
                             67.0,23.5,5,
                             20.0,35.0,35]
        
        self.YLabelOffsetsXBottom = [-2,-0.5,-3,
                                -2,-0.5,-3,
                                -2,-3.0,-3,
                                -2,-3.0,-3,
                                -2,-3.0,-3]
        
        self.YLabelOffsetsYBottom = [-7,-13.5,-25.0,
                                -7,-13.5,-25.0,
                                -10,-13.5,-25.0,
                                -14,-27.5,-55.0,
                                -40,-39.5,-25.0]
        
        self.AnglesUnitLabels = ["Degrees","Degrees","Degrees","Degrees","Degrees"]
        
class SagittalKinPageSettings:
    def __init__(self):
        # sagittal kinetics page settings
        self.LeftSagittalKineticsNames = ['LeftTrunkTilt','', '', 
                                     'LeftPelvicTilt', '', '',
                                     'LeftHipFlexExt', 'LeftKneeFlexExt', 'LeftDorsiPlanFlex',
                                     'LeftHipFlexExtMoment', 'LeftKneeFlexExtMoment', 'LeftDorsiPlanFlexMoment',
                                     'LeftHipFlexExtPower', 'LeftKneeFlexExtPower', 'LeftDorsiPlanFlexPower']
        
        self.RightSagittalKineticsNames = ['RightTrunkTilt','', '', 
                                      'RightPelvicTilt', '', '',
                                      'RightHipFlexExt', 'RightKneeFlexExt', 'RightDorsiPlanFlex',
                                      'RightHipFlexExtMoment', 'RightKneeFlexExtMoment', 'RightDorsiPlanFlexMoment',
                                      'RightHipFlexExtPower', 'RightKneeFlexExtPower', 'RightDorsiPlanFlexPower']
        
        self.SagittalKineticsTitles =    ['Trunk Tilt','', '', 
                                     'Pelvic Tilt', '', '',
                                     'Hip Flexion-Extension', 'Knee Flexion-Extension', 'Ankle Plantar-Dorsiflexion',
                                     'Hip Moment', 'Knee Moment', 'Ankle Moment',
                                     'Hip Power (Sagittal)', 'Knee Power (Sagittal)', 'Ankle Power (Sagittal)']
        
        self.SagittalKineticsYLabels =   ['Ant-Post', '-', '-', 
                                     'Ant-Post', '-', '-', 
                                     'Flex-Ext', 'Flex-Ext', 'Dors-Plnt', 
                                     'Ext-Flex', 'Ext-Flex', 'Ext-Flex', 
                                     'Gen-Abs', 'Gen-Abs', 'Gen-Abs']
        
        self.SagittalKineticsUpperLimit = [40,15,45,
                                      40,15,45,
                                      60,80,30,
                                      2,2,2,
                                      3,3,7]
        
        self.SagittalKineticsLowerLimit = [-10,-15,-30,
                                      -10,-15,-30,
                                      -15,-20,-45,
                                      -1,-1,-1,
                                      -2,-2,-2]
        
        self.SagittalKineticsYAxisTickLabels = [[-10,0,10,20,30,40],[],[],
                                           [-10,0,10,20,30,40],[],[],
                                           [-15,0,15,30,45,60],[-20,0,20,40,60,80],[-45,-30,-15,0,15,30],
                                           [-1,0,1,2],[-1,0,1,2],[-1,0,1,2],
                                           [-2,-1,0,1,2,3],[-2,-1,0,1,2,3],[-2,-1,0,1,2,3]]
        
        self.SagittalKineticsYLabelOffsetsXTop = [-2,0,0,
                                             -2,0,0,
                                             -2,-2,-2,
                                             -2,-2,-2,
                                             -2,-2,-2]
        
        self.SagittalKineticsYLabelOffsetsYTop = [33.5,0,0,
                                             33.5,0,0,
                                             50.0,67.0,20.0,
                                             1.5,1.5,1.5,
                                             2.5,2.5,2.5]
        
        self.SagittalKineticsYLabelOffsetsXBottom = [-2,0,0,
                                                -2,0,0,
                                                -2,-2,-2,
                                                -2,-2,-2,
                                                -2,-2,-2]
        
        self.SagittalKineticsYLabelOffsetsYBottom = [-7,0,0,
                                                -7,0,0,
                                                -10,-14,-40,
                                                -0.7,-0.7,-0.7,
                                                -1.7,-1.7,-1.7]
        
        
        self.SagittalKineticsUnitLabels = ["Degrees","Degrees","Degrees","Nm/kg","Watts/kg"]
        
class CoronalKinPageSettings:
    def __init__(self):
        # coronal kinetics page settings
        self.LeftCoronalKineticsNames = ['LeftTrunkObliquity','', '', 
                                     'LeftPelvicObliquity', '', '',
                                     'LeftHipAbAdduct', 'LeftKneeValgVar', '',
                                     'LeftHipAbAdductMoment', 'LeftKneeValgVarMoment', 'LeftFootAbAdductMoment',
                                     'LeftHipAbAdductPower', 'LeftKneeValgVarPower', '']
        
        self.RightCoronalKineticsNames = ['RightTrunkObliquity','', '', 
                                     'RightPelvicObliquity', '', '',
                                     'RightHipAbAdduct', 'RightKneeValgVar', '',
                                     'RightHipAbAdductMoment', 'RightKneeValgVarMoment', 'RightFootAbAdductMoment',
                                     'RightHipAbAdductPower', 'RightKneeValgVarPower', '']
        
        self.CoronalKineticsTitles =    ['Trunk Obliquity','', '', 
                                     'Pelvic Obliquity', '', '',
                                     'Hip Ab/Adduction', 'Knee Varus/Valgus', '',
                                     'Hip Moment', 'Knee Moment', 'Ankle Moment',
                                     'Hip Power (Coronal)', 'Knee Power (Coronal)', '']
        
        self.CoronalKineticsYLabels =   ['Up-Down', '-', '-', 
                                     'Up-Down', '-', '-', 
                                     'Add-Abd', 'Var-Val', '-', 
                                     'Abd-Add', 'Abd-Add', 'Abd-Add', 
                                     'Gen-Abs', 'Gen-Abs', '-']
        
        self.CoronalKineticsUpperLimit = [15,15,45,
                                      15,15,45,
                                      15,30,45,
                                      2,2,2,
                                      3,3,3]
        
        self.CoronalKineticsLowerLimit = [-15,-15,-30,
                                      -15,-15,-30,
                                      -15,-30,-30,
                                      -1,-1,-1,
                                      -2,-2,-2]
        
        self.CoronalKineticsYAxisTickLabels = [[-15,-10,-5,0,5,10,15],[],[],
                                           [-15,-10,-5,0,5,10,15],[],[],
                                           [-15,-10,-5,0,5,10,15],[-30,-20,-10,0,10,20,30],[],
                                           [-1,0,1,2],[-1,0,1,2],[-1,0,1,2],
                                           [-2,-1,0,1,2,3],[-2,-1,0,1,2,3],[]]
        
        self.CoronalKineticsYLabelOffsetsXTop = [-3,0,0,
                                            -3,0,0,
                                            -3,-3,-3,
                                            -2,-2,-2,
                                            -2,-2,-2]
        
        self.CoronalKineticsYLabelOffsetsYTop = [11.5,0,0,
                                            11.5,0,0,
                                            11.5,23.5,35.0,
                                            1.5,1.5,1.5,
                                            2.5,2.5,2.5]
        
        self.CoronalKineticsYLabelOffsetsXBottom = [-0.5,0,0,
                                               -0.5,0,0,
                                               -3,-3,-3,
                                               -2,-2,-2,
                                               -2,-2,-2]
        
        self.CoronalKineticsYLabelOffsetsYBottom = [-13.5,0,0,
                                               -13.5,0,0,
                                               -13.5,-27.5,-39.5,
                                               -0.7,-0.7,-0.7,
                                               -1.7,-1.7,-1.7]
        
        self.CoronalKineticsUnitLabels = ["Degrees","Degrees","Degrees","Nm/kg","Watts/kg"]
        
class MuscleLengthVelocityPageSettings:
    def __init__(self):
        # coronal kinetics page settings
        self.LeftMuscleLengthVelocityNames = ['LeftTrunkTilt','','',
                                'LeftPelvicTilt','LeftIlioPsoasLength','LeftRectFemLength',
                                'LeftHipFlexExt','LeftMedHamstringLength','LeftLatHamstringLength',
                                'LeftKneeFlexExt','LeftMedHamstringVelocity','LeftLatHamstringVelocity',
                                'LeftDorsiPlanFlex', 'LeftGastrocLength','LeftSoleusLength']
        
        self.RightMuscleLengthVelocityNames = ['RightTrunkTilt','','',
                                'RightPelvicTilt','RightIlioPsoasLength','RightRectFemLength',
                                'RightHipFlexExt','RightMedHamstringLength','RightLatHamstringLength',
                                'RightKneeFlexExt','RightMedHamstringVelocity','RightLatHamstringVelocity',
                                'RightDorsiPlanFlex', 'RightGastrocLength','RightSoleusLength']
        
        self.MuscleLengthVelocityTitles =    ['Trunk Tilt','', '', 
                          'Pelvic Tilt', 'IlioPsoas Length (Normalized)', 'Rectus Femoris Length (Norm.)',
                          'Hip Flexion-Extension', 'Med Hamstrings Length (Norm.)','Lat Hamstrings Length (Norm.)',
                          'Knee Flexion-Extension', 'Med Hamstrings Velocity (Norm.)','Lat Hamstrings Velocity (Norm.)',
                          'Ankle Plantar-Dorsiflexion', 'Gastrocnemius Length (Norm.)','Soleus Length (Normalized)',]
        
        self.MuscleLengthVelocityYLabels =   ['Ant-Post', '-', '-', 
                          'Ant-Post', '-', '-', 
                          'Flex-Ext', '-', '-', 
                          'Flex-Ext', '-', '-', 
                          'Dors-Plnt', '-', '-']
        
        self.MuscleLengthVelocityUpperLimit = [ 40,1.2,1.2,
                                   40,1.1,1.15,
                                   60,1.1,1.1,
                                   80,2,2,
                                   30,1.1,1.1,]
        
        self.MuscleLengthVelocityLowerLimit = [-10,0.8,0.8,
                                  -10,0.9,0.9,
                                  -15,0.9,0.9,
                                  -20,-2,-2,
                                  -45,0.9,0.9]
                           
        self.MuscleLengthVelocityYAxisTickLabels = [[-10,0,10,20,30,40],[0.8,0.9,1.0,1.1,1.2],[0.8,0.9,1.0,1.1,1.2],
                                       [-10,0,10,20,30,40],[0.9,0.95,1.0,1.05,1.1],[0.9,0.95,1.0,1.05,1.1,1.15],
                                       [-15,0,15,30,45,60],[0.9,0.95,1.0,1.05,1.1],[0.9,0.95,1.0,1.05,1.1],
                                       [-20,0,20,40,60,80], [-2,-1,0,1,2], [-2,-1,0,1,2],
                                       [-45,-30,-15,0,15,30],[0.9,0.95,1.0,1.05,1.1],[0.9,0.95,1.0,1.05,1.1]]
        
        self.MuscleLengthVelocityYLabelOffsetsXTop = [-2,-2,-2,
                                         -2,-2,-2,
                                         -2,-2,-2,
                                         -2,-2,-2,
                                         -2,-2,-2]
        
        self.MuscleLengthVelocityYLabelOffsetsYTop = [33.5,1.14,1.14,
                                         33.5,1.30,1.14,
                                         50.0,1.14,1.14,
                                         67.0,1.4,1.4,
                                         20.0,1.14,1.14,]
        
        self.MuscleLengthVelocityYLabelOffsetsXBottom = [-2,-2,-2,
                                             -2,-2,-2,
                                             -2,-2,-2,
                                             -2,-2,-2,
                                             -2,-2,-2]
        
        self.MuscleLengthVelocityYLabelOffsetsYBottom = [-7,0.84,0.84,
                                            -7,0.86,0.84,
                                            -10,0.84,0.84,
                                            -14,-1.6,-1.6,
                                            -40.5,0.84,0.84,]          
        
        self.MuscleLengthVelocityUnitLabels = ["Degrees","Degrees","Degrees","Degrees","Degrees"]
        
class FootKinematicsPageSettings:
    def __init__(self):
        self.LeftFootAngleNames = ['LeftHindFootTilt','LeftHindFootObliquity','LeftForeFootTilt',
                            'LeftDorsiPlanFlex', '', 'LeftFootProgression',  
                            'LeftAnkleComplexDorsiPlanFlex','LeftAnkleComplexValgVar','LeftAnkleComplexRotation', 
                            'LeftMidFootDorsiPlanFlex','LeftMidFootSupPron','LeftMidFootAbAdduct',
                            'LeftHalDorsiPlanFlex', 'LeftSupination', 'LeftHalValgVar']

        self.RightFootAngleNames = ['RightHindFootTilt','RightHindFootObliquity','RightForeFootTilt',
                            'RightDorsiPlanFlex', '', 'RightFootProgression',  
                            'RightAnkleComplexDorsiPlanFlex','RightAnkleComplexValgVar','RightAnkleComplexRotation', 
                            'RightMidFootDorsiPlanFlex','RightMidFootSupPron','RightMidFootAbAdduct',
                            'RightHalDorsiPlanFlex', 'RightSupination', 'RightHalValgVar']

        self.FootAngleTitles =    ['Hindfoot Tilt','Hindfoot Obliquity','Forefoot Tilt',
                              'Ankle Plantar-Dorsiflexion', '', 'Foot Progression',
                              'AnkleComplex Plnt-Dorsiflexion','AnkleComplex Varus/Valgus', 'AnkleComplex Rotation', 
                              'MidfootComplex Flex-Extension','MidfootComplex Inv/Eversion', 'MidfootComplex Ab/Adduction',
                              '1st MTP Flexion-Extension', 'Supination Index', '1st MTP Varus-Valgus']

        self.FootAnglesYLabels =   ['Dors-Plnt','Var-Val','Dors-Plnt', 
                          'Dors-Plnt', '-', 'Int-Ext',
                          'Dors-Plnt', 'Var-Val', 'Int-Ext', 
                          'Dors-Plnt', 'Inv-Ev', 'Add-Abd', 
                          'Dors-Plnt', 'Sup-Pro', 'Var-Val']

        self.FootAngleUpperLimit = [90,30,60,
                           30,45,45,
                           45,30,45,
                           15,30,45,
                           90,30,45]

        self.FootAngleLowerLimit = [-90,-30,-180,
                               -45,-30,-45,
                               -30,-30,-45,
                               -60,-30,-45,
                               -30,-30,-45]
                           
        self.FootYAxisTickLabels = [[-90,-60,-30,0,30,60,90],[-30,-15,0,15,30],[-180,-120,-60,0,60],
                               [-45,-30,-15,0,15,30],[-30,-15,0,15,30,45],[-45,-30,-15,0,15,30,45],
                               [-30,-15,0,15,30,45],[-30,-15,0,15,30],[-45,-30,-15,0,15,30,45],
                               [-60,-45,-30,-15,0,15],[-30,-15,0,15,30],[-45,-30,-15,0,15,30,45],
                               [-30,0,30,60,90],[-30,-15,0,15,30],[-45,-30,-15,0,15,30,45]]

        self.FootYLabelOffsetsXTop = [-2,-3,-3,
                             -2,-3,-3,
                             -2,-3,-3,
                             -2,-3,-3,
                             -2,-2,-3]

        self.FootYLabelOffsetsYTop = [70.0,22.5,30.0,
                                 20.0,35.0,34.5,
                                 35.0,22.5,34.5,
                                 04.5,22.5,34.5,
                                 72.5,22.5,34.5]

        self.FootYLabelOffsetsXBottom = [-2,-3,-3,
                                -2,-3,-3,
                                -2,-3.0,-3,
                                -2,-3.0,-3,
                                -2,-3.0,-3]

        self.FootYLabelOffsetsYBottom = [-80,-25.0,-160,
                                    -40.5,-25.0,-40.5,
                                    -25.5,-25.5,-40.5,
                                    -55.0,-25.5,-40.5,
                                    -17.5,-25.5,-40.5]

        self.FootAnglesUnitLabels = ["Degrees","Degrees","Degrees","Degrees","Degrees"]
        
class EMGpageSettings:
    def __init__(self):
        self.LeftEMGNames = ['LeftRawLRectFem','LeftRawLVastLat', 'LeftRawLMedHams', 'LeftRawLGasTroc', 'LeftRawLTibAnte']

        self.RightEMGNames = ['RightRawRRectFem','RightRawRVastLat', 'RightRawRMedHams', 'RightRawRGasTroc', 'RightRawRTibAnte']

        self.NormEMGEnvelopeNames = ['RectFemEnvelope','VastLatEnvelope', 'MedHamsEnvelope', 'GasTrocEnvelope', 'TibAnteEnvelope']

        self.NormEMGOffsets = [0.06,0.08,0.2,0.12,0.3]

        self.EMGTitles =    ['Rectus Femoris','Vastus Lateralis', 'Medial Hamstrings', 'Gastrocnemius', 'Tibialis Anterior']

        self.EMGUpperLimit = [5,5,5,
                         5,5,5,
                         5,5,5,
                         5,5,5,
                         5,5,5]

        self.EMGLowerLimit = [-5,-5,-5,
                         -5,-5,-5,
                         -5,-5,-5,
                         -5,-5,-5,
                         -5,-5,-5]

        self.EMGYAxisTickLabels = [[-5,-2,0,2,5],[-5,-2,0,2,5],[-5,-2,0,2,5],
                              [-5,-2,0,2,5],[-5,-2,0,2,5],[-5,-2,0,2,5],
                              [-5,-2,0,2,5],[-5,-2,0,2,5],[-5,-2,0,2,5],
                              [-5,-2,0,2,5],[-5,-2,0,2,5],[-5,-2,0,2,5],
                              [-5,-2,0,2,5],[-5,-2,0,2,5],[-5,-2,0,2,5]]

        ## Based on Typical Data from SLC, GRN, SPO
        self.EMGOnOffBarStart =  [[0,52,93,0],   # Rectus Femoris
                                 [0,85,0,0],    # Vastus Lateralis
                                 [0,85,0,0],    # MedialHamstrings
                                 [5,0,0,0],    # Gastrocnemius
                                 [0,57,0,0]]    # Tibialis Anterior

        self.EMGOnOffBarEnd =    [[14,75,100,0], # Rectus Femoris
                                 [23,100,0,0],  # Vastus Lateralis
                                 [30,100,0,0],   # MedialHamstrings
                                 [53,0,0,0],    # Gastrocnemius
                                 [11,100,0,0]]  # Tibialis Anterior

        #Reference- Gazendam 2007- Averaged EMG profiles in jogging and running at different speeds
        self.RunEMGOnOffBarStart =  [[0,40,80,0],   # Rectus Femoris
                             [0,80,0,0],    # Vastus Lateralis
                             [6,70,0,0],    # MedialHamstrings
                             [0,86,0,0],    # Gastrocnemius
                             [27,0,0,0]]    # Tibialis Anterior

        self.RunEMGOnOffBarEnd =    [[15,70,100,0], # Rectus Femoris
                             [15,100,0,0],  # Vastus Lateralis
                             [30,100,0,0],  # MedialHamstrings
                             [25,100,0,0],  # Gastrocnemius
                             [100,0,0,0]]   # Tibialis Anterior