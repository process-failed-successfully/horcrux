package storage

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestRetrieveKeyValue(t *testing.T) {
	store := NewStorage()

	// Step 1: Store a key-value pair
	key := "test"
	value := []byte("data")

	err := store.Store(key, value)
	assert.NoError(t, err)

	// Step 2: Retrieve the value using the key
	retrieved, err := store.Get(key)
	assert.NoError(t, err)

	// Step 3: Verify the retrieved value matches the stored value
	assert.Equal(t, value, retrieved)
	assert.Equal(t, "data", string(retrieved))

	// Step 4: Check for error handling on non-existent keys
	_, err = store.Get("nonexistent")
	assert.Error(t, err)
	assert.Equal(t, "key not found", err.Error())
}

func TestRetrieveEmptyKey(t *testing.T) {
	store := NewStorage()

	_, err := store.Get("")
	assert.Error(t, err)
	assert.Equal(t, "key cannot be empty", err.Error())
}

func TestRetrieveMultipleKeys(t *testing.T) {
	store := NewStorage()

	// Store multiple key-value pairs
	store.Store("key1", []byte("value1"))
	store.Store("key2", []byte("value2"))
	store.Store("key3", []byte("value3"))

	// Retrieve and verify each one
	val1, _ := store.Get("key1")
	assert.Equal(t, "value1", string(val1))

	val2, _ := store.Get("key2")
	assert.Equal(t, "value2", string(val2))

	val3, _ := store.Get("key3")
	assert.Equal(t, "value3", string(val3))
}

func TestRetrieveAfterUpdate(t *testing.T) {
	store := NewStorage()

	// Store initial value
	store.Store("test", []byte("initial"))

	// Retrieve initial value
	val, _ := store.Get("test")
	assert.Equal(t, "initial", string(val))

	// Update the value
	store.Store("test", []byte("updated"))

	// Retrieve updated value
	val, _ = store.Get("test")
	assert.Equal(t, "updated", string(val))
}
