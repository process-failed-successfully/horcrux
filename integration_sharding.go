package main

import (
	"fmt"
	"horcruxkv/internal/sharding"
)

func main() {
	// Test shard manager creation
	sm, err := sharding.NewShardManager(3, 1)
	if err != nil {
		fmt.Printf("Failed to create shard manager: %v\n", err)
		return
	}

	// Test storing and retrieving data
	testKey := "test_key"
	testValue := []byte("test_value")

	err = sm.Store(testKey, testValue)
	if err != nil {
		fmt.Printf("Failed to store data: %v\n", err)
		return
	}

	retrievedValue, err := sm.Get(testKey)
	if err != nil {
		fmt.Printf("Failed to retrieve data: %v\n", err)
		return
	}

	if string(retrievedValue) != string(testValue) {
		fmt.Printf("Retrieved value doesn't match stored value\n")
		return
	}

	// Test data distribution
	keys := []string{"key1", "key2", "key3", "key4", "key5"}
	for _, key := range keys {
		err = sm.Store(key, []byte(fmt.Sprintf("value_%s", key)))
		if err != nil {
			fmt.Printf("Failed to store key %s: %v\n", key, err)
			return
		}
	}

	// Verify all keys can be retrieved
	for _, key := range keys {
		val, err := sm.Get(key)
		if err != nil {
			fmt.Printf("Failed to retrieve key %s: %v\n", key, err)
			return
		}
		expected := fmt.Sprintf("value_%s", key)
		if string(val) != expected {
			fmt.Printf("Value mismatch for key %s\n", key)
			return
		}
	}

	fmt.Println("All sharding integration tests passed!")
}
