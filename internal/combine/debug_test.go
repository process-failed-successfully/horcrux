package combine

import (
	"fmt"
	"testing"

	"github.com/process-failed-successfully/horcrux/internal/split"
)

func TestDebugCombine(t *testing.T) {
	// Test with a simple secret
	secret := "48656c6c6f" // "Hello"

	// Split the secret
	shares, err := split.SplitSecret(secret, 5, 3)
	if err != nil {
		t.Fatalf("Failed to split secret: %v", err)
	}

	// Print the shares for debugging
	fmt.Println("Shares:")
	for i, share := range shares {
		fmt.Printf("Share %d: X=%d, Y=%s\n", i, share.X, share.Y.String())
	}

	// Test with first 3 shares
	combo := []split.Share{shares[0], shares[1], shares[2]}
	reconstructed, err := CombineShares(combo, 3)
	if err != nil {
		t.Fatalf("Failed to combine shares: %v", err)
	}

	fmt.Printf("Original: %s\n", secret)
	fmt.Printf("Reconstructed: %s\n", reconstructed)
	fmt.Printf("Match: %v\n", reconstructed == secret)
}
