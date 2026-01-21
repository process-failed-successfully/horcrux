package main

import (
	"io/ioutil"
	"os"
	"path/filepath"
	"testing"
)

func TestAppendLogEntry(t *testing.T) {
	// Setup test environment
	testDir := "test_logs"
	os.Setenv("LOG_DIR", testDir)
	defer os.RemoveAll(testDir)

	// Test data
	testData := map[string]interface{}{
		"event": "test",
		"value": 123,
	}

	// Append entry
	err := appendLogEntry(testData)
	if err != nil {
		t.Fatalf("Failed to append log entry: %v", err)
	}

	// Verify file was created
	logFile := filepath.Join(testDir, logFileName)
	if _, err := os.Stat(logFile); os.IsNotExist(err) {
		t.Fatal("Log file was not created")
	}

	// Read and verify entry
	entries, err := readLogEntries()
	if err != nil {
		t.Fatalf("Failed to read log entries: %v", err)
	}

	if len(entries) != 1 {
		t.Fatalf("Expected 1 entry, got %d", len(entries))
	}

	entry := entries[0]
	if entry.Data.(map[string]interface{})["event"] != "test" {
		t.Errorf("Expected event 'test', got %v", entry.Data.(map[string]interface{})["event"])
	}
}

func TestReadLogEntries(t *testing.T) {
	// Setup test environment
	testDir := "test_logs_read"
	os.Setenv("LOG_DIR", testDir)
	defer os.RemoveAll(testDir)

	// Create test log file
	logFile := filepath.Join(testDir, logFileName)
	testData := `{"id":"test-1","timestamp":"2023-01-01T00:00:00Z","data":{"event":"test"}}
{"id":"test-2","timestamp":"2023-01-01T00:00:01Z","data":{"event":"test2"}}`

	err := ioutil.WriteFile(logFile, []byte(testData), 0644)
	if err != nil {
		t.Fatalf("Failed to create test log file: %v", err)
	}

	// Read entries
	entries, err := readLogEntries()
	if err != nil {
		t.Fatalf("Failed to read log entries: %v", err)
	}

	if len(entries) != 2 {
		t.Fatalf("Expected 2 entries, got %d", len(entries))
	}

	if entries[0].ID != "test-1" {
		t.Errorf("Expected first entry ID 'test-1', got %s", entries[0].ID)
	}
}

func TestImmutableLog(t *testing.T) {
	// Setup test environment
	testDir := "test_logs_immutable"
	os.Setenv("LOG_DIR", testDir)
	defer os.RemoveAll(testDir)

	// Append initial entry
	testData := map[string]interface{}{
		"event": "original",
	}
	err := appendLogEntry(testData)
	if err != nil {
		t.Fatalf("Failed to append log entry: %v", err)
	}

	// Try to append another entry
	testData2 := map[string]interface{}{
		"event": "second",
	}
	err = appendLogEntry(testData2)
	if err != nil {
		t.Fatalf("Failed to append second log entry: %v", err)
	}

	// Verify both entries exist
	entries, err := readLogEntries()
	if err != nil {
		t.Fatalf("Failed to read log entries: %v", err)
	}

	if len(entries) != 2 {
		t.Fatalf("Expected 2 entries, got %d", len(entries))
	}

	// Verify first entry is unchanged
	if entries[0].Data.(map[string]interface{})["event"] != "original" {
		t.Errorf("First entry was modified, expected 'original', got %v",
			entries[0].Data.(map[string]interface{})["event"])
	}
}
