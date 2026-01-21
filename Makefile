# Makefile for Shamir's Secret Sharing

.PHONY: all clean test build run-split run-combine

all: build

clean:
	rm -f cmd/split/split
	rm -f cmd/combine/combine
	rm -f internal/edge/edge

test:
	cd internal/split && go test -v
	cd internal/combine && go test -v

build:
	cd cmd/split && go build -o split
	cd cmd/combine && go build -o combine

run-split:
	cd cmd/split && go run main.go --secret "Hello" --shares 5 --threshold 3

run-combine:
	cd cmd/combine && go run main.go --shares "1,122928063121537008206361213584414899535421367223168767925645095452074462689534 2,382871791567658475181379758099882999778420045970797548471618952758731769618957 3,779831185338364400925055633546404300728996036242886341637921571920282860038044" --threshold 3
