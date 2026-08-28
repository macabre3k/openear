.PHONY: install test run docker

install:
	python -m pip install -e . pytest

test:
	pytest -q

run:
	streamlit run app.py

docker:
	docker compose up --build
