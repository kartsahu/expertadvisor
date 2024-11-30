# Expertadvisor Application

## collaborator space for Expertadvisor as part of TTH hackathon

### Steps for the environment setup 

### 1. Create the environment using the reuqirement file 
conda create --name advexpert python=3.9.20 -c conda-forge --file "C:\Users\61011060\Downloads\requirements.txt"
create the following two directory name as:
* data -> place the json and pdf files in the folder which is used as reference data from LLM
* access -> place gemini access key named as gemini_key.json


### 2. Activate the environment
conda activate advexpert

### 3. install the gcp key related dependencies
pip install grpcio==1.68.0
pip install grpcio-status==1.62.3
