import os, glob
from pbee import print_infos, print_end
from shutil import which

def configure_pbee():
    PbeePATH = '/home/elton/Documents/bioinfo-tools/python/pbee'
    
    # ---
    superlearner = f'{PbeePATH}/basemodels/super_learner_model.pkl' 
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

    # ---
    condition = os.path.isdir(f'{PbeePATH}/basemodels')
    if condition is True:
        for item in basemodels:
            if os.path.isfile(item) is True:
                continue
            else:
                print_infos(f'requirement not found: {os.path.basename(item)}', type='none'); print_end()
        if os.path.isfile(superlearner) is False:
            print_infos(f'requirement not found: super_learner_model.pkl', type='none'); print_end()
    else:
        print_infos(f'error: invalid PbeePATH (configure.py, line 6)', type='none'); print_end()
    return PbeePATH, basemodels, superlearner

def requirements():
    RosettaPATHS = ['ROSETTA3', 'ROSETTA3_BIN', 'ROSETTA3_TOOLS']
    count = 0
    for item in RosettaPATHS:
        condition = os.environ.get(item)
        if condition is None:
            print_infos(message=f'error (rosetta_path): {item} has not been defined as an environment variable.', type='none')
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
                print_infos(message=f'error: requirement not found -> {item}', type='none'); print_end()
    else:
        print_end()

def istool(tool):
    return which(tool) is not None
