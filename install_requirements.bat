chcp 65001
venv\Scripts\python.exe -m pip install --upgrade pip
echo https://pytorch.org/
venv\Scripts\pip install -r requirements.txt
venv\Scripts\pip install ftfy regex tqdm
venv\Scripts\pip install git+https://github.com/openai/CLIP.git