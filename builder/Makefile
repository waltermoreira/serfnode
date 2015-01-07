.PHONY: clean

build: Dockerfile template/*
	docker build -t serfnode_init .
	touch .build

clean:
	rm .build
