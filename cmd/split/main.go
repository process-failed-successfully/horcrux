package main

import (
	"encoding/hex"
	"fmt"
	"os"

	"github.com/process-failed-successfully/horcrux/internal/split"
)

func main() {
	if len(os.Args) < 4 {
		fmt.Println("Usage: split --secret <secret> --shares <number> --threshold <number>")
		os.Exit(1)
	}

	secret := ""
	shares := 0
	threshold := 0

	for i := 1; i < len(os.Args); i += 2 {
		switch os.Args[i] {
		case "--secret":
			secret = os.Args[i+1]
		case "--shares":
			fmt.Sscanf(os.Args[i+1], "%d", &shares)
		case "--threshold":
			fmt.Sscanf(os.Args[i+1], "%d", &threshold)
		}
	}

	if secret == "" || shares == 0 || threshold == 0 {
		fmt.Println("Invalid arguments")
		os.Exit(1)
	}

	// Convert secret to hex if it's not already
	if _, err := hex.DecodeString(secret); err != nil {
		secret = hex.EncodeToString([]byte(secret))
	}

	sharesList, err := split.SplitSecret(secret, shares, threshold)
	if err != nil {
		fmt.Printf("Error splitting secret: %v\n", err)
		os.Exit(1)
	}

	fmt.Println("Shares generated successfully:")
	for _, share := range sharesList {
		fmt.Printf("Share %d: x=%d, y=%s\n", share.X, share.X, share.Y.String())
	}
}
