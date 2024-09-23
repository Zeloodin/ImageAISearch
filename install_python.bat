chcp 65001

echo Эти символы, не должны быть в пути установки.
echo ^! ^# ^$ ^% ^& ^( ^) ^* ^+ ^, ^; ^< ^= ^> ^? ^@ ^[ ^] ^^ ^` ^{ ^| ^} ^~
echo ^|
echo И кириллицу
echo а б в г д е ё ж з и й к л м н о п р с т у ф х ц ч ш щ ъ ы ь э ю я
echo ^|
echo Пожалуйста, пробелы замените на символы ^_ ^-
echo Спасибо.
echo ^|

python -m venv venv
venv\Scripts\activate.bat

one_click.py

pause
