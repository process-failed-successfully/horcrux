package main

import (
	"flag"
	"fmt"
	"log"
	"os"

	"horcruxkv/internal/storage"
)

func main() {
	// Parse command line flags
	storeCmd := flag.NewFlagSet("store", flag.ExitOnError)
	getCmd := flag.NewFlagSet("get", flag.ExitOnError)
	deleteCmd := flag.NewFlagSet("delete", flag.ExitOnError)
	hasCmd := flag.NewFlagSet("has", flag.ExitOnError)

	if len(os.Args) < 2 {
		fmt.Println("Usage: horcruxkv <command> [arguments]")
		fmt.Println("Commands:")
		fmt.Println("  store <key> <value>  Store a key-value pair")
		fmt.Println("  get <key>             Get the value for a key")
		fmt.Println("  delete <key>          Delete a key-value pair")
		fmt.Println("  has <key>             Check if a key exists")
		os.Exit(1)
	}

	// Create storage instance
	store := storage.NewStorage()

	switch os.Args[1] {
	case "store":
		storeCmd.Parse(os.Args[2:])
		if storeCmd.NArg() != 2 {
			fmt.Println("Usage: horcruxkv store <key> <value>")
			os.Exit(1)
		}
		key := storeCmd.Arg(0)
		value := []byte(storeCmd.Arg(1))

		err := store.Store(key, value)
		if err != nil {
			log.Fatalf("Failed to store: %v", err)
		}
		fmt.Printf("Stored key '%s' with value '%s'\n", key, string(value))

	case "get":
		getCmd.Parse(os.Args[2:])
		if getCmd.NArg() != 1 {
			fmt.Println("Usage: horcruxkv get <key>")
			os.Exit(1)
		}
		key := getCmd.Arg(0)

		value, err := store.Get(key)
		if err != nil {
			log.Fatalf("Failed to get: %v", err)
		}
		fmt.Printf("Value for key '%s': %s\n", key, string(value))

	case "delete":
		deleteCmd.Parse(os.Args[2:])
		if deleteCmd.NArg() != 1 {
			fmt.Println("Usage: horcruxkv delete <key>")
			os.Exit(1)
		}
		key := deleteCmd.Arg(0)

		err := store.Delete(key)
		if err != nil {
			log.Fatalf("Failed to delete: %v", err)
		}
		fmt.Printf("Deleted key '%s'\n", key)

	case "has":
		hasCmd.Parse(os.Args[2:])
		if hasCmd.NArg() != 1 {
			fmt.Println("Usage: horcruxkv has <key>")
			os.Exit(1)
		}
		key := hasCmd.Arg(0)

		exists := store.Has(key)
		fmt.Printf("Key '%s' exists: %t\n", key, exists)

	default:
		fmt.Println("Unknown command:", os.Args[1])
		os.Exit(1)
	}
}
