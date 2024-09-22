chcp 65001
installer_files\env\python.exe -m pip install --upgrade pip
installer_files\env\Scripts\pip install -r requirements.txt
installer_files\env\Scripts\pip install ftfy regex tqdm
installer_files\env\Scripts\pip install git+https://github.com/openai/CLIP.git