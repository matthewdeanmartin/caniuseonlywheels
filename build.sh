export PYTHONPATH=$PYTHONPATH:.
# what is wrong with ignore?!
# pylint caniuseonlywheels --ignore=distlib
flake8 caniuseonlywheels
python -m pytest caniuseonlywheels
python -m pytest --doctest-glob="caniuseonlywheels/**/*.py"
pytest test -v --cov-report html:coverage --cov=caniuseonlywheels
echo not bumping version here, just checking if we can create the wheel
poetry build
check-wheel-contents dist/*.whl
vermin caniuseonlywheels