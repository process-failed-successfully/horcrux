package main

import (
	"encoding/json"
	"errors"
	"fmt"
	"math/big"
	"os"

	"github.com/process-failed-successfully/horcrux/internal/combine"
	"github.com/process-failed-successfully/horcrux/internal/split"
)

func main() {
	if len(os.Args) < 2 {
		fmt.Println("Usage: horcrux combine --shares <file1> <file2> ...")
		os.Exit(1)
	}

	if os.Args[1] != "--shares" {
		fmt.Println("Usage: horcrux combine --shares <file1> <file2> ...")
		os.Exit(1)
	}

	if len(os.Args) < 4 {
		fmt.Println("Error: At least 2 share files are required")
		os.Exit(1)
	}

	// Read share files
	var shares []split.Share
	for i := 2; i < len(os.Args); i++ {
		shareFile := os.Args[i]
		share, err := readShareFile(shareFile)
		if err != nil {
			fmt.Printf("Error reading share file %s: %v\n", shareFile, err)
			os.Exit(1)
		}
		shares = append(shares, share)
	}

	// Combine shares
	secret, err := combine.CombineShares(shares, len(shares))
	if err != nil {
		fmt.Printf("Error combining shares: %v\n", err)
		os.Exit(1)
	}

	fmt.Printf("Reconstructed secret: %s\n", secret)
}

func readShareFile(filename string) (split.Share, error) {
	var share split.Share
	file, err := os.Open(filename)
	if err != nil {
		return share, err
	}
	defer file.Close()

	decoder := json.NewDecoder(file)
	err = decoder.Decode(&share)
	if err != nil {
		return share, err
	}

	return share, nil
}
