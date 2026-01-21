.PHONY: build run clean

build:
	go build

run:
	go run main.go

clean:
	rm -f horcrux
