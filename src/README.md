# Game Bundle

Use Poetry to install dependencies. You can then run Flask from inside the game directory to test/play Quipped:

```
python -m pip install poetry
poetry install
cd game
poetry run python -m flask run
```