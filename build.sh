python3 setup.py bdist_wheel
cp dist/*.whl ../../
rm -rf dist
rm -rf build
rm -rf servicebase.egg-info
