package main

import (
	"fmt"
	"log"
	"testing"

	"horcruxkv/internal/storage"
)

func TestRetrieveKeyValueIntegration(t *testing.T) {
	// Step 1: Create storage instance
	store := storage.NewStorage()

	// Step 2: Store a key-value pair
	key := "test"
	value := []byte("data")

	err := store.Store(key, value)
	if err != nil {
		t.Fatalf("Step 2 failed: Failed to store key-value pair: %v", err)
	}
	fmt.Println("Step 2: Successfully stored key-value pair")

	// Step 3: Retrieve the value using the key
	retrieved, err := store.Get(key)
	if err != nil {
		t.Fatalf("Step 3 failed: Failed to retrieve value: %v", err)
	}
	fmt.Println("Step 3: Successfully retrieved value")

	// Step 4: Verify the retrieved value matches the stored value
	if string(retrieved) != string(value) {
		t.Fatalf("Step 3 failed: Retrieved value '%s' does not match stored value '%s'", string(retrieved), string(value))
	}
	fmt.Println("Step 3: Verified retrieved value matches stored value")

	// Step 5: Check for error handling on non-existent keys
	_, err = store.Get("nonexistent")
	if err == nil {
		t.Fatal("Step 4 failed: Expected error for non-existent key")
	}
	if err.Error() != "key not found" {
		t.Fatalf("Step 4 failed: Expected 'key not found' error, got '%v'", err)
	}
	fmt.Println("Step 4: Verified error handling for non-existent keys")
}

func main() {
	// Run the integration test
	t := &testing.T{}
	TestRetrieveKeyValueIntegration(t)

	if !t.Failed() {
		fmt.Println("\n✓ All integration tests passed!")
	} else {
		log.Fatal("Integration tests failed")
	}
}
