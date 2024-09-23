import sys
import os

import argparse
import glob
import hashlib

import platform
import re
import signal
import site
import subprocess

# https://github.com/oobabooga/text-generation-webui

script_dir = os.getcwd()
conda_env_path = os.path.join(script_dir, "installer_files", "env")

# Remove the '# ' from the following lines as needed for your AMD GPU on Linux
# os.environ["ROCM_PATH"] = '/opt/rocm'
# os.environ["HSA_OVERRIDE_GFX_VERSION"] = '10.3.0'
# os.environ["HCC_AMDGPU_TARGET"] = 'gfx1030'

flags = f"{' '.join([flag for flag in sys.argv[1:] if flag != '--update'])}"


def signal_handler(sig, frame):
    """
    Эта функция вызывается при получении сигнала.

    Она заставит программу выйти с кодом состояния 0.

    :param sig: Номер полученного сигнала.
    :param frame: Текущий кадр стека.
    :return: Нет
    """
    
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)


def is_linux():
    """
    Проверяет, является ли текущая ОС Linux.

    :return: True, если текущая ОС Linux, False в противном случае.
    """
    return sys.platform.startswith("linux")


def is_windows():
    """
    Проверяет, является ли текущая ОС Windows.

    :return: True, если текущая ОС Windows, False в противном случае.
    """
    return sys.platform.startswith("win")


def is_macos():
    """
    Проверяет, является ли текущая ОС macOS.

    :return: True, если текущая ОС macOS, False в противном случае.
    """
    return sys.platform.startswith("darwin")


def is_x86_64():
    """
    Проверяет, является ли текущая архитектура x86-64.

    :return: True, если текущая архитектура x86-64, False в противном случае.
    """
    return platform.machine() == "x86_64"


def cpu_has_avx2():
    """
    Проверяет, есть ли у ЦП набор инструкций AVX2.

    Эта функция использует библиотеку cpuinfo для получения информации о ЦП и проверяет,
    есть ли флаг 'avx2'. Если да, функция возвращает True, в противном случае
    она возвращает False. Если библиотеке cpuinfo не удается импортировать
    (например, если не установлена библиотека), или получить информацию о ЦП, функция возвращает True.

    :return: True, если у ЦП есть набор инструкций AVX2, в противном случае False.
    """
    try:
        import cpuinfo

        info = cpuinfo.get_cpu_info()
        if 'avx2' in info['flags']:
            return True
        else:
            return False
    except:
        return True


def cpu_has_amx():
    """
    Проверяет, есть ли у ЦП набор инструкций AMX.

    Эта функция использует библиотеку cpuinfo для получения информации о ЦП и проверяет,
    есть ли флаг 'amx'. Если да, функция возвращает True, в противном случае
    она возвращает False. Если библиотеке cpuinfo не удается импортировать
    (например, если не установлена библиотека), или получить информацию о ЦП, функция возвращает True.

    :return: True, если у ЦП есть набор инструкций AMX, в противном случае False.
    """
    try:
        import cpuinfo

        info = cpuinfo.get_cpu_info()
        if 'amx' in info['flags']:
            return True
        else:
            return False
    except:
        return True


def torch_version():
    """
    Возвращает версию torch, установленную в среде.

    Если файл 'version.py' найден в пакете torch, он считывает версию оттуда.
    В противном случае он импортирует модуль torch и считывает версию из него.

    Возвращает:
        str: Версия torch в виде строки.
    """
    site_packages_path = None
    for sitedir in site.getsitepackages():
        if "site-packages" in sitedir and conda_env_path in sitedir:
            site_packages_path = sitedir
            break

    if site_packages_path:
        torch_version_file = open(os.path.join(site_packages_path, 'torch', 'version.py')).read().splitlines()
        torver = [line for line in torch_version_file if '__version__' in line][0].split('__version__ = ')[1].strip("'")
    else:
        from torch import __version__ as torver

    return torver


