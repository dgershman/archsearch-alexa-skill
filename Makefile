.PHONY: deploy

deploy:
	pyenv version 3.6
	sls deploy
