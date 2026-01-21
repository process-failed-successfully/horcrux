package retrieval

import (
	"testing"
	"horcruxkv/internal/storage"
)

func TestRetrieveKeyValue(t *testing.T) {
	store := storage.NewStorage()
	retrieval := NewRetrieval(store)

	key := "test_key"
	value := []byte("test_value")

	// Store the value first
	err := store.Store(key, value)
	if err != nil {
		t.Fatalf("Failed to store value: %v", err)
	}

	// Retrieve the value
	retrieved, err := retrieval.Get(key)
	if err != nil {
		t.Fatalf("Failed to retrieve value: %v", err)
	}

	if string(retrieved) != string(value) {
		t.Errorf("Retrieved value doesn't match stored value")
	}
}

func TestRetrieveEmptyKey(t *testing.T) {
	store := storage.NewStorage()
	retrieval := NewRetrieval(store)

	_, err := retrieval.Get("")
	if err == nil {
		t.Error("Expected error for empty key")
	}
}

func TestRetrieveMultipleKeys(t *testing.T) {
	store := storage.NewStorage()
	retrieval := NewRetrieval(store)

	keys := []string{"key1", "key2", "key3"}
	values := [][]byte{[]byte("value1"), []byte("value2"), []byte("value3")}

	// Store multiple values
	for i := range keys {
		err := store.Store(keys[i], values[i])
		if err != nil {
			t.Fatalf("Failed to store value: %v", err)
		}
	}

	// Retrieve all values
	for i := range keys {
		retrieved, err := retrieval.Get(keys[i])
		if err != nil {
			t.Fatalf("Failed to retrieve value: %v", err)
		}

		if string(retrieved) != string(values[i]) {
			t.Errorf("Retrieved value doesn't match stored value for key %s", keys[i])
		}
	}
}

func TestRetrieveAfterUpdate(t *testing.T) {
	store := storage.NewStorage()
	retrieval := NewRetrieval(store)

	key := "test_key"
	value1 := []byte("value1")
	value2 := []byte("value2")

	// Store initial value
	err := store.Store(key, value1)
	if err != nil {
		t.Fatalf("Failed to store value: %v", err)
	}

	// Update the value
	err = store.Store(key, value2)
	if err != nil {
		t.Fatalf("Failed to update value: %v", err)
	}

	// Retrieve the updated value
	retrieved, err := retrieval.Get(key)
	if err != nil {
		t.Fatalf("Failed to retrieve value: %v", err)
	}

	if string(retrieved) != string(value2) {
		t.Errorf("Retrieved value doesn't match updated value")
	}
}

func TestHasKey(t *testing.T) {
	store := storage.NewStorage()
	retrieval := NewRetrieval(store)

	key := "test_key"
	value := []byte("test_value")

	// Key should not exist initially
	if retrieval.Has(key) {
		t.Error("Key should not exist initially")
	}

	// Store the value
	err := store.Store(key, value)
	if err != nil {
		t.Fatalf("Failed to store value: %v", err)
	}

	// Key should exist after storage
	if !retrieval.Has(key) {
		t.Error("Key should exist after storage")
	}

	// Delete the value
	err = store.Delete(key)
	if err != nil {
		t.Fatalf("Failed to delete value: %v", err)
	}

	// Key should not exist after deletion
	if retrieval.Has(key) {
		t.Error("Key should not exist after deletion")
	}
}
