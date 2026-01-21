package main

import (
	"fmt"
	"log"
	"os"
	"os/signal"
	"syscall"

	"horcruxkv/internal/storage"
)

func main() {
	// Create storage instance
	store := storage.NewStorage()

	// Store some test data
	err := store.Store("test", []byte("Hello, HorcruxKV!"))
	if err != nil {
		log.Fatalf("Failed to store data: %v", err)
	}

	// Retrieve the data
	value, err := store.Get("test")
	if err != nil {
		log.Fatalf("Failed to retrieve data: %v", err)
	}

	fmt.Printf("Stored and retrieved value: %s\n", string(value))

	// Wait for interrupt signal
	sigChan := make(chan os.Signal, 1)
	signal.Notify(sigChan, syscall.SIGINT, syscall.SIGTERM)
	<-sigChan

	fmt.Println("Shutting down...")
}
