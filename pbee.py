#!/bin/python3
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# Elaborated by Elton Chaves (chavesejf@gmail.com)
# -----------------------------------------------------------------------------------
# Protein Binding Energy Estimator (PBEE)
# Protein Engineering and Biomaterial Modeling Group (BIOMAT)
# Aggeu Magalhaes Institute, Oswaldo Cruz Foundation, Recife-PE, Brazil
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
import os, math, time, shutil, argparse, subprocess
from posix import environ
import pandas as pd
from configure import *
from modules.detect_ions import *
from modules.detect_gaps import *
from modules.rosettaXML import *
from modules.superlearner import *

def pre_processing(pdbfiles):
    """
    
    Parameters:
    -----------
    - pdbfiles ->

    Returns:
    - bad_structures ->
    """
    bad_structures = []
    for mol, pdb in enumerate(pdbfiles):
        basename = os.path.basename(pdb[:-4])
        outdir = f'{args.odir[0]}/pbee_outputs/{basename}'

        # Verifica se o(s) arquivo(s) estão no formato PDB
        condition = ispdb(pdb)
        if condition is not False:
            print_infos(message=f'[{mol}] {pdb}\r', type='structure')
            # cria diretório para armazenar outputs
            if not os.path.isdir(outdir):
                os.makedirs(outdir)
        else:
            print_infos(message=f'invalid PDB file -> {os.path.basename(pdb)}.', type='structure')
            continue

        # 1. verifica se a estrutura contém partner1 e partner2
        # -----------------------------------------------------
        chains = partner_checker(pdb, partner1, partner2)
        if chains[0] <= 1:
            print_infos(message=f'[{mol}] argument error (--partner1/--partner2): chain ID not found ({chains[1]})', type='info')
            bad_structures.append(pdb)
            shutil.rmtree(outdir)
            if len(pdbfiles) == 1:
                print_end()
            else:
                continue
        
        # 2. verifica se a estrutura contém gaps
        # --------------------------------------
        partners = pdbcleaner(pdb, basename, outdir, submit_dir, partner1, partner2)
        gaps = []
        for partner in partners:
            n_gaps = detect_gaps(partner)
            gaps.append(n_gaps)
        total_gaps = 0
        for partner, gap in zip(partners, gaps):
            if gap != 0:
                print_infos(message=f'[{mol}] warning: {gap} gap(s) found -> {os.path.basename(partner)}', type='info')
                total_gaps += gap
        if total_gaps > 0 and force_mode is False:
            bad_structures.append(pdb)
            shutil.rmtree(outdir); continue
    return bad_structures

