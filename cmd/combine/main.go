package main

import (
	"encoding/hex"
	"fmt"
	"os"
	"strconv"
	"strings"

	"github.com/process-failed-successfully/horcrux/internal/combine"
	"github.com/process-failed-successfully/horcrux/internal/split"
)

func main() {
	if len(os.Args) < 2 {
		fmt.Println("Usage: combine --shares \"x1,y1 x2,y2 x3,y3\" --threshold <number>")
		os.Exit(1)
	}

	sharesStr := ""
	threshold := 0

	for i := 1; i < len(os.Args); i += 2 {
		if i+1 >= len(os.Args) {
			fmt.Println("Invalid arguments")
			os.Exit(1)
		}

		switch os.Args[i] {
		case "--shares":
			sharesStr = os.Args[i+1]
		case "--threshold":
			var err error
			threshold, err = strconv.Atoi(os.Args[i+1])
			if err != nil {
				fmt.Printf("Invalid threshold: %v\n", err)
				os.Exit(1)
			}
		}
	}

	if sharesStr == "" || threshold == 0 {
		fmt.Println("Invalid arguments")
		os.Exit(1)
	}

	// Parse the shares
	shares, err := parseShares(sharesStr)
	if err != nil {
		fmt.Printf("Error parsing shares: %v\n", err)
		os.Exit(1)
	}

	// Combine the shares
	secret, err := combine.CombineShares(shares, threshold)
	if err != nil {
		fmt.Printf("Error combining shares: %v\n", err)
		os.Exit(1)
	}

	// Convert the secret from hex to string if it's valid UTF-8
	secretBytes, err := hex.DecodeString(secret)
	if err != nil {
		fmt.Printf("Reconstructed secret (hex): %s\n", secret)
	} else {
		secretString := string(secretBytes)
		if isPrintable(secretString) {
			fmt.Printf("Reconstructed secret: %s\n", secretString)
		} else {
			fmt.Printf("Reconstructed secret (hex): %s\n", secret)
		}
	}
}

func parseShares(sharesStr string) ([]split.Share, error) {
	sharePairs := strings.Fields(sharesStr)
	shares := make([]split.Share, len(sharePairs))

	for i, pair := range sharePairs {
		parts := strings.Split(pair, ",")
		if len(parts) != 2 {
			return nil, fmt.Errorf("invalid share format: %s", pair)
		}

		x, err := strconv.Atoi(parts[0])
		if err != nil {
			return nil, fmt.Errorf("invalid x-coordinate: %s", parts[0])
		}

		y, ok := new(big.Int).SetString(parts[1], 10)
		if !ok {
			return nil, fmt.Errorf("invalid y-coordinate: %s", parts[1])
		}

		shares[i] = split.Share{X: x, Y: y}
	}

	return shares, nil
}

func isPrintable(s string) bool {
	for _, r := range s {
		if r < 32 || r > 126 {
			return false
		}
	}
	return true
}
