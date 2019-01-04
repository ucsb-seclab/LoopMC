# LoopMC

This repo contains all the relevant sourced related to our ACSAC 2018 paper: [`LoopMC: Using Loops For Malware Classification Resilient to
Feature-unaware Perturbations`](https://dl.acm.org/citation.cfm?id=3274731).

## Utils
The folder `utils` contains individual utils related to our work.

### Semantic labeling
We provided a standalone version of our semantic labeling technique, which will give a semantic label from `method name`, `class` and, `method signature`.

How to use it:
```
cd utils
# ipython
In [1]: import semantic_labeling as sl

In [2]: sl.get_method_label_by_name('equals', 'Ljava/lang/Object;', 'equals(Ljava/lang/Object;)Z')

Out[2]: 'ObjectComparision'
```
You can import the `semantic_labeling` module into your projects and use it as illustrated above.


## Running the entire pipeline
We created a virtual box VM of Ubuntu 16.04, that contains the required dependencies along with all the sources.

### Importing and logging into the guest machine
1. Make sure you have VirtualBox installed on your system.
2. Download the VM (in OVA format) from [here](https://drive.google.com/open?id=1Gt_HW7AWAqBQcPBrJ4UlDU4GWXPmRUAf).
3. Import the Downloaded OVA into VirtualBox: `File` -> `Import Appliance` -> `specify the file path to the .ova file`.
4. You can login using user: `loopmc` and password `loopmc`

__Note: We suggest to give to the VM at least 4GB of RAM. For obvious reasons, the more the better.__

### Running the pipeline
There are four steps in our pipeline that start from a given set of benign and malicious apks.
#### Activate the virtual environment
```
cd ~/loopmc/loopmc_code
source ~/virtualenvs/loopmc/bin/activate
```
The following steps should be run from within the virtual env.
#### Generating JSON files Database
This steps will disassemble the provided APKs, analyze all the loops and emits JSON files.

__Generating JSONS:__
```
cd ~/loopmc/loopmc_code
python analyze_batch.py -d <directory_containing_apks> -r <directory_where_the_jsons_should_be_stored>
```
Example:
```
python analyze_batch.py -d /tmp/apks -r /tmp/apkjsons
```

`analyze_batch.py` has other fancier options to run in multi-process mode. You are free to explore.

__Dumping into a local database:__

```
cd ~/loopmc/loopmc_code/ml_project/cellophane
python cellophane.py -j <directory_where_the_jsons_are_stored> --generate-db
```

The above command will create an sqlite DB in the file: `/home/loopmc/loopmc/loopmc_code/ml_project/loopmc.db`

#### Generating Label files
This will create auxillary label files needed to create the feature vector.
```
cd  ~/loopmc/loopmc_code/ml_project/feature_scripts
python get_all_labels.py <directory_where_the_jsons_are_stored>
python boolean_vectorize.py
cd ~/loopmc/loopmc_code/ml_project/clustering/sklearn
python fast_level_split.py --vector ../../feature_scripts/vector_data/vector.txt --idmap ../../feature_scripts/vector_data/loop_id_map.txt --available-labels ../../feature_scripts/features_data/available_labels.txt --label-json ../../feature_scripts/features_data/label_tree.json --outdir <directory_where_temp_clusters_should_be_stored>
```
#### Generating feature vector
This steps will generate the feature vector which could be used by any machine learning technique.
```
cd  ~/loopmc/loopmc_code/ml_project/type_classification_scripts
python extract_type_genome.py <directory_where_the_jsons_are_stored> ../feature_scripts/vector_data/loop_id_map.txt <directory_where_temp_clusters_are_stored>/fast_leaf_level_split <output_directory>
```
Here, `<directory_where_temp_clusters_are_stored>` is the directory provided in the __Generating Label files__ step.

The above script will generate a file at : `<output_directory>/type_clusters.csv`, that contains the feature vector for each APK.

__NOTE:__ The script, `extract_type_genome.py` creates the ground truth labels for APKs based on the name. If you want to change it, please change the function `categorize_em_all` in the file.

#### Running Random forest
Once the feature vector is created, you can follow the below steps to run Random forest:
```
cd ~/loopmc/loopmc_code/ml_project/type_classification_scripts
python print_RF_type_results.py <output_directory>/type_clusters.csv <directory_where_temp_clusters_are_stored>/fast_leaf_level_split 
```

Where, `<output_directory>/type_clusters.csv` is the file generated in the previous step and `<directory_where_temp_clusters_are_stored>` is the folder provided in the __Generating Label files__ step.

The results will be stored in the files: `score_RF.txt` and the folder `RF_trees` contains the individual trees and the estimator.


