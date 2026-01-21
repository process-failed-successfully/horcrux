package main

import (
	"encoding/json"
	"fmt"
	"io/ioutil"
	"os"
	"path/filepath"
	"time"
)

const (
	logFileName = "log.jsonl"
)

var (
	logDir = "data/logs"
)

func init() {
	// Allow override via environment variable for testing
	if envDir := os.Getenv("LOG_DIR"); envDir != "" {
		logDir = envDir
	}
}

type LogEntry struct {
	ID        string      `json:"id"`
	Timestamp time.Time   `json:"timestamp"`
	Data      interface{} `json:"data"`
}

func ensureLogDir() error {
	if _, err := os.Stat(logDir); os.IsNotExist(err) {
		return os.MkdirAll(logDir, 0755)
	}
	return nil
}

func getLogFilePath() string {
	return filepath.Join(logDir, logFileName)
}

func appendLogEntry(data interface{}) error {
	// Ensure log directory exists
	if err := ensureLogDir(); err != nil {
		return fmt.Errorf("failed to create log directory: %v", err)
	}

	// Create log entry
	entry := LogEntry{
		ID:        fmt.Sprintf("entry-%d", time.Now().UnixNano()),
		Timestamp: time.Now(),
		Data:      data,
	}

	// Marshal to JSON
	jsonData, err := json.Marshal(entry)
	if err != nil {
		return fmt.Errorf("failed to marshal log entry: %v", err)
	}

	// Append to log file
	logFile := getLogFilePath()
	f, err := os.OpenFile(logFile, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
	if err != nil {
		return fmt.Errorf("failed to open log file: %v", err)
	}
	defer f.Close()

	if _, err := f.Write(append(jsonData, '\n')); err != nil {
		return fmt.Errorf("failed to write to log file: %v", err)
	}

	return nil
}

func readLogEntries() ([]LogEntry, error) {
	logFile := getLogFilePath()

	// Check if file exists
	if _, err := os.Stat(logFile); os.IsNotExist(err) {
		return []LogEntry{}, nil
	}

	// Read file
	content, err := ioutil.ReadFile(logFile)
	if err != nil {
		return nil, fmt.Errorf("failed to read log file: %v", err)
	}

	// Parse JSON lines
	var entries []LogEntry
	for _, line := range splitLines(string(content)) {
		if line == "" {
			continue
		}

		var entry LogEntry
		if err := json.Unmarshal([]byte(line), &entry); err != nil {
			return nil, fmt.Errorf("failed to unmarshal log entry: %v", err)
		}

		entries = append(entries, entry)
	}

	return entries, nil
}

func splitLines(s string) []string {
	var lines []string
	var current string

	for _, r := range s {
		if r == '\n' {
			lines = append(lines, current)
			current = ""
		} else {
			current += string(r)
		}
	}

	if current != "" {
		lines = append(lines, current)
	}

	return lines
}

func main() {
	if len(os.Args) < 2 {
		fmt.Println("Usage: local-storage <command> [args]")
		fmt.Println("Commands:")
		fmt.Println("  append <json-data>  - Append a log entry")
		fmt.Println("  read                - Read all log entries")
		os.Exit(1)
	}

	command := os.Args[1]

	switch command {
	case "append":
		if len(os.Args) < 3 {
			fmt.Println("Usage: local-storage append <json-data>")
			os.Exit(1)
		}

		var data map[string]interface{}
		if err := json.Unmarshal([]byte(os.Args[2]), &data); err != nil {
			fmt.Printf("Error: invalid JSON data: %v\n", err)
			os.Exit(1)
		}

		if err := appendLogEntry(data); err != nil {
			fmt.Printf("Error: failed to append log entry: %v\n", err)
			os.Exit(1)
		}

		fmt.Println("Log entry appended successfully")

	case "read":
		entries, err := readLogEntries()
		if err != nil {
			fmt.Printf("Error: failed to read log entries: %v\n", err)
			os.Exit(1)
		}

		for _, entry := range entries {
			fmt.Printf("ID: %s, Timestamp: %s, Data: %v\n", entry.ID, entry.Timestamp.Format(time.RFC3339), entry.Data)
		}

	default:
		fmt.Printf("Error: unknown command '%s'\n", command)
		os.Exit(1)
	}
}