def is_installed():
    """
    Проверяет, установлен ли torch в активной среде conda.

    Возвращает:
        bool: True, если torch установлен, False - в противном случае.
    """
    site_packages_path = None
    for sitedir in site.getsitepackages():
        if "site-packages" in sitedir and conda_env_path in sitedir:
            site_packages_path = sitedir
            break

    if site_packages_path:
        return os.path.isfile(os.path.join(site_packages_path, 'torch', '__init__.py'))
    else:
        return os.path.isdir(conda_env_path)


def check_env():
    # If we have access to conda, we are probably in an environment
    """
    Проверяет, является ли среда средой conda, а не базовой средой.

    Выход, если conda не установлена ​​или среда является базовой средой.

    Возвращает:
        None
    """
    conda_exist = run_cmd("conda", environment=True, capture_output=True).returncode == 0
    if not conda_exist:
        print("Conda не установлена. Выход...")
        sys.exit(1)

    # Ensure this is a new environment and not the base environment
    if os.environ["CONDA_DEFAULT_ENV"] == "base":
        print("Создайте среду для этого проекта и активируйте ее. Выход...")
        sys.exit(1)


def clear_cache():
    """
    Очищает кэш conda и pip.
    
    run_cmd("conda clean -a -y", environment=True)
    run_cmd("python -m pip cache purge", environment=True)
    """
    
    run_cmd("conda clean -a -y", environment=True)
    run_cmd("python -m pip cache purge", environment=True)


def print_big_message(message):
    """
    Печатает сообщение с большой рамкой вокруг него.

    Аргументы:
        message (str): Сообщение для печати.
    """

    message = message.strip()
    lines = message.split('\n')
    print("\n\n*******************************************************************")
    for line in lines:
        if line.strip() != '':
            print("*", line)

    print("*******************************************************************\n\n")


