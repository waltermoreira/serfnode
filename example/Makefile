.PHONY: clean

build: Dockerfile handler/* example.conf
	docker build -t serfnode_example .
	touch build

clean:
	rm build
