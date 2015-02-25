.PHONY: docs

code : rabbitman.py

rabbitman.py : codegen.py
	python codegen.py > rabbitman.py

docs:
	sphinx-build -b html -d docs/_build/doctrees docs docs/_build/html