def calculate_file_hash(file_path):
    """
    Вычисляет хэш SHA-256 файла.

    Аргументы:
    file_path (str): Путь к файлу для хэширования.

    Возвращает:
    str: хэш SHA-256 файла или пустую строку, если файл не существует.
    """
    p = os.path.join(script_dir, file_path)
    if os.path.isfile(p):
        with open(p, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()
    else:
        return ''


def run_cmd(cmd, assert_success=False, environment=False, capture_output=False, env=None):
    # Use the conda environment
    """
    Запускает команду оболочки. Если `environment` имеет значение True, команда запускается из среды conda. 
    Если `assert_success` имеет значение True, программа завершит работу, если команда завершится неудачей. 
    Если `capture_output` имеет значение True, вывод команды захватывается и 
    возвращается как объект CompletedProcess.

    Аргументы:
    cmd (str): Команда для запуска.
    assert_success (bool): Если True, программа завершит работу, если команда завершится неудачей.
    environment (bool): Если True, команда запускается из среды conda.
    capture_output (bool): Если True, вывод команды захватывается и возвращается.
    env (dict): Словарь переменных среды, которые необходимо задать перед запуском команды.

    Возвращает:
    subprocess.CompletedProcess: Результат команды. Если `capture_output` имеет значение True,
    этот объект будет содержать вывод команды.
    """
    if environment:
        if is_windows():
            conda_bat_path = os.path.join(script_dir, "installer_files", "conda", "condabin", "conda.bat")
            cmd = f'"{conda_bat_path}" activate "{conda_env_path}" >nul && {cmd}'
        else:
            conda_sh_path = os.path.join(script_dir, "installer_files", "conda", "etc", "profile.d", "conda.sh")
            cmd = f'. "{conda_sh_path}" && conda activate "{conda_env_path}" && {cmd}'

    # Run shell commands
    result = subprocess.run(cmd, shell=True, capture_output=capture_output, env=env)

    # Assert the command ran successfully
    if assert_success and result.returncode != 0:
        print(f"Command '{cmd}' failed with exit status code '{str(result.returncode)}'.\n\nExiting now.\nTry running the start/update script again.")
        sys.exit(1)

    return result


def install_ImageAISearch():
    # Select your GPU, or choose to run in CPU mode
    """
    Выберите свой графический процессор или выберите режим работы в режиме центрального процессора.

    Попросите пользователя ввести свой выбор графического процессора 
    (NVIDIA, AMD, Apple M Series, Intel Arc (IPEX) или None (режим центрального процессора)).
    Если пользователь выбирает NVIDIA, спросите, хочет ли он использовать CUDA 11.8 вместо 12.1.
    # Если пользователь выбирает AMD, проверьте, установлен ли ROCm SDK, и запросите подтверждение.
    # Если пользователь выбирает Intel Arc (IPEX), установите необходимые библиотеки времени выполнения Intel oneAPI.

    Установите зависимости PyTorch и PyTorch в зависимости от выбора графического процессора пользователем.
    Если пользователь выбирает NVIDIA, установите библиотеки времени выполнения CUDA.
    Если пользователь выбирает Intel Arc (IPEX), установите необходимые библиотеки времени выполнения Intel oneAPI.

    Обновите требования для веб-интерфейса, запустив Функция update_requirements с аргументом initial_installation, установленным на True.
    """
    if "GPU_CHOICE" in os.environ:
        choice = os.environ["GPU_CHOICE"].upper()
        print_big_message(f"Selected GPU choice \"{choice}\" based on the GPU_CHOICE environment variable.")
    else:
        print()
        print("Какой у вас графический процессор??")
        print()
        print("A) NVIDIA")
        # print("B) AMD (Linux/MacOS only. Requires ROCm SDK 5.6 on Linux)")
        # print("C) Apple M Series")
        # print("D) Intel Arc (IPEX)")
        print("N) Нет (я хочу запускать модели в режиме CPU (ЦП)")
        print()

        choice = input("Input> ").upper()
        while choice not in 'AND': #'ABCDN':
            print("Неверный выбор. Попробуйте еще раз..")
            choice = input("Input> ").upper()

    gpu_choice_to_name = {
        "A": "NVIDIA",
        # "B": "AMD",
        # "C": "APPLE",
        "D": "INTEL",
        "N": "NONE"
    }

    selected_gpu = gpu_choice_to_name[choice]

    # Find the proper Pytorch installation command
    install_git = "conda install -y -k ninja git"
    install_pytorch = "python -m pip install torch==2.1.* torchvision==0.16.* torchaudio==2.1.* "

    use_cuda118 = "N"
    if any((is_windows(), is_linux())) and selected_gpu == "NVIDIA":
        if "USE_CUDA118" in os.environ:
            use_cuda118 = "Y" if os.environ.get("USE_CUDA118", "").lower() in ("yes", "y", "true", "1", "t", "on") else "N"
        else:
            # Ask for CUDA version if using NVIDIA
            print("\nDХотите использовать CUDA 11.8 вместо 12.1? Выбирайте этот вариант только если ваш GPU очень старый (Kepler или старше).\nДля графических процессоров серий RTX и GTX, скажем, \"N\". Если не уверены, скажите \"N\".\n")
            use_cuda118 = input("Input (Y/N)> ").upper().strip('"\'').strip()
            while use_cuda118 not in 'YN':
                print("Неверный выбор. Попробуйте еще раз.")
                use_cuda118 = input("Input> ").upper().strip('"\'').strip()

        if use_cuda118 == 'Y':
            print("CUDA: 11.8")
            install_pytorch += "--index-url https://download.pytorch.org/whl/cu118"
        else:
            print("CUDA: 12.1")
            install_pytorch += "--index-url https://download.pytorch.org/whl/cu121"
    # elif not is_macos() and selected_gpu == "AMD":
    #     if is_linux():
    #         install_pytorch += "--index-url https://download.pytorch.org/whl/rocm5.6"
    #     else:
    #         print("Графические процессоры AMD поддерживаются только в Linux. Выход...")
    #         sys.exit(1)
    # elif is_linux() and selected_gpu in ["APPLE", "NONE"]:
    #     install_pytorch += "--index-url https://download.pytorch.org/whl/cpu"
    elif selected_gpu == "INTEL":
        install_pytorch = "python -m pip install torch==2.1.0a0 torchvision==0.16.0a0 torchaudio==2.1.0a0 intel-extension-for-pytorch==2.1.10 --extra-index-url https://pytorch-extension.intel.com/release-whl/stable/xpu/us/"

    # Install Git and then Pytorch
    print_big_message("Installing PyTorch.")
    run_cmd(f"{install_git} && {install_pytorch} && python -m pip install py-cpuinfo==9.0.0", assert_success=True, environment=True)

    # Install CUDA libraries (this wasn't necessary for Pytorch before...)
    if selected_gpu == "NVIDIA":
        print_big_message("Installing the CUDA runtime libraries.")
        run_cmd(f"conda install -y -c \"nvidia/label/{'cuda-12.1.1' if use_cuda118 == 'N' else 'cuda-11.8.0'}\" cuda-runtime", assert_success=True, environment=True)

    if selected_gpu == "INTEL":
        # Install oneAPI dependencies via conda
        print_big_message("Installing Intel oneAPI runtime libraries.")
        run_cmd("conda install -y -c intel dpcpp-cpp-rt=2024.0 mkl-dpcpp=2024.0")
        # Install libuv required by Intel-patched torch
        run_cmd("conda install -y libuv")

    # Install the webui requirements
    update_requirements(initial_installation=True)


def update_requirements(initial_installation=False):
    # Create .git directory if missing
    """
    Обновляет требования к ImageAiSearch до последней версии.

    :param initial_installation: Является ли это первым запуском скрипта. 
                                 Если True, будут установлены требования для всех расширений.

    :type initial_installation: bool
    """
    if not os.path.exists(os.path.join(script_dir, ".git")):
        git_creation_cmd = 'git init -b main && git remote add origin https://github.com/Zeloodin/ImageAISearch && git fetch && git symbolic-ref refs/remotes/origin/HEAD refs/remotes/origin/main && git reset --hard origin/main && git branch --set-upstream-to=origin/main'
        run_cmd(git_creation_cmd, environment=True, assert_success=True)

    files_to_check = [
        'start_windows.bat', 'update_windows.bat', 'run.py', 'run.bat', 'one_click.py'
    ]

    before_pull_hashes = {file_name: calculate_file_hash(file_name) for file_name in files_to_check}
    run_cmd("git pull --autostash", assert_success=True, environment=True)
    after_pull_hashes = {file_name: calculate_file_hash(file_name) for file_name in files_to_check}

    # Check for differences in installation file hashes
    for file_name in files_to_check:
        if before_pull_hashes[file_name] != after_pull_hashes[file_name]:
            print_big_message(f"Файл '{file_name}' был обновлен во время 'git pull'. Пожалуйста, запустите скрипт еще раз.")
            exit(1)

    # Определите версии Python и PyTorch
    torver = torch_version()
    is_cuda = '+cu' in torver
    is_cuda118 = '+cu118' in torver  # 2.1.0+cu118
    is_rocm = '+rocm' in torver  # 2.0.1+rocm5.4.2
    is_intel = '+cxx11' in torver  # 2.0.1a0+cxx11.abi
    is_cpu = '+cpu' in torver  # 2.0.1+cpu

    # if is_rocm:
    #     base_requirements = "requirements_amd" + ("_noavx2" if not cpu_has_avx2() else "") + ".txt"
    # if is_cpu or is_intel:
    #     base_requirements = "requirements" + ("_noavx2" if not cpu_has_avx2() else "") + ".txt"
    # elif is_macos():
    #     base_requirements = "requirements_apple_" + ("intel" if is_x86_64() else "silicon") + ".txt"
    # else:
    #     base_requirements = "requirements" + ("_noavx2" if not cpu_has_avx2() else "") + ".txt"

    base_requirements = "requirements.txt"

    requirements_file = base_requirements

    print_big_message(f"Установка требований ImageAISearch из файла: {requirements_file}")
    print(f"TORCH: {torver}\n")

    # Подготовьте файл требований
    textgen_requirements = open(requirements_file).read().splitlines()
    # if is_cuda118:
    #     textgen_requirements = [req.replace('+cu121', '+cu118').replace('+cu122', '+cu118') for req in textgen_requirements]
    # if is_windows() and is_cuda118:  # No flash-attention on Windows for CUDA 11
    #     textgen_requirements = [req for req in textgen_requirements if 'jllllll/flash-attention' not in req]

    with open('temp_requirements.txt', 'w') as file:
        file.write('\n'.join(textgen_requirements))

    # Обходной путь для пакетов git+, которые не обновляются должным образом.
    git_requirements = [req for req in textgen_requirements if req.startswith("git+")]
    for req in git_requirements:
        url = req.replace("git+", "")
        package_name = url.split("/")[-1].split("@")[0].rstrip(".git")
        run_cmd(f"python -m pip uninstall -y {package_name}", environment=True)
        print(f"Удален {package_name}")

    # Убедитесь, что установлены требования API (временно)
    extension_req_path = os.path.join("requirements.txt")
    if os.path.exists(extension_req_path):
        run_cmd(f"python -m pip install -r {extension_req_path} --upgrade", environment=True)

    # Установить/обновить требования проекта
    run_cmd("python -m pip install -r temp_requirements.txt --upgrade", assert_success=True, environment=True)
    os.remove('temp_requirements.txt')

    # Установка требований, CLIP, ftfy regex tqdm
    run_cmd(f"@rem Установка требований, CLIP, ftfy regex tqdm")
    run_cmd(f"installer_files\env\python.exe -m pip install --upgrade pip", assert_success=True, environment=True)
    run_cmd(f"installer_files\env\Scripts\pip install -r requirements.txt", assert_success=True, environment=True)
    run_cmd(f"installer_files\env\Scripts\pip install ftfy regex tqdm", assert_success=True, environment=True)
    run_cmd(f"installer_files\env\Scripts\pip install git+https://github.com/openai/CLIP.git", assert_success=True, environment=True)

    # Проверьте наличие '+cu' или '+rocm' в строке версии, чтобы определить, использует ли torch CUDA или ROCm. Проверьте также наличие pytorch-cuda для обратной совместимости
    if not any((is_cuda, is_rocm)) and run_cmd("conda list -f pytorch-cuda | grep pytorch-cuda", environment=True, capture_output=True).returncode == 1:
        clear_cache()
        return

    # if not os.path.exists("repositories/"):
    #     os.mkdir("repositories")

    clear_cache()


def launch_ImageAISearch():
    run_cmd(f"installer_files\env\python.exe run.py {flags}", environment=True)


if __name__ == "__main__":
    # Проверяет, что мы находимся в среде conda
    check_env()

    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument('--update', action='store_true', help='Update the web UI.')
    args, _ = parser.parse_known_args()

    if args.update:
        update_requirements()
    else:
        # Если ImageAISearch уже установлен, пропустите и запустите
        if not is_installed():
            install_ImageAISearch()
            os.chdir(script_dir)

        if os.environ.get("LAUNCH_AFTER_INSTALL", "").lower() in ("no", "n", "false", "0", "f", "off"):
            print_big_message("Установка успешно завершена и теперь будет завершена из-за LAUNCH_AFTER_INSTALL.")
            sys.exit()

        # Обходной путь для llama-cpp-python, загружающий пути в переменные окружения CUDA, даже если они не существуют
        conda_path_bin = os.path.join(conda_env_path, "bin")
        if not os.path.exists(conda_path_bin):
            os.mkdir(conda_path_bin)

        # Запустите ImageAISearch
        launch_ImageAISearch()
