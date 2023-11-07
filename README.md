
# Overview
PBEE (**P**rotein **B**inding **E**nergy **E**stimator) is an easy-to-use pipeline written in Python3 that use a ML model based on Rosetta descriptors to predict the free energy of binding of protein-protein complexes.

The PBEE workflow is shown below:

```mermaid
flowchart TB
	pdb[/PDB file/] 
	step1[Extracts chains to a new pdb file] 
	step2{Looks for gaps \n in the backbone}
	step3[Checks for ions near \n protein atoms] 
	step4[Remove non-protein atoms] 
	step5["Geometry optimization \n (Rosetta)"] 
	step6["Interface analysis \n (Rosetta)"] 
	step7[SL engine]
	result[dGbind]
	ends[End process]
	
	subgraph B[ ]
	step5 --> |Minimized structure| step6 --> |Rosetta descriptors| step7
	end 
	
	subgraph A[ ]
	step1 --> step2
	step2 --> |Yes| ends
	step2 --> |No| step3
	step3 --> step4
	end 
	
	pdb -.- step1
	step4 -.-> step5
	step7 -.-> result
``` 

# Requirements

| Package        | Version |
|----------------|---------|
| RosettaCommons | 3.12    |
| numpy          | 1.24.4  |
| pandas         | 2.0.3   |
| gdown          | 4.7.1   |


# Download & Install

1. Clone this repository on your machine: `git clone https://github.com/eltonjfc/pbee.git`
2. Go into the `pbee` folder and open the `setup.sh` file and edit the PbeePATH variable with the PBEE directory path on your machine, save and close the file;
   ```
   PbeePATH=/path/to/pbee/folder
   ```
4. Open the terminal (ctrl + t) and execute the following command: `bash setup.sh`
5. Download (or update) the required packages, and ML models: `pip3 install -r requirements.txt && python3 update_basemodels.py`

**⚠️ Warning**: RosettaCommons binaries are not available in this repository and must be properly installed and configured before running PBEE. More information on downloading, installing and configuring can be found on the software's web page (https://www.rosettacommons.org/).

# Arguments description

| Argument          | Mandatory | Description |
|-------------------|-----------|-------------|
| -\-ipdb            | Yes      | Input files in the PDB format |
| -\-partner1        | Yes      | Chain ID of the binding partner (e.g.: receptor) |
| -\-partner2        | Yes      | Chain ID of the binding partner (e.g.: ligand) |
| -\-odir            | No       | Folder path to save the output files |
| -\-ion_dist_cutoff | No       | Cutoff distance to detect ion(s) close to the protein atoms |          
| -\-force_mode      | No       | Skip warning messages and continue |

# Usage

The example below includes the structure of an antibody (HyHEL-63) that binds to lysozyme C (PDB 1XGU) with a binding affinity of -11.28 kcal/mol. In the PDB file, the heavy and light chains of the antibody (ligand) are coded as chain "A" and "B", respectively, while Lysozyme C (receptor) is coded as "C". Therefore, the PBEE should be run as follows:

```
python3 pbee.py --ipdb ./test/pdbs/1xgu.pdb --partner1 AB --partner2 C --odir ./test
```

The above command will redirect the outputs to `/path/to/pbee/folder/test/pbee_outputs/1xgu`. A detailed description of the output files generated can be seen in the table below:

| File              | Description                                                                 |
|-------------------|-----------------------------------------------------------------------------|
| 1xgu.xml          | Rosetta protocol that performs geometry optimization and interface analysis |
| 1xgu_rlx_0001.pdb | Optimized structure |
| dG_pred.csv       | Rosetta descriptors and dGbind predicted by PBEE |
| score_rlx.csv     | Rosetta descriptors (csv format required by PBEE) |
| score_rlx.sc      | Rosetta descriptors (json format) |



# Description of the Rosetta XML script

