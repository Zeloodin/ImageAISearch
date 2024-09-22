chcp 65001
@echo off

cd /D "%~dp0"

set PATH=%PATH%;%SystemRoot%\system32

echo "%CD%"| findstr /C:" " >nul && echo Этот скрипт использует Miniconda, которую нельзя установить в фоновом режиме, указав путь с пробелами. && goto end

@rem Проверьте наличие специальных символов в пути установки.
set "SPCHARMESSAGE="ВНИМАНИЕ: В пути установки обнаружены специальные символы!" "         Это может привести к сбою установки!""
echo "%CD%"| findstr /R /C:"[!#\$%&()\*+,;<=>?@\[\]\^`{|}~]" >nul && (
	call :PrintBigMessage %SPCHARMESSAGE%
)
set SPCHARMESSAGE=

echo Эти символы, не должны быть в пути установки.
echo ^! ^# ^$ ^% ^& ^( ^) ^* ^+ ^, ^; ^< ^= ^> ^? ^@ ^[ ^] ^^ ^` ^{ ^| ^} ^~
echo ^|
echo И кириллицу
echo а б в г д е ё ж з и й к л м н о п р с т у ф х ц ч ш щ ъ ы ь э ю я
echo ^|
echo Пожалуйста, пробелы замените на символы ^_ ^-
echo Спасибо.
echo ^|

@rem исправить ошибку установки при установке на отдельный диск
set TMP=%cd%\installer_files
set TEMP=%cd%\installer_files

@rem деактивируйте существующие среды conda по мере необходимости, чтобы избежать конфликтов
(call conda deactivate && call conda deactivate && call conda deactivate) 2>nul

@rem config
set INSTALL_DIR=%cd%\installer_files
set CONDA_ROOT_PREFIX=%cd%\installer_files\conda
set INSTALL_ENV_DIR=%cd%\installer_files\env
set MINICONDA_DOWNLOAD_URL=https://repo.anaconda.com/miniconda/Miniconda3-py310_23.3.1-0-Windows-x86_64.exe
set conda_exists=F

@rem выяснить, нужно ли устанавливать git и conda
call "%CONDA_ROOT_PREFIX%\_conda.exe" --version >nul 2>&1
if "%ERRORLEVEL%" EQU "0" set conda_exists=T

@rem (при необходимости) установите git и conda в изолированную среду
@rem скачать конда
if "%conda_exists%" == "F" (
	echo Downloading Miniconda from %MINICONDA_DOWNLOAD_URL% to %INSTALL_DIR%\miniconda_installer.exe

	mkdir "%INSTALL_DIR%"
	call curl -Lk "%MINICONDA_DOWNLOAD_URL%" > "%INSTALL_DIR%\miniconda_installer.exe" || ( echo. && echo Не удалось загрузить Miniconda. && goto end )

	echo Установка Миниконды to %CONDA_ROOT_PREFIX%
	start /wait "" "%INSTALL_DIR%\miniconda_installer.exe" /InstallationType=JustMe /NoShortcuts=1 /AddToPath=0 /RegisterPython=0 /NoRegistry=1 /S /D=%CONDA_ROOT_PREFIX%

	@rem протестировать двоичный файл conda
	echo Miniconda version:
	call "%CONDA_ROOT_PREFIX%\_conda.exe" --version || ( echo. && echo Миниконда не найдена. && goto end )
)

@rem создать среду установщика
if not exist "%INSTALL_ENV_DIR%" (
	echo Packages to install: %PACKAGES_TO_INSTALL%
	call "%CONDA_ROOT_PREFIX%\_conda.exe" create --no-shortcuts -y -k --prefix "%INSTALL_ENV_DIR%" python=3.11 || ( echo. && echo Не удалось создать среду Conda. && goto end )
)

@rem проверьте, действительно ли была создана среда conda
if not exist "%INSTALL_ENV_DIR%\python.exe" ( echo. && echo Среда Conda пуста. && goto end )

@rem изоляция окружающей среды
set PYTHONNOUSERSITE=1
set PYTHONPATH=
set PYTHONHOME=
set "CUDA_PATH=%INSTALL_ENV_DIR%"
set "CUDA_HOME=%CUDA_PATH%"

@rem активировать установщик env
call "%CONDA_ROOT_PREFIX%\condabin\conda.bat" activate "%INSTALL_ENV_DIR%" || ( echo. && echo Крючок Miniconda не найден. && goto end )

@rem установка установщика env
call python one_click.py %*

@rem ниже приведены функции для скрипта, следующая строка пропускает их во время обычного выполнения
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
