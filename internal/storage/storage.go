package storage

import (
	"errors"
	"sync"
)

// Storage represents a simple key-value store
type Storage struct {
	data map[string][]byte
	mu   sync.RWMutex
}

// NewStorage creates a new Storage instance
func NewStorage() *Storage {
	return &Storage{
		data: make(map[string][]byte),
	}
}

// Store stores a key-value pair
func (s *Storage) Store(key string, value []byte) error {
	if key == "" {
		return errors.New("key cannot be empty")
	}
	if value == nil {
		return errors.New("value cannot be nil")
	}

	s.mu.Lock()
	defer s.mu.Unlock()

	s.data[key] = value
	return nil
}

// Get retrieves a value by key
func (s *Storage) Get(key string) ([]byte, error) {
	if key == "" {
		return nil, errors.New("key cannot be empty")
	}

	s.mu.RLock()
	defer s.mu.RUnlock()

	value, exists := s.data[key]
	if !exists {
		return nil, errors.New("key not found")
	}

	return value, nil
}

// Delete removes a key-value pair
func (s *Storage) Delete(key string) error {
	if key == "" {
		return errors.New("key cannot be empty")
	}

	s.mu.Lock()
	defer s.mu.Unlock()

	delete(s.data, key)
	return nil
}

// Has checks if a key exists
func (s *Storage) Has(key string) bool {
	if key == "" {
		return false
	}

	s.mu.RLock()
	defer s.mu.RUnlock()

	_, exists := s.data[key]
	return exists
}
