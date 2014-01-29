test: test_accounts test_api test_htk

compile:
	cd static/css/ && make

compile_all:
	cd static/css && make compile_all

test_accounts:
	python manage.py test accounts

test_api:
	python manage.py test api

test_htk:
	python manage.py test htk

test_scripts:
	python manage.py test scripts

deploy:
	fab deploy
