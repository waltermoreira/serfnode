.PHONY: clean

all: .build

.build: Dockerfile handler/* programs/* serfnode.conf
	docker build -t serfnode .
	touch .build

clean:
	rm .build
