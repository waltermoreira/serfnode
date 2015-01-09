.PHONY: clean

build: Dockerfile entry.sh template/*
	docker build -t serfnode_init .
	touch .build

clean:
	rm .build
