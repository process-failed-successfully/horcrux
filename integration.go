package main

import (
	"fmt"
	"horcruxkv/internal/retrieval"
	"horcruxkv/internal/storage"
)

func main() {
	// Initialize storage
	store := storage.NewStorage()

	// Initialize retrieval
	retriever := retrieval.NewRetrieval(store)

	// Store a key-value pair
	key := "test_key"
	value := []byte("test_value")
	err := store.Store(key, value)
	if err != nil {
		fmt.Printf("Error storing value: %v\n", err)
		return
	}

	// Retrieve the value
	retrieved, err := retriever.Get(key)
	if err != nil {
		fmt.Printf("Error retrieving value: %v\n", err)
		return
	}

	// Verify the retrieved value
	if string(retrieved) == string(value) {
		fmt.Println("Integration test passed: Retrieved value matches stored value")
	} else {
		fmt.Println("Integration test failed: Retrieved value doesn't match stored value")
	}
}
