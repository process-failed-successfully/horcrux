package main

import (
	"fmt"
	"horcruxkv/internal/sharding"
)

func main() {
	// Initialize shard manager
	shardManager := sharding.NewShardManager(3)

	// Store a key-value pair
	key := "test_key"
	value := []byte("test_value")
	err := shardManager.Store(key, value)
	if err != nil {
		fmt.Printf("Error storing value: %v\n", err)
		return
	}

	// Retrieve the value
	retrieved, err := shardManager.Get(key)
	if err != nil {
		fmt.Printf("Error retrieving value: %v\n", err)
		return
	}

	// Verify the retrieved value
	if string(retrieved) == string(value) {
		fmt.Println("Sharding integration test passed: Retrieved value matches stored value")
	} else {
		fmt.Println("Sharding integration test failed: Retrieved value doesn't match stored value")
	}
}
