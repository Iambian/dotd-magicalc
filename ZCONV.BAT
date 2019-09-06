@echo off
copy /Y dotdmagi.py dotdmagi3.py
python C:\Python27\Tools\Scripts\2to3.py -w -n dotdmagi3.py
pause


