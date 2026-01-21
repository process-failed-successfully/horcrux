// Package retrieval provides functionality to retrieve key-value pairs from storage
package retrieval

import (
	"errors"
	"horcruxkv/internal/storage"
)

// Retriever handles retrieval operations from storage
type Retriever struct {
	store *storage.Storage
}

// NewRetriever creates a new Retriever instance
func NewRetriever(store *storage.Storage) *Retriever {
	return &Retriever{
		store: store,
	}
}

// Get retrieves a value by key from storage
// Returns the value and a boolean indicating if the key exists
// Returns an error if the key is empty
func (r *Retriever) Get(key string) (interface{}, bool, error) {
	if key == "" {
		return nil, false, errors.New("key cannot be empty")
	}

	value, exists := r.store.Get(key)
	return value, exists, nil
}

// GetMultiple retrieves multiple values by keys from storage
// Returns a map of key-value pairs for existing keys
// Returns an error if any key is empty
func (r *Retriever) GetMultiple(keys []string) (map[string]interface{}, error) {
	result := make(map[string]interface{})

	for _, key := range keys {
		if key == "" {
			return nil, errors.New("key cannot be empty")
		}

		if value, exists := r.store.Get(key); exists {
			result[key] = value
		}
	}

	return result, nil
}
