C:\python37\python setup.py bdist_wheel
copy dist\*.whl ..\..\
rd dist /s /q
rd build /s /q
rd servicebase.egg-info /s /q
