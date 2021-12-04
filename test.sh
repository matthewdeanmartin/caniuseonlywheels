pip freeze>hypothetical_requirements.txt
python -m caniuseonlywheels -r hypothetical_requirements.txt --verbose
echo "expect to find out who has no wheels at all.""