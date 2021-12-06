pip freeze>example_reqs/hypothetical_requirements.txt
python -m caniuseonlywheels -r example_reqs/hypothetical_requirements.txt
python -m caniuseonlywheels -r example_reqs/more.txt

echo "expect to find out who has no wheels at all."