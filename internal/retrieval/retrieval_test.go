// Package retrieval provides functionality to retrieve key-value pairs from storage
package retrieval

import (
	"errors"
	"testing"
	"horcruxkv/internal/storage"
)

func TestGet(t *testing.T) {
	store := storage.NewStorage()
	retriever := NewRetriever(store)

	// Test retrieving non-existent key
	_, exists, err := retriever.Get("non-existent")
	if err != nil {
		t.Errorf("Expected no error for non-existent key, got: %v", err)
	}
	if exists {
		t.Error("Expected exists to be false for non-existent key")
	}

	// Store a value
	store.Set("test-key", "test-value")

	// Test retrieving existing key
	value, exists, err := retriever.Get("test-key")
	if err != nil {
		t.Errorf("Expected no error, got: %v", err)
	}
	if !exists {
		t.Error("Expected exists to be true")
	}
	if value != "test-value" {
		t.Errorf("Expected value to be 'test-value', got: %v", value)
	}
}

func TestGetEmptyKey(t *testing.T) {
	store := storage.NewStorage()
	retriever := NewRetriever(store)

	_, _, err := retriever.Get("")
	if err == nil {
		t.Error("Expected error for empty key")
	}
	if err.Error() != "key cannot be empty" {
		t.Errorf("Expected error message 'key cannot be empty', got: %v", err.Error())
	}
}

func TestGetMultiple(t *testing.T) {
	store := storage.NewStorage()
	retriever := NewRetriever(store)

	// Store some values
	store.Set("key1", "value1")
	store.Set("key2", "value2")
	store.Set("key3", "value3")

	// Test retrieving multiple keys
	keys := []string{"key1", "key2", "key4"}
	result, err := retriever.GetMultiple(keys)
	if err != nil {
		t.Errorf("Expected no error, got: %v", err)
	}

	// Check that only existing keys are returned
	if len(result) != 2 {
		t.Errorf("Expected 2 results, got: %d", len(result))
	}
	if result["key1"] != "value1" {
		t.Errorf("Expected value1, got: %v", result["key1"])
	}
	if result["key2"] != "value2" {
		t.Errorf("Expected value2, got: %v", result["key2"])
	}
	if _, exists := result["key4"]; exists {
		t.Error("Expected key4 to not be in result")
	}
}

func TestGetMultipleWithEmptyKey(t *testing.T) {
	store := storage.NewStorage()
	retriever := NewRetriever(store)

	keys := []string{"key1", "", "key2"}
	_, err := retriever.GetMultiple(keys)
	if err == nil {
		t.Error("Expected error for empty key in list")
	}
	if err.Error() != "key cannot be empty" {
		t.Errorf("Expected error message 'key cannot be empty', got: %v", err.Error())
	}
}

func TestRetrieverIntegration(t *testing.T) {
	store := storage.NewStorage()
	retriever := NewRetriever(store)

	// Store multiple values
	store.Set("name", "Alice")
	store.Set("age", 30)
	store.Set("city", "New York")

	// Retrieve and verify
	name, exists, err := retriever.Get("name")
	if err != nil || !exists || name != "Alice" {
		t.Errorf("Failed to retrieve name: err=%v, exists=%v, value=%v", err, exists, name)
	}

	age, exists, err := retriever.Get("age")
	if err != nil || !exists || age != 30 {
		t.Errorf("Failed to retrieve age: err=%v, exists=%v, value=%v", err, exists, age)
	}

	// Test non-existent key
	_, exists, err = retriever.Get("country")
	if err != nil {
		t.Errorf("Unexpected error for non-existent key: %v", err)
	}
	if exists {
		t.Error("Expected exists to be false for non-existent key")
	}
}
