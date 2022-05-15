del /s /q dist
pyinstaller main.py --onefile
ren .\dist\main.exe .\dist\MobSkillDBEditor.exe
copy config_tmpl.yml .\dist\config.yml
copy *.ui .\dist
pause