def post_processing(pdbfiles, partner1, partner2, basemodels, superlearner):
    """
    
    Parameters:
    -----------
    - pdbfiles ->
    - partner1 ->
    - partner2 ->

    Returns:
    
    """
    for mol, pdb in enumerate(pdbfiles):
        basename = os.path.basename(pdb[:-4])
        outdir = f'{args.odir[0]}/pbee_outputs/{basename}'

        # 1. concatena estruturas de partner1 e partner2
        # ----------------------------------------------
        print_infos(message=f'[{mol}] {pdb}', type='protocol')
        partners = [
            f'{outdir}/{basename}_{partner1}.pdb',
            f'{outdir}/{basename}_{partner2}.pdb']
        _pdb = concat_pdbs(outdir, basename, partner1=partners[0], partner2=partners[1])

        # 2. verifica se a estrutura original contém íon(s)
        # se existir, recupera as coordenadas xyz do(s) íon(s) e insere na estrutura concatenada
        # --------------------------------------------------------------------------------------
        ions = detect_ions(_pdb, cutoff=ion_dist_cutoff, chains=[partner1, partner2])
        print_infos(message=f'[{mol}] total number of ions: {len(ions)}', type='protocol')  
        if len(ions) != 0:
            with open(_pdb, 'r') as f:
                lines = f.readlines()
            for ion in ions:
                for i,line in enumerate(lines):
                    if line.startswith('ATOM') and line[21] == ion[1][21]:
                        index = i
                lines.insert(index + 1, ion[1])
            with open(_pdb, 'w') as f:
                f.writelines(lines)

        # 3. executa o protocolo scorejd2
        _pdb = scorejd2(_pdb, basename, outdir)
        
        # 4. previne erros no rosetta
        _pdb = preventing_errors(_pdb, basename, outdir)

        # 5. prepara o script .xml
        _xml = prepareXML(outdir, basename, partner1, partner2)

        # 6. executa o protocolo de minimização e calcula descritores de interface
        # ------------------------------------------------------------------------
        print_infos(message=f'[{mol}] geometry optimization and interface analysis', type='protocol')
        rosetta_features = get_interface_features(_pdb, ions, _xml, outdir)
        rosetta_features = pd.read_csv(json2csv(rosetta_features,outdir), delimiter=',').iloc[:,1:]

        # 7. calcula dG com o super modelo
        # --------------------------------
        print_infos(message=f'[{mol}] calculating dGbind', type='protocol')
        columns_to_remove = ['decoy', 'database', 'partner1', 'partner2', 'complex_type', 'affinity', 'classifier', 'dG_exp']
        x_train = pd.read_csv(f'{PbeePATH}/train_file.csv', delimiter=',').drop(columns=columns_to_remove)
        y_train = pd.read_csv(f'{PbeePATH}/train_file.csv', delimiter=',')['dG_exp']
    
        if ignore_outliers is False:
            outliers = detect_outliers(x_train, rosetta_features)
            if outliers != 0:
                continue

        dG_pred = predictor(basemodels, superlearner, x_train, y_train, rosetta_features)
        affinity = calc_affinity(dG_pred)
        rosetta_features.insert(1, 'dG_pred', dG_pred)
        rosetta_features.insert(2, 'affinity', affinity)
        rosetta_features.to_csv(f'{outdir}/dG_pred.csv', index=False)

        # 7.3 Mostra os dados de dG_pred na tela
        print_infos(message=f'[{mol}] dGbind = {dG_pred:.3f} kcal/mol ({affinity} M)', type='protocol')

        # 8 Apaga arquivos temporários
        remove_files(files=[
            f'{outdir}/{basename}_{partner1}.pdb',
            f'{outdir}/{basename}_{partner2}.pdb',
            f'{outdir}/{basename}_{partner1}.fasta',
            f'{outdir}/{basename}_{partner2}.fasta',
            f'{outdir}/{basename}_jd2_01.pdb',
            f'{outdir}/{basename}_jd2_02.pdb',
            f'{outdir}/{basename}_jd2.pdb',
            f'{outdir}/{basename}_jd2_0001.pdb'])

def remove_files(files):
    for file in files:
        if os.path.exists(file):
            os.remove(file)
        else:
            continue

def partner_checker(pdbfile, partner1, partner2):
    """
    
    Parameters:
    ----------
    -pdbfile ->
    -partner1 ->
    -partner2 ->

    Returns:
    -count ->
    -chains ->
    """
    chains, partners = detect_chains(pdbfile), list(partner1 + partner2)
    count = 0
    for chain in chains:
        if chain in partners:
            count += 1
    return count, chains

def detect_chains(pdbfile):
    chains = set()
    with open(pdbfile, 'r') as file:
        for line in file:
            if line.startswith('ATOM'):
                chain_id = line[21]
                chains.add(chain_id)
    return chains

def detect_outliers(x, rosetta_features):
    """
    
    Parameters:
    -----------
    -x_train ->
    -rosetta_features ->

    Returns: 
    
    --------
    """
    count = 0
    for col in x.columns:
        for index, row in rosetta_features.iterrows():
            sup = True if row[col] > x[col].mean() + x[col].std() * 4 else False
            inf = True if row[col] < x[col].mean() - x[col].std() * 4 else False
            if sup is True or inf is True:
                print_infos(message=f'outlier: {col} = {row[col]}', type='protocol')
                count += 1
    return count

def calc_affinity(dG):
    T = 298.15
    R = 8.314
    dG_J = dG * 4184
    affinity = float(f'{math.exp(dG_J / (R * T)):.6e}')
    return affinity

def json2csv(json_file, outdir):
    outfile = f'{outdir}/score_rlx.csv'
    df = pd.read_json(json_file, orient='records', lines=True)
    df.rename(columns={
        "ifa_dG_separated/dSASAx100":"ifa_dG_separated_dSASAx100","ifa_dG_cross/dSASAx100":"ifa_dG_cross_dSASAx100"}, inplace=True)
    df.to_csv(outfile, index=False)
    return outfile

