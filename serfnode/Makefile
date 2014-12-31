.PHONY: clean

build: Dockerfile handler/* programs/* serfnode.conf
	docker build -t serfnode .
	touch build

clean:
	rm build
