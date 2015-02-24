.PHONY: docs

code : rabbitman/client.py
	python codegen.py > rabbitman/client.py

docs:
	sphinx-build -b html -d docs/_build/doctrees docs docs/_build/html
