import os, glob
from shutil import which

def configure_pbee():
    PbeePATH = '/home/elton/Documents/bioinfo-tools/python/pbee'
    condition = os.path.isdir(PbeePATH)
    if condition is False:
        print(f'error: invalid PbeePATH (configure.py, line 6)'); exit()
    else:
        return PbeePATH

def configure_basemodels(PbeePATH):
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
    condition = os.path.isdir(f'{PbeePATH}/basemodels')
    if condition is True:
        for item in basemodels:
            if os.path.isfile(item) is True:
                continue
            else:
                print(f' requirement not found: {os.path.basename(item)}'); exit()

def configure_sl(PbeePATH):
    superlearner = f'{PbeePATH}/basemodels/super_learner_model.pkl'
    condition = os.path.isfile(superlearner)
    if condition is False:
        print(f' requirement not found: super_learner_model.pkl'); exit()
    else:
        return superlearner

def requirements():
    RosettaPATHS = ['ROSETTA3', 'ROSETTA3_BIN', 'ROSETTA3_TOOLS']
    count = 0
    for item in RosettaPATHS:
        condition = os.environ.get(item)
        if condition is None:
            print(f' error (rosetta_path): {item} has not been defined as an environment variable.')
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
                print(f' error: requirement not found -> {item}', type='none'); exit()
    else:
        exit()

def istool(tool):
    return which(tool) is not None