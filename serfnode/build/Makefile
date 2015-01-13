.PHONY: clean

all: .build

.build: Dockerfile handler/* programs/* serfnode.conf serf me.py
	docker build -t serfnode .
	touch .build

clean:
	rm .build
