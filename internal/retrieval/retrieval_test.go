package retrieval

import (
	"testing"
	"horcruxkv/internal/storage"
)

func TestRetrieveKeyValue(t *testing.T) {
	store := storage.NewStorage()
	retriever := NewRetriever(store)

	// Store a test value
	key := "test"
	value := []byte("test_data")
	store.Store(key, value)

	// Retrieve the value
	retrieved, err := retriever.Get(key)
	if err != nil {
		t.Fatalf("Failed to retrieve value: %v", err)
	}

	if string(retrieved) != string(value) {
		t.Errorf("Retrieved value doesn't match. Expected: %s, Got: %s", string(value), string(retrieved))
	}
}

func TestRetrieveNonExistentKey(t *testing.T) {
	store := storage.NewStorage()
	retriever := NewRetriever(store)

	_, err := retriever.Get("non_existent_key")
	if err == nil {
		t.Error("Expected error for non-existent key, got nil")
	}
}

func TestRetrieveEmptyKey(t *testing.T) {
	store := storage.NewStorage()
	retriever := NewRetriever(store)

	_, err := retriever.Get("")
	if err == nil {
		t.Error("Expected error for empty key, got nil")
	}
}

func TestGetString(t *testing.T) {
	store := storage.NewStorage()
	retriever := NewRetriever(store)

	key := "test"
	value := "test_string"
	store.Store(key, []byte(value))

	result, err := retriever.GetString(key)
	if err != nil {
		t.Fatalf("Failed to retrieve string: %v", err)
	}

	if result != value {
		t.Errorf("Retrieved string doesn't match. Expected: %s, Got: %s", value, result)
	}
}

func TestExists(t *testing.T) {
	store := storage.NewStorage()
	retriever := NewRetriever(store)

	key := "test"
	store.Store(key, []byte("value"))

	exists, err := retriever.Exists(key)
	if err != nil {
		t.Fatalf("Exists check failed: %v", err)
	}
	if !exists {
		t.Error("Expected key to exist")
	}

	exists, err = retriever.Exists("non_existent")
	if err != nil {
		t.Fatalf("Exists check failed: %v", err)
	}
	if exists {
		t.Error("Expected non-existent key to not exist")
	}
}

func TestExistsEmptyKey(t *testing.T) {
	store := storage.NewStorage()
	retriever := NewRetriever(store)

	_, err := retriever.Exists("")
	if err == nil {
		t.Error("Expected error for empty key, got nil")
	}
}
