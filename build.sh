export PYTHONPATH=$PYTHONPATH:.
# what is wrong with ignore?!
# pylint caniuseonlywheels --ignore=distlib
# flake8 caniuseonlywheels
poetry run python -m pytest caniuseonlywheels
poetry run python -m pytest --doctest-glob="caniuseonlywheels/**/*.py"
poetry run pytest test -v --cov-report html:coverage --cov=caniuseonlywheels
echo "not bumping version here, just checking if we can create the wheel"
poetry run poetry build
poetry run check-wheel-contents dist/*.whl
poetry run vermin caniuseonlywheels