def preventing_errors(pdbfile, basename, outdir):
    _pdb1 = f'{outdir}/{basename}_jd2_01.pdb'
    with open(pdbfile, "r") as input_file, open(_pdb1, "w") as output_file:
        ter_found = False
        last_ter_index = -1
        for line_index, line in enumerate(input_file):
            if line.startswith("TER"):
                ter_found = True
                last_ter_index = line_index
        if ter_found:
            input_file.seek(0)
            for line_index, line in enumerate(input_file):
                if line_index == last_ter_index:
                    output_file.write("END" + line[3:])
                else:
                    output_file.write(line)
    _pdb2 = f'{outdir}/{basename}_jd2_02.pdb'
    with open(_pdb1, 'r') as inpfile, open(_pdb2, 'w') as outfile:
        for line in inpfile:
            if not line.startswith('SSBOND'):
                outfile.write(line)
    return _pdb2

def pdbcleaner(pdbfile, basename, outdir, submit_dir, partner1, partner2):
    commands = [
        f'python $ROSETTA3_TOOLS/protein_tools/scripts/clean_pdb.py {pdbfile} {partner1}',
        f'python $ROSETTA3_TOOLS/protein_tools/scripts/clean_pdb.py {pdbfile} {partner2}',
        f'mv {submit_dir}/{basename}_{partner1}.pdb {outdir}',
        f'mv {submit_dir}/{basename}_{partner2}.pdb {outdir}',
        f'mv {submit_dir}/{basename}_*.fasta {outdir}']
    for command in commands:
        subprocess.run(command, stdout=subprocess.PIPE, shell=True)
    return f'{outdir}/{basename}_{partner1}.pdb', f'{outdir}/{basename}_{partner2}.pdb'

def concat_pdbs(outdir, basename, partner1, partner2):
    outfile = f'{outdir}/{basename}_jd2.pdb'
    with open(partner1, 'r') as f1, open(partner2, 'r') as f2, open(outfile, 'w') as output_f:
        content1 = f1.read(); output_f.write(content1)
        content2 = f2.read(); output_f.write(content2)
    return outfile

def scorejd2(pdbfile,basename,outdir):
    command = f'\
    score_jd2.default.linuxgccrelease \
    -s {pdbfile} -renumber_pdb \
    -ignore_unrecognized_res \
    -out:pdb \
    -out:path:all {outdir} \
    -output_pose_energies_table false'
    subprocess.run(command, stdout=subprocess.PIPE, shell=True)
    return f'{outdir}/{basename}_jd2_0001.pdb'

def get_interface_features(pdbfile,ions,xml,outdir):
    if len(ions) != 0:
        json_file = f'{outdir}/score_ion_rlx.sc'
        command = f'\
        rosetta_scripts.default.linuxgccrelease \
        -s {pdbfile} \
        -parser:protocol {xml} \
        -holes:dalphaball $ROSETTA3/external/DAlpahBall/DAlphaBall.gcc \
        -ex1 -ex2 -ex2aro \
        -auto_setup_metals \
        -beta_nov16 \
        -use_input_sc \
        -flip_HNQ \
        -no_optH false \
        -out:suffix _ion_rlx \
        -out:file:scorefile_format json \
        -out:path:score {outdir} \
        -out:path:all {outdir} \
        -output_pose_energies_table false'    
    else:
        json_file = f'{outdir}/score_rlx.sc'
        command = f'\
        rosetta_scripts.default.linuxgccrelease \
        -s {pdbfile} \
        -parser:protocol {xml} \
        -holes:dalphaball $ROSETTA3/external/DAlpahBall/DAlphaBall.gcc \
        -ex1 -ex2 -ex2aro \
        -beta_nov16 \
        -use_input_sc \
        -flip_HNQ \
        -no_optH false \
        -out:suffix _rlx \
        -out:file:scorefile_format json \
        -out:path:score {outdir} \
        -out:path:all {outdir} \
        -output_pose_energies_table false'
    subprocess.run(command, stdout=subprocess.PIPE, shell=True)
    return json_file

def ispdb(pdbfile):
    with open(pdbfile, 'r') as file:
        lines = file.readlines()
        count = 0
        for line in lines:
            if line.startswith("ATOM"): 
                count += 1
        if count != 0:
            return os.path.abspath(pdbfile)
        else:
            return False

def isdir(path):
    if os.path.isdir(path):
        return os.path.abspath(path)
    else:
        print_infos(message=f'error: path not found -> {path}', type='none'); print_end()

def processing_time(st):
    sum_x = 0
    for i in range(1000000):
        sum_x += i
    time.sleep(1)
    elapsed_time = time.time() - st
    print(' processing time:', time.strftime("%H:%M:%S", time.gmtime(elapsed_time)))

def print_infos(message, type):
    if type == 'info':
        print(f'            info: {message}')
    if type == 'structure':
        print(f'       structure: {message}')
    if type == 'protocol':
        print(f'        protocol: {message}')
    if type == 'none':
        print(f' {message}')

def print_end():
    exit('\n ####################### End process ############################\n')

def header(version):
    print('')
    print( ' =======================================')
    print( ' Protein Binding Energy Estimator (PBEE)')
    print()
    print( '     DOI: -')
    print(f' version: {version}')
    print( ' =======================================')
    print('')

if (__name__ == "__main__"):
    # Define o tempo de início do script
    st = time.time()

    # Define variável que armazena o diretório de submissão
    submit_dir = os.getcwd()

    # Imprime o cabeçalho na tela
    header(version='-')

    # Define PbeePATH e algoritmos ML
    PbeePATH, basemodels, superlearner = configure_pbee()
    requirements()

    # Configura os argumentos do script
    # ---------------------------------
    parser = argparse.ArgumentParser()
    mandatory = parser.add_argument_group('mandatory arguments')
    # obrigatórios
    mandatory.add_argument('--ipdb', nargs='+', type=str, required=True, metavar='',
    help='str | input file(s) in the PDB format')
    mandatory.add_argument('--partner1', nargs=1, type=str, required=True, metavar='',
    help='str | chain ID of the binding partner (e.g.: receptor)')
    mandatory.add_argument('--partner2', nargs=1, type=str, required=True, metavar='',
    help='str | chain ID of the binding partner (e.g.: ligand)')
    # opcionais
    parser.add_argument('--odir', nargs=1, type=isdir, default=[f'{submit_dir}'], metavar='', 
    help=f'str | folder path to save the output files (default={submit_dir})')
    parser.add_argument('--ion_dist_cutoff', nargs=1, type=int, default=[2], metavar='',
    help='int | cutoff distance (Å) to detect ion(s) close to the protein atoms (default=2)')
    parser.add_argument('--force_mode', action='store_true',
    help='skip warning messages and continue')
    
    # Configura os argumentos e outras variáveis utilizadas
    # -----------------------------------------------------
    args            = parser.parse_args()
    pdbfiles        = args.ipdb
    partner1        = args.partner1[0]
    partner2        = args.partner2[0]
    odir            = args.odir[0]
    force_mode      = args.force_mode
    ion_dist_cutoff = args.ion_dist_cutoff[0]
    ignore_outliers = False # True or False

    # Mostra parâmetros do script na tela
    # ------------------------------------
    print(f'    rosetta_path: {os.environ["ROSETTA3"]}')
    print(f'    rosetta_path: {os.environ["ROSETTA3_BIN"]}')
    print(f'    rosetta_path: {os.environ["ROSETTA3_TOOLS"]}')
    print(f'        partner1: {partner1}')
    print(f'        partner2: {partner2}')
    print(f'      force_mode: {force_mode}')
    print(f' ion_dist_cutoff: {ion_dist_cutoff}')
    print(f' ignore_outliers: {ignore_outliers}')

    # Pré-processamento
    # -----------------
    bad_structures = pre_processing(pdbfiles)
    if force_mode is False:
        pdbfiles = [item for item in pdbfiles if item not in bad_structures]
    else:
        pass
    
    # Pós-processamento
    # -----------------
    print_infos(message=f'total structures: {len(pdbfiles)}', type='info')
    if len(pdbfiles) != 0:
        post_processing(pdbfiles, partner1, partner2, basemodels, superlearner)
    else:
        print_infos(message='nothing to do', type='info'); print_end()

    processing_time(st); print_end()
