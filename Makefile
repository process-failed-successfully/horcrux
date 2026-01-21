# Makefile for horcrux-node gRPC server

.PHONY: init
init:
	./init.sh

.PHONY: proto
proto:
	protoc --go_out=. --go-grpc_out=. proto/*.proto

.PHONY: build
build:
	go build -o horcrux-node

.PHONY: run
run:
	go run .

.PHONY: clean
clean:
	rm -f horcrux-node

.PHONY: test
test:
	go test ./...
