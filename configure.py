#!/bin/python3
# Written by Elton Chaves

from pbee import print_end
from shutil import which
import os, glob

def configure_pbee():
    PbeePATH = os.path.dirname(__file__)
    
    # ---
    condition = os.path.isdir(PbeePATH)
    if condition is False:
        print(' error: invalid PbeePATH'); print_end
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
                print(f' requirement not found: {item}'); print_end()
        return basemodels
    else:
        print(f' requirements not found\n'); exit()

def configure_sl(PbeePATH):
    superlearner = f'{PbeePATH}/super_learner_model.pkl'
    condition = os.path.isfile(superlearner)
    if condition is False:
        print(f' requirement not found: super_learner_model.pkl\n'); print_end()
    else:
        return superlearner

def requirements(PbeePATH):
    RosettaPATHS = ['ROSETTA3', 'ROSETTA3_BIN', 'ROSETTA3_TOOLS']
    count = 0
    for item in RosettaPATHS:
        condition = os.environ.get(item)
        if condition is None:
            print(f' error (rosetta_path): {item} is not an environment variable.\n')
            count += 1; continue
    if count == 0:
        r1 = glob.glob(f'{os.environ["ROSETTA3_BIN"]}/score_jd2.default.*')[0]
        r2 = glob.glob(f'{os.environ["ROSETTA3_BIN"]}/rosetta_scripts.default.*')[0]
        r3 = f'{os.environ["ROSETTA3_TOOLS"]}/protein_tools/scripts/clean_pdb.py'
        r4 = f'{os.environ["ROSETTA3"]}/external/DAlpahBall/DAlphaBall.gcc'
        r5 = f'{PbeePATH}/train_file.csv'
        requirements = [r1, r2, r3, r4, r5]
        for item in requirements:
            condition = istool(item)
            if condition is False:
                print(f' error: requirement not found -> {item}\n'); exit()
    else:
        exit()

def istool(tool):
    return which(tool) is not None