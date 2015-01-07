.PHONY: clean

all: .build

.build: Dockerfile handler/*
	docker build -t {{cookiecutter.node_name}} .
	touch .build

clean:
	rm .build