The following is an example of a Rosetta XML script used in the PBEE. The script outlines a pipeline for analyzing and manipulating protein structures, utilizing a variety of scoring functions, residue selectors, simple metrics, filters,  and movers. In this context, the script aims to assess and refine interactions between two protein chains, focusing on interaction energy and structural features. In summary, the XML script represents a detailed plan for protein structure analysis and manipulation using Rosetta. It outlines a series of steps aimed at evaluating protein chain interactions and improving structure quality.


```xml
<ROSETTASCRIPTS>
<SCOREFXNS>
	<ScoreFunction name="beta" weights="beta_nov16"/>
</SCOREFXNS>
<RESIDUE_SELECTORS>
	<Chain name="partner1" chains="AB"/>
	<Chain name="partner2" chains="C"/>
</RESIDUE_SELECTORS>
<TASKOPERATIONS>
	<InitializeFromCommandline name="init"/>
</TASKOPERATIONS>
<SIMPLE_METRICS>
	<InteractionEnergyMetric name="ie" residue_selector="partner1" residue_selector2="partner2" scorefxn="beta"/>
</SIMPLE_METRICS>
<FILTERS>
	<ShapeComplementarity name="sc" residue_selector1="partner1" residue_selector2="partner2" confidence="0"/>
	<ContactMolecularSurface name="cms" distance_weight="0.5" target_selector="partner1" binder_selector="partner2" confidence="0"/>
	<InterfaceHoles name="holes" jump="1" confidence="0"/>
	<Ddg name="ddg_filter1" scorefxn="beta" jump="1" chain_num="2" repeats="1" repack="0" repack_bound="0" repack_unbound="0" threshold="99999" confidence="0"/>
</FILTERS>
<MOVERS>
	<MinMover name="min1" scorefxn="beta" jump="1" max_iter="50000" tolerance="0.0001" cartesian="0" bb="0" chi="1" bb_task_operations="init" chi_task_operations="init"/>
	<MinMover name="min2" scorefxn="beta" jump="1" max_iter="50000" tolerance="0.0001" cartesian="0" bb="1" chi="1" bb_task_operations="init" chi_task_operations="init"/>
	<InterfaceAnalyzerMover name="ifa" scorefxn="beta" interface="A_B" packstat="1" interface_sc="1" tracer="1" scorefile_reporting_prefix="ifa"/>
	<RunSimpleMetrics name="iesum" metrics="ie"/>
</MOVERS>
<PROTOCOLS>
	<Add mover_name="min1"/>
	<Add mover_name="min2"/>
	<Add mover_name="iesum"/>
	<Add mover_name="ifa"/>
	<Add filter_name="ddg_filter1"/>
	<Add filter_name="cms"/>
	<Add filter_name="sc"/>
	<Add filter_name="holes"/>
</PROTOCOLS>
</ROSETTASCRIPTS>
```

1. The script begins by defining the **scoring functions** to be used, which weigh different energetic terms concerning protein interactions;
2. Subsequently, **residue selectors** are set up to identify the protein chains of interest, labeled as **partner1** and **partner2**; 
3. Task operations are also defined to initialize parameters from the command line;
4. The next script section introduces **simple metrics** that evaluate specific aspects of the protein structure, such as interaction energy between selected residues in the **partner1** and **partner2** chains; 
5. In the **filters** section, a series of filters are defined to assess structural and energetic properties of interactions. These filters encompass calculations of shape complementarity, molecular surface contacts, interface holes, and changes in free energy (ddG);
6. **Movers** are defined to carry out minimization and interface analysis. This includes minimization with varying parameters and levels of detail, as well as **interface analysis** to evaluate features such as packing and hydrogen bonding. 
7. Lastly, protocols are constructed using the defined movers and filters. The movers and filters are added in a specific sequence to perform desired analysis and refinement steps. This encompasses minimization, metric calculation, interface analysis, and the application of filters to select structures meeting predetermined criteria.
