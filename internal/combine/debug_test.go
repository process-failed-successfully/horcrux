package combine

import (
	"testing"
	"fmt"
	"math/big"

	"github.com/process-failed-successfully/horcrux/internal/split"
)

func TestDebugCombine(t *testing.T) {
	// Split a secret
	secret := "48656c6c6f" // "Hello"
	shares, err := split.SplitSecret(secret, 5, 3)
	if err != nil {
		t.Fatalf("Failed to split secret: %v", err)
	}

	fmt.Println("Shares:")
	for i, share := range shares {
		fmt.Printf("Share %d: X=%d, Y=%s\n", i, share.X, share.Y.String())
	}

	// Test different combinations
	testCases := [][]int{
		{0, 1, 2}, // This should work
		{0, 1, 3}, // This is failing
		{0, 1, 4}, // This is failing
	}

	for _, comboIndices := range testCases {
		combo := make([]split.Share, len(comboIndices))
		for i, idx := range comboIndices {
			combo[i] = shares[idx]
		}

		fmt.Printf("\nTesting combination: %v\n", comboIndices)

		// Manual Lagrange interpolation
		result := big.NewInt(0)
		for i := 0; i < len(combo); i++ {
			x_i := big.NewInt(int64(combo[i].X))
			numeratorProduct := big.NewInt(1)
			denominatorProduct := big.NewInt(1)

			for j := 0; j < len(combo); j++ {
				if i == j {
					continue
				}

				x_j := big.NewInt(int64(combo[j].X))
				numerator := new(big.Int).Neg(x_j)
				denominator := new(big.Int).Sub(x_i, x_j)

				numeratorProduct.Mul(numeratorProduct, numerator)
				denominatorProduct.Mul(denominatorProduct, denominator)
			}

			fmt.Printf("  i=%d: numeratorProduct=%s, denominatorProduct=%s\n", i, numeratorProduct.String(), denominatorProduct.String())

			basis := new(big.Int).Div(numeratorProduct, denominatorProduct)
			term := new(big.Int).Mul(basis, combo[i].Y)

			fmt.Printf("  i=%d: basis=%s, term=%s\n", i, basis.String(), term.String())

			result.Add(result, term)
		}

		fmt.Printf("  Manual result: %s\n", result.String())

		// Using the function
		reconstructed, err := CombineShares(combo, 3)
		if err != nil {
			t.Fatalf("Failed to combine shares: %v", err)
		}

		fmt.Printf("  Function result: %s\n", reconstructed)
		fmt.Printf("  Expected: %s\n", secret)
		fmt.Printf("  Match: %v\n", reconstructed == secret)
	}
}
