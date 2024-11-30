# Expertadvisor Application

## collaborator space for Expertadvisor as part of TTH hackathon

### Steps for the environment setup 
Assumes miniconda3 is installed 
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
pip install pyPDF2

### 4. Install pycharm community edition 2024.02
### 5. Create the new project from git
File > Project from version control
In the URL , key in  "https://github.com/kartsahu/expertadvisor.git" and clone
File > Settings > project:expertadvisor > Add interpeter to include the conda environment as shown below
![image](https://github.com/user-attachments/assets/a519ba40-b12b-44e5-a3de-d0c3f9503b51)

### 6. Launch the streamlit web app 
Ensure the conda environment advexpert is enabled in Terminal
Launch the web app by invoking the command python -m streamlit run C:\Users\<xxxx>\PycharmProjects\expertadvisor\Sakwatchen_streamlit_gemini_multi.py



