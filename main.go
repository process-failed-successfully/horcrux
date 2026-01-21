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
	logDir      = "data/logs"
	logFileName = "log.jsonl"
)

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
	file, err := os.OpenFile(logFile, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
	if err != nil {
		return fmt.Errorf("failed to open log file: %v", err)
	}
	defer file.Close()

	if _, err := file.Write(append(jsonData, '\n')); err != nil {
		return fmt.Errorf("failed to write to log file: %v", err)
	}

	return nil
}

func readLogEntries() ([]LogEntry, error) {
	logFile := getLogFilePath()
	data, err := ioutil.ReadFile(logFile)
	if err != nil {
		if os.IsNotExist(err) {
			return []LogEntry{}, nil
		}
		return nil, fmt.Errorf("failed to read log file: %v", err)
	}

	var entries []LogEntry
	for _, line := range splitLines(string(data)) {
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
	start := 0
	for i := 0; i < len(s); i++ {
		if s[i] == '\n' {
			lines = append(lines, s[start:i])
			start = i + 1
		}
	}
	if start < len(s) {
		lines = append(lines, s[start:])
	}
	return lines
}

func main() {
	if len(os.Args) < 2 {
		fmt.Println("Usage: local-storage <command> [args]")
		fmt.Println("Commands:")
		fmt.Println("  append <data>  - Append a log entry")
		fmt.Println("  read           - Read all log entries")
		os.Exit(1)
	}

	command := os.Args[1]

	switch command {
	case "append":
		if len(os.Args) < 3 {
			fmt.Println("Error: Missing data argument for append command")
			os.Exit(1)
		}

		data := os.Args[2]
		var parsedData interface{}
		if err := json.Unmarshal([]byte(data), &parsedData); err != nil {
			fmt.Printf("Error: Invalid JSON data: %v\n", err)
			os.Exit(1)
		}

		if err := appendLogEntry(parsedData); err != nil {
			fmt.Printf("Error: Failed to append log entry: %v\n", err)
			os.Exit(1)
		}

		fmt.Println("Log entry appended successfully")

	case "read":
		entries, err := readLogEntries()
		if err != nil {
			fmt.Printf("Error: Failed to read log entries: %v\n", err)
			os.Exit(1)
		}

		for _, entry := range entries {
			fmt.Printf("ID: %s, Timestamp: %s, Data: %v\n",
				entry.ID, entry.Timestamp.Format(time.RFC3339), entry.Data)
		}

	default:
		fmt.Printf("Error: Unknown command '%s'\n", command)
		os.Exit(1)
	}
}
