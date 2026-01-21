package retrieval

import (
	"testing"
	"horcruxkv/internal/storage"
)

func TestGet(t *testing.T) {
	store := storage.NewStorage()
	retriever := NewRetriever(store)

	key := "test_key"
	value := []byte("test_value")

	// Store a value first
	err := store.Store(key, value)
	if err != nil {
		t.Fatalf("Failed to store value: %v", err)
	}

	// Retrieve the value
	retrieved, err := retriever.Get(key)
	if err != nil {
		t.Fatalf("Failed to retrieve value: %v", err)
	}

	if string(retrieved) != string(value) {
		t.Errorf("Retrieved value doesn't match stored value")
	}
}

func TestGetNonExistentKey(t *testing.T) {
	store := storage.NewStorage()
	retriever := NewRetriever(store)

	_, err := retriever.Get("non_existent_key")
	if err == nil {
		t.Error("Expected error for non-existent key")
	}
}

func TestEmptyKey(t *testing.T) {
	store := storage.NewStorage()
	retriever := NewRetriever(store)

	_, err := retriever.Get("")
	if err == nil {
		t.Error("Expected error for empty key")
	}
}

func TestGetMultiple(t *testing.T) {
	store := storage.NewStorage()
	retriever := NewRetriever(store)

	// Store multiple values
	keys := []string{"key1", "key2", "key3"}
	for _, key := range keys {
		err := store.Store(key, []byte("value_"+key))
		if err != nil {
			t.Fatalf("Failed to store value for key %s: %v", key, err)
		}
	}

	// Retrieve multiple values
	results, err := retriever.GetMultiple(keys)
	if err != nil {
		t.Fatalf("Failed to retrieve multiple values: %v", err)
	}

	// Verify all values
	for _, key := range keys {
		expected := "value_" + key
		if string(results[key]) != expected {
			t.Errorf("Value mismatch for key %s", key)
		}
	}
}

func TestGetMultipleWithNonExistentKey(t *testing.T) {
	store := storage.NewStorage()
	retriever := NewRetriever(store)

	// Store one value
	err := store.Store("key1", []byte("value_key1"))
	if err != nil {
		t.Fatalf("Failed to store value: %v", err)
	}

	// Try to retrieve with non-existent key
	_, err = retriever.GetMultiple([]string{"key1", "non_existent"})
	if err == nil {
		t.Error("Expected error for non-existent key in multiple retrieval")
	}
}

func TestHas(t *testing.T) {
	store := storage.NewStorage()
	retriever := NewRetriever(store)

	key := "test_key"
	value := []byte("test_value")

	// Key should not exist initially
	exists, err := retriever.Has(key)
	if err != nil {
		t.Fatalf("Failed to check key existence: %v", err)
	}
	if exists {
		t.Error("Key should not exist initially")
	}

	// Store the value
	err = store.Store(key, value)
	if err != nil {
		t.Fatalf("Failed to store value: %v", err)
	}

	// Key should exist now
	exists, err = retriever.Has(key)
	if err != nil {
		t.Fatalf("Failed to check key existence: %v", err)
	}
	if !exists {
		t.Error("Key should exist after storage")
	}
}
