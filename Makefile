update-cdk:
	cd iot-playground;
	pip install --upgrade aws-cdk.core;
	cd -;

restart-env:
	cd iot-playground;
	python3 -m venv .env;
	source .env/bin/activate.fish;
	pip install -r requirements.txt;
	cd -;