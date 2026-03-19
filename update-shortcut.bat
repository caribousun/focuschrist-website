@echo off
set "lnk=C:\Users\carib\OneDrive\Desktop\Mission Control (Online).lnk"
set "url=http://705f14cec0f3df44-24-2-77-101.serveousercontent.com"
powershell -Command "$s = New-Object -ComObject WScript.Shell; $l = $s.CreateShortcut('%lnk%'); $l.TargetPath = '%url%'; $l.Save()"
