package storage

import (
	"testing"
)

func TestStoreAndRetrieve(t *testing.T) {
	store := NewStorage()

	// Test storing and retrieving a value
	key := "test_key"
	value := []byte("test_value")

	err := store.Store(key, value)
	if err != nil {
		t.Fatalf("Failed to store value: %v", err)
	}

	retrieved, err := store.Get(key)
	if err != nil {
		t.Fatalf("Failed to retrieve value: %v", err)
	}

	if string(retrieved) != string(value) {
		t.Errorf("Retrieved value doesn't match stored value")
	}
}

func TestGetNonExistentKey(t *testing.T) {
	store := NewStorage()

	_, err := store.Get("non_existent_key")
	if err == nil {
		t.Error("Expected error for non-existent key")
	}
}

func TestEmptyKey(t *testing.T) {
	store := NewStorage()

	err := store.Store("", []byte("value"))
	if err == nil {
		t.Error("Expected error for empty key")
	}

	_, err = store.Get("")
	if err == nil {
		t.Error("Expected error for empty key")
	}
}

func TestNilValue(t *testing.T) {
	store := NewStorage()

	err := store.Store("key", nil)
	if err == nil {
		t.Error("Expected error for nil value")
	}
}

func TestDelete(t *testing.T) {
	store := NewStorage()

	key := "test_key"
	value := []byte("test_value")

	err := store.Store(key, value)
	if err != nil {
		t.Fatalf("Failed to store value: %v", err)
	}

	err = store.Delete(key)
	if err != nil {
		t.Fatalf("Failed to delete value: %v", err)
	}

	_, err = store.Get(key)
	if err == nil {
		t.Error("Expected error after deletion")
	}
}

func TestHas(t *testing.T) {
	store := NewStorage()

	key := "test_key"
	value := []byte("test_value")

	if store.Has(key) {
		t.Error("Key should not exist initially")
	}

	err := store.Store(key, value)
	if err != nil {
		t.Fatalf("Failed to store value: %v", err)
	}

	if !store.Has(key) {
		t.Error("Key should exist after storage")
	}

	err = store.Delete(key)
	if err != nil {
		t.Fatalf("Failed to delete value: %v", err)
	}

	if store.Has(key) {
		t.Error("Key should not exist after deletion")
	}
}
