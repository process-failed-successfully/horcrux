package combine

import (
	"testing"

	"github.com/process-failed-successfully/horcrux/internal/split"
)

func TestCombineShares(t *testing.T) {
	// Create a test secret
	secret := "48656c6c6f" // "Hello" in hex

	// Split the secret into shares
	shares, err := split.SplitSecret(secret, 5, 3)
	if err != nil {
		t.Fatalf("Failed to split secret: %v", err)
	}

	// Test with sufficient shares (threshold)
	reconstructed, err := CombineShares(shares[:3], 3)
	if err != nil {
		t.Fatalf("Failed to combine shares: %v", err)
	}

	if reconstructed != secret {
		t.Errorf("Reconstructed secret does not match original. Expected: %s, Got: %s", secret, reconstructed)
	}

	// Test with insufficient shares
	_, err = CombineShares(shares[:2], 3)
	if err == nil {
		t.Error("Expected error for insufficient shares")
	}

	// Test with different combinations of shares
	for i := 0; i < 5; i++ {
		for j := i + 1; j < 5; j++ {
			for k := j + 1; k < 5; k++ {
				combo := []split.Share{shares[i], shares[j], shares[k]}
				reconstructed, err := CombineShares(combo, 3)
				if err != nil {
					t.Errorf("Failed to combine shares %d, %d, %d: %v", i, j, k, err)
				}
				if reconstructed != secret {
					t.Errorf("Reconstructed secret does not match original for shares %d, %d, %d. Expected: %s, Got: %s", i, j, k, secret, reconstructed)
				}
			}
		}
	}
}

func TestCombineSharesEdgeCases(t *testing.T) {
	// Test with duplicate shares
	secret := "48656c6c6f" // "Hello" in hex
	shares, err := split.SplitSecret(secret, 5, 3)
	if err != nil {
		t.Fatalf("Failed to split secret: %v", err)
	}

	// Create a slice with duplicate shares
	duplicateShares := []split.Share{shares[0], shares[0], shares[1]}
	_, err = CombineShares(duplicateShares, 3)
	if err == nil {
		t.Error("Expected error for duplicate shares")
	}
}
