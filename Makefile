# Makefile for Shamir's Secret Sharing

.PHONY: all clean test build run-split

all: build

clean:
	rm -f cmd/split/split
	rm -f internal/combine/combine
	rm -f internal/edge/edge

test:
	cd internal/split && go test -v

build:
	cd cmd/split && go build -o split

run-split:
	cd cmd/split && go run main.go --secret "Hello" --shares 5 --threshold 3
