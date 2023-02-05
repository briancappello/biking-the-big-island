#!/bin/bash

echo "running black"
poetry run black .
echo
echo "running isort"
poetry run isort .
echo
echo "running prettier"
npx prettier --write src/
