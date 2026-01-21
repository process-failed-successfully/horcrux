package split

import (
	"testing"
)

func TestSplitSecret(t *testing.T) {
	// Test with a simple secret
	secret := "48656c6c6f" // "Hello" in hex
	n := 5
	k := 3

	shares, err := SplitSecret(secret, n, k)
	if err != nil {
		t.Fatalf("Failed to split secret: %v", err)
	}

	if len(shares) != n {
		t.Fatalf("Expected %d shares, got %d", n, len(shares))
	}

	// Verify that all shares are unique
	shareMap := make(map[int]bool)
	for _, share := range shares {
		if shareMap[share.X] {
			t.Errorf("Duplicate share found for x=%d", share.X)
		}
		shareMap[share.X] = true
	}

	// Verify that shares are in the correct format
	for _, share := range shares {
		if share.X <= 0 || share.X > n {
			t.Errorf("Invalid share x-coordinate: %d", share.X)
		}
		if share.Y == nil {
			t.Errorf("Share y-coordinate is nil")
		}
	}
}

func TestSplitSecretInvalidInputs(t *testing.T) {
	// Test with invalid secret format
	_, err := SplitSecret("invalid", 5, 3)
	if err == nil {
		t.Error("Expected error for invalid secret format")
	}

	// Test with k <= 1
	_, err = SplitSecret("48656c6c6f", 5, 1)
	if err == nil {
		t.Error("Expected error for k <= 1")
	}

	// Test with n < k
	_, err = SplitSecret("48656c6c6f", 3, 5)
	if err == nil {
		t.Error("Expected error for n < k")
	}
}
