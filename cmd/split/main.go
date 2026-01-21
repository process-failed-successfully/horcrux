package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"math/big"
	"os"

	"github.com/process-failed-successfully/horcrux/internal/split"
)

func main() {
	// Parse command line flags
	secretHex := flag.String("secret", "", "Secret in hexadecimal format")
	shares := flag.Int("shares", 0, "Number of shares to create")
	threshold := flag.Int("threshold", 0, "Minimum number of shares required to reconstruct")
	outputDir := flag.String("output", ".", "Directory to save share files")
	flag.Parse()

	if *secretHex == "" || *shares == 0 || *threshold == 0 {
		fmt.Println("Usage: horcrux split --secret <hex> --shares <number> --threshold <number> [--output <directory>]")
		os.Exit(1)
	}

	// Convert hex secret to big.Int
	secret, ok := new(big.Int).SetString(*secretHex, 16)
	if !ok {
		fmt.Println("Error: Invalid hex secret")
		os.Exit(1)
	}

	// Generate shares
	generatedShares, err := split.SplitSecret(secret, *shares, *threshold)
	if err != nil {
		fmt.Printf("Error splitting secret: %v\n", err)
		os.Exit(1)
	}

	// Create output directory if it doesn't exist
	if err := os.MkdirAll(*outputDir, 0755); err != nil {
		fmt.Printf("Error creating output directory: %v\n", err)
		os.Exit(1)
	}

	// Save shares as JSON files
	for i, share := range generatedShares {
		filename := fmt.Sprintf("%s/share_%d.json", *outputDir, i+1)
		file, err := os.Create(filename)
		if err != nil {
			fmt.Printf("Error creating share file %s: %v\n", filename, err)
			os.Exit(1)
		}

		encoder := json.NewEncoder(file)
		encoder.SetIndent("", "  ")
		if err := encoder.Encode(share); err != nil {
			fmt.Printf("Error encoding share to JSON: %v\n", err)
			file.Close()
			os.Exit(1)
		}
		file.Close()

		fmt.Printf("Share %d saved to %s\n", i+1, filename)
	}

	fmt.Printf("Successfully generated %d shares with threshold %d\n", *shares, *threshold)
}
