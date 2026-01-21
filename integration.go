package main

import (
	"fmt"
	"log"
	"horcruxkv/internal/storage"
	"horcruxkv/internal/retrieval"
)

func main() {
	// Initialize storage and retriever
	store := storage.NewStorage()
	retriever := retrieval.NewRetriever(store)

	// Test 1: Store and retrieve a key-value pair
	key := "test"
	value := "Hello, World!"
	store.Store(key, []byte(value))

	retrieved, err := retriever.GetString(key)
	if err != nil {
		log.Fatalf("Failed to retrieve value: %v", err)
	}

	if retrieved != value {
		log.Fatalf("Retrieved value doesn't match. Expected: %s, Got: %s", value, retrieved)
	}
	fmt.Printf("Successfully retrieved key '%s' with value '%s'\n", key, retrieved)

	// Test 2: Try to retrieve non-existent key
	_, err = retriever.Get("non_existent")
	if err == nil {
		log.Fatal("Expected error for non-existent key, got nil")
	}
	fmt.Println("Expected error for non-existent key")

	// Test 3: Check if key exists
	exists, err := retriever.Exists(key)
	if err != nil {
		log.Fatalf("Exists check failed: %v", err)
	}
	if !exists {
		log.Fatal("Expected key to exist")
	}
	fmt.Printf("Key '%s' exists: %t\n", key, exists)

	// Test 4: Check non-existent key
	exists, err = retriever.Exists("non_existent")
	if err != nil {
		log.Fatalf("Exists check failed: %v", err)
	}
	if exists {
		log.Fatal("Expected non-existent key to not exist")
	}
	fmt.Printf("Non-existent key exists: %t\n", exists)

	fmt.Println("All integration tests passed!")
}
