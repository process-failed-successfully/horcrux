package storage

import (
	"testing"

	"github.com/stretchr/testify/assert"
)

func TestStoreAndGet(t *testing.T) {
	store := NewStorage()

	// Test storing and retrieving a key-value pair
	key := "test"
	value := []byte("data")

	err := store.Store(key, value)
	assert.NoError(t, err)

	retrieved, err := store.Get(key)
	assert.NoError(t, err)
	assert.Equal(t, value, retrieved)
}

func TestStoreEmptyKey(t *testing.T) {
	store := NewStorage()

	err := store.Store("", []byte("data"))
	assert.Error(t, err)
	assert.Equal(t, "key cannot be empty", err.Error())
}

func TestStoreNilValue(t *testing.T) {
	store := NewStorage()

	err := store.Store("test", nil)
	assert.Error(t, err)
	assert.Equal(t, "value cannot be nil", err.Error())
}

func TestGetNonExistentKey(t *testing.T) {
	store := NewStorage()

	_, err := store.Get("nonexistent")
	assert.Error(t, err)
	assert.Equal(t, "key not found", err.Error())
}

func TestGetEmptyKey(t *testing.T) {
	store := NewStorage()

	_, err := store.Get("")
	assert.Error(t, err)
	assert.Equal(t, "key cannot be empty", err.Error())
}

func TestOverwriteKey(t *testing.T) {
	store := NewStorage()

	key := "test"
	value1 := []byte("data1")
	value2 := []byte("data2")

	err := store.Store(key, value1)
	assert.NoError(t, err)

	err = store.Store(key, value2)
	assert.NoError(t, err)

	retrieved, err := store.Get(key)
	assert.NoError(t, err)
	assert.Equal(t, value2, retrieved)
}

func TestHas(t *testing.T) {
	store := NewStorage()

	store.Store("test", []byte("data"))

	assert.True(t, store.Has("test"))
	assert.False(t, store.Has("nonexistent"))
	assert.False(t, store.Has(""))
}

func TestDelete(t *testing.T) {
	store := NewStorage()

	store.Store("test", []byte("data"))
	assert.True(t, store.Has("test"))

	err := store.Delete("test")
	assert.NoError(t, err)
	assert.False(t, store.Has("test"))
}

func TestConcurrentAccess(t *testing.T) {
	store := NewStorage()

	// Store multiple values concurrently
	for i := 0; i < 100; i++ {
		go func(i int) {
			key := string(rune(i))
			value := []byte(string(rune(i + 1)))
			store.Store(key, value)
		}(i)
	}

	// Retrieve values concurrently
	for i := 0; i < 100; i++ {
		go func(i int) {
			key := string(rune(i))
			_, _ = store.Get(key)
		}(i)
	}
}
