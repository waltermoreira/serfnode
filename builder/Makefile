.PHONY: clean

all: .build

.build: Dockerfile entry.sh template/* roles_template/*
	docker build -t serfnode_init .
	touch .build

clean:
	rm -rf .build
