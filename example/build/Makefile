.PHONY: clean

build: Dockerfile handler/*
	docker build -t rabbit .
	touch build

clean:
	rm build
