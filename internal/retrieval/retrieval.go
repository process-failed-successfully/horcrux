package retrieval

import (
	"errors"
	"horcruxkv/internal/storage"
)

// Retriever handles retrieval operations
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

	return r.store.Get(key)
}

// GetMultiple retrieves multiple values by keys
func (r *Retriever) GetMultiple(keys []string) (map[string][]byte, error) {
	if len(keys) == 0 {
		return nil, errors.New("keys list cannot be empty")
	}

	result := make(map[string][]byte)
	for _, key := range keys {
		value, err := r.store.Get(key)
		if err != nil {
			return nil, err
		}
		result[key] = value
	}

	return result, nil
}

// Has checks if a key exists
func (r *Retriever) Has(key string) (bool, error) {
	if key == "" {
		return false, errors.New("key cannot be empty")
	}

	return r.store.Has(key), nil
}
