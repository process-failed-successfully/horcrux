.PHONY: setup test run clean cli

setup:
	chmod +x init.sh
	./init.sh

test:
	go test ./...

run:
	go run cmd/server/main.go

cli:
	go run cmd/cli/main.go

clean:
	go clean
