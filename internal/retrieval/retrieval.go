package retrieval

import (
	"errors"
	"horcruxkv/internal/storage"
)

// Retriever handles key-value retrieval operations
type Retriever struct {
	store *storage.Storage
}

// NewRetriever creates a new Retriever instance
func NewRetriever(store *storage.Storage) *Retriever {
	return &Retriever{
		store: store,
	}
}

// Get retrieves a value by key
func (r *Retriever) Get(key string) ([]byte, error) {
	if key == "" {
		return nil, errors.New("key cannot be empty")
	}

	value, err := r.store.Get(key)
	if err != nil {
		return nil, err
	}
	return value, nil
}

// GetString retrieves a value by key and returns it as a string
func (r *Retriever) GetString(key string) (string, error) {
	value, err := r.Get(key)
	if err != nil {
		return "", err
	}
	return string(value), nil
}

// Exists checks if a key exists in the store
func (r *Retriever) Exists(key string) (bool, error) {
	if key == "" {
		return false, errors.New("key cannot be empty")
	}
	return r.store.Has(key), nil
}
