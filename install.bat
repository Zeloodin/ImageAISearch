@echo off

cd /D "%~dp0"

set PATH=%PATH%;%SystemRoot%\system32

echo "%CD%"| findstr /C:" " >nul && echo ���� ������ ���������� Miniconda, ������� ������ ���������� � ������� ������, ������ ���� � ���������. && goto end

@rem ��������� ������� ����������� �������� � ���� ���������.
set "SPCHARMESSAGE="��������: � ���� ��������� ���������� ����������� �������!" "         ��� ����� �������� � ���� ���������!""
echo "%CD%"| findstr /R /C:"[!#\$%&()\*+,;<=>?@\[\]\^`{|}~]" >nul && (
	call :PrintBigMessage %SPCHARMESSAGE%
)
set SPCHARMESSAGE=

@rem ��������� ������ ��������� ��� ��������� �� ��������� ����
set TMP=%cd%\installer_files
set TEMP=%cd%\installer_files

@rem ������������� ������������ ����� conda �� ���� �������������, ����� �������� ����������
(call conda deactivate && call conda deactivate && call conda deactivate) 2>nul

@rem config
set INSTALL_DIR=%cd%\installer_files
set CONDA_ROOT_PREFIX=%cd%\installer_files\conda
set INSTALL_ENV_DIR=%cd%\installer_files\env
set MINICONDA_DOWNLOAD_URL=https://repo.anaconda.com/miniconda/Miniconda3-py310_23.3.1-0-Windows-x86_64.exe
set conda_exists=F

@rem ��������, ����� �� ������������� git � conda
call "%CONDA_ROOT_PREFIX%\_conda.exe" --version >nul 2>&1
if "%ERRORLEVEL%" EQU "0" set conda_exists=T

@rem (��� �������������) ���������� git � conda � ������������� �����
@rem ������� �����
if "%conda_exists%" == "F" (
	echo Downloading Miniconda from %MINICONDA_DOWNLOAD_URL% to %INSTALL_DIR%\miniconda_installer.exe

	mkdir "%INSTALL_DIR%"
	call curl -Lk "%MINICONDA_DOWNLOAD_URL%" > "%INSTALL_DIR%\miniconda_installer.exe" || ( echo. && echo �� ������� ��������� Miniconda. && goto end )

	echo ��������� ��������� to %CONDA_ROOT_PREFIX%
	start /wait "" "%INSTALL_DIR%\miniconda_installer.exe" /InstallationType=JustMe /NoShortcuts=1 /AddToPath=0 /RegisterPython=0 /NoRegistry=1 /S /D=%CONDA_ROOT_PREFIX%

	@rem �������������� �������� ���� conda
	echo Miniconda version:
	call "%CONDA_ROOT_PREFIX%\_conda.exe" --version || ( echo. && echo Miniconda not found. && goto end )
)

@rem ������� ����� �����������
if not exist "%INSTALL_ENV_DIR%" (
	echo Packages to install: %PACKAGES_TO_INSTALL%
	call "%CONDA_ROOT_PREFIX%\_conda.exe" create --no-shortcuts -y -k --prefix "%INSTALL_ENV_DIR%" python=3.11 || ( echo. && echo �� ������� ������� ����� Conda. && goto end )
)

@rem ���������, ������������� �� ���� ������� ����� conda
if not exist "%INSTALL_ENV_DIR%\python.exe" ( echo. && echo ����� Conda �����. && goto end )

@rem �������� ���������� �����
set PYTHONNOUSERSITE=1
set PYTHONPATH=
set PYTHONHOME=
set "CUDA_PATH=%INSTALL_ENV_DIR%"
set "CUDA_HOME=%CUDA_PATH%"

set CMD_FLAGS = "--chat --extensions Playground webui_tavernai_charas"

@rem ������������ ���������� env
call "%CONDA_ROOT_PREFIX%\condabin\conda.bat" activate "%INSTALL_ENV_DIR%" || ( echo. && echo ������ Miniconda �� ������. && goto end )

@rem ��������� ����������� env
call python one_click.py %*

@rem ���� ��������� ������� ��� �������, ��������� ������ ���������� �� �� ����� �������� ����������
goto end

:PrintBigMessage
echo. && echo.
echo *******************************************************************
for %%M in (%*) do echo * %%~M
echo *******************************************************************
echo. && echo.
exit /b

:end
pause
