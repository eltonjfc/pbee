#!/bin/python3
# Written by Elton Chaves

from shutil import which
import os, glob

def configure_pbee():
    PbeePATH = os.getcwd()
    
    # ---
    condition = os.path.isdir(PbeePATH)
    if condition is False:
        print(f'error: invalid PbeePATH\n'); exit()
    else:
        return PbeePATH

def configure_basemodels(PbeePATH):
    condition = os.path.isdir(f'{PbeePATH}/basemodels')
    if condition is True:
        basemodels = [
            f'{PbeePATH}/basemodels/base_model_LinearRegression.pkl',
            f'{PbeePATH}/basemodels/base_model_ElasticNet.pkl',
            f'{PbeePATH}/basemodels/base_model_SVR.pkl',
            f'{PbeePATH}/basemodels/base_model_DecisionTreeRegressor.pkl',
            f'{PbeePATH}/basemodels/base_model_KNeighborsRegressor.pkl',
            f'{PbeePATH}/basemodels/base_model_AdaBoostRegressor.pkl',
            f'{PbeePATH}/basemodels/base_model_BaggingRegressor.pkl',
            f'{PbeePATH}/basemodels/base_model_RandomForestRegressor.pkl',
            f'{PbeePATH}/basemodels/base_model_ExtraTreesRegressor.pkl',
            f'{PbeePATH}/basemodels/base_model_XGBRegressor.pkl']
        for item in basemodels:
            if os.path.isfile(item) is True:
                continue
            else:
                print(f' requirement not found: {os.path.basename(item)}\n'); exit()
        return basemodels
    else:
        print(f' requirements not found\n'); exit()

def configure_sl(PbeePATH):
    superlearner = f'{PbeePATH}/super_learner_model.pkl'
    condition = os.path.isfile(superlearner)
    if condition is False:
        print(f' requirement not found: super_learner_model.pkl\n'); exit()
    else:
        return superlearner

def requirements():
    RosettaPATHS = ['ROSETTA3', 'ROSETTA3_BIN', 'ROSETTA3_TOOLS']
    count = 0
    for item in RosettaPATHS:
        condition = os.environ.get(item)
        if condition is None:
            print(f' error (rosetta_path): {item} is not an environment variable.\n')
            count += 1; continue
    if count == 0:
        b1 = glob.glob(f'{os.environ["ROSETTA3_BIN"]}/score_jd2.default.*')[0]
        b2 = glob.glob(f'{os.environ["ROSETTA3_BIN"]}/rosetta_scripts.default.*')[0]
        b3 = f'{os.environ["ROSETTA3_TOOLS"]}/protein_tools/scripts/clean_pdb.py'
        b4 = f'{os.environ["ROSETTA3"]}/external/DAlpahBall/DAlphaBall.gcc'
        requirements = [b1, b2, b3, b4]
        for item in requirements:
            condition = istool(item)
            if condition is False:
                print(f' error: requirement not found -> {item}\n'); exit()
    else:
        exit()

def istool(tool):
    return which(tool) is not None
