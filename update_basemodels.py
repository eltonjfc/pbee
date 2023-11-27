#!/bin/python3
# Written by Elton Chaves

from configure import configure_pbee
import os, gdown

PbeePATH = configure_pbee()
MLmodels = {
    'base_model_AdaBoostRegressor': 	'1opbenrx1hpsqgz2Yr35JH95X1ugfAqYs',
    'base_model_BaggingRegressor': 		'1zZPMffxE5c7-68VObItcabEEzNeINxTN',
    'base_model_DecisionTreeRegressor': '1U4cuyu5WtYfOOyakQ7mD9AMhdwD6wMQY',
    'base_model_ElasticNet': 			'1REy_gMIEDv3Eb4vVJESzflTiJALtsL1p',
    'base_model_ExtraTreesRegressor': 	'1wTSwwTOJD215OLcNSxc3RaDqLELrNarW',
    'base_model_KNeighborsRegressor': 	'1MebrZuxr3fzgBP2SUT4qM8kHMantbcZ0',
    'base_model_LinearRegression': 		'1qL--HrSV5m9JisGvtrM01cPQYhoLbtw9',
    'base_model_RandomForestRegressor': '1yVhQYbUPx-MPWq56KvpZacA8AdaZNMxr',
    'base_model_SVR': 					'1nztm49l-9seM-HfeoJ6tBbIdt2uPVfZy',
    'base_model_XGBRegressor': 			'10CCoMMrdA3VFUj8INjD7Aqcr13HOABjP'}

if not os.path.isdir(f'{PbeePATH}/basemodels'):
    os.mkdir(f'{PbeePATH}/basemodels')

for item in MLmodels:
    url = f'https://drive.google.com/uc?id={MLmodels[item]}'
    out = f'{PbeePATH}/basemodels/{item}.pkl'
    gdown.download(url, out)    
