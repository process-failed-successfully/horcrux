package retrieval

import (
	"errors"
	"horcruxkv/internal/storage"
)

// Retrieval wraps a storage instance to provide retrieval functionality
type Retrieval struct {
	store *storage.Storage
}

// NewRetrieval creates a new Retrieval instance
func NewRetrieval(store *storage.Storage) *Retrieval {
	return &Retrieval{
		store: store,
	}
}

// Get retrieves a value by key
func (r *Retrieval) Get(key string) ([]byte, error) {
	if key == "" {
		return nil, errors.New("key cannot be empty")
	}

	value, err := r.store.Get(key)
	if err != nil {
		return nil, err
	}

	return value, nil
}

// Has checks if a key exists
func (r *Retrieval) Has(key string) bool {
	if key == "" {
		return false
	}

	return r.store.Has(key)
}
