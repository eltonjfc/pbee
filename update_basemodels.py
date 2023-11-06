from modules.configure import configure_pbee
import os, gdown

PbeePATH = configure_pbee()
MLmodels = {
    'base_model_AdaBoostRegressor': 	'1pNliK5lEy4I-Uc-XVVyS-M4TZPHUb2k2',
    'base_model_BaggingRegressor': 		'1eI_K8Bl44FoAj2xofmpleCyWaFbXdZZO',
    'base_model_DecisionTreeRegressor': '1_A_65Mxnw7CfcuFZjWhLOLqPRZkQjHOm',
    'base_model_ElasticNet': 			'1xwv6psNij8XvetjbIjkcffzILWAiduuf',
    'base_model_ExtraTreesRegressor': 	'1WrqJnUf04-TxyopLthBVdmEsyo3BQpw5',
    'base_model_KNeighborsRegressor': 	'1VcF4CZOr9g1kgBlX5Kd0DArR3O1izXVs',
    'base_model_LinearRegression': 		'1lCA-2HxTiHM3egJ7RLQNrT3Q9AEZjg2r',
    'base_model_RandomForestRegressor': '1b5zY27GXAH6N5Dg_5rMgbG3O2hVBj4bY',
    'base_model_SVR': 					'19_C5_EkbiJNoYPZ8ED6_y1pEna4-uBfa',
    'base_model_XGBRegressor': 			'1ivvaZoUKT85JiqxB3RBen9ys74I0IrG_'}

if not os.path.isdir(f'{PbeePATH}/basemodels'):
    os.mkdir(f'{PbeePATH}/basemodels')

for item in MLmodels:
    url = f'https://drive.google.com/uc?id={MLmodels[item]}'
    out = f'{PbeePATH}/basemodels/{item}.pkl'
    gdown.download(url, out)
