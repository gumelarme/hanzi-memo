test:
	PICCOLO_CONF="piccolo_conf_test" \
	python -m pytest -s

test_coverage:
	PICCOLO_CONF="piccolo_conf_test" \
	coverage run -m pytest && coverage html && xdg-open htmlcov/index.html
