package main

import (
	"fmt"
	"math/big"

	"github.com/process-failed-successfully/horcrux/internal/split"
)

var Prime = new(big.Int).SetBytes([]byte{
	0xFF, 0xFF, 0xFF, 0xFF, 0x00, 0x00, 0x00, 0x01,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0xFF, 0xFF, 0xFF, 0xFF,
	0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
})

func lagrangeInterpolation(shares []split.Share) *big.Int {
	result := big.NewInt(0)

	for i, share := range shares {
		numerator := big.NewInt(1)
		denominator := big.NewInt(1)

		for j, other := range shares {
			if i == j {
				continue
			}

			// numerator *= -other.X
			numerator.Mul(numerator, big.NewInt(int64(-other.X)))
			numerator.Mod(numerator, Prime)

			// denominator *= (share.X - other.X)
			denomDiff := big.NewInt(int64(share.X - other.X))
			denominator.Mul(denominator, denomDiff)
			denominator.Mod(denominator, Prime)
		}

		// Calculate the Lagrange basis polynomial term
		term := new(big.Int).Set(share.Y)

		// Compute modular inverse of denominator
		denominatorInv := new(big.Int).ModInverse(denominator, Prime)
		if denominatorInv == nil {
			continue
		}

		// Multiply numerator by inverse of denominator
		basis := new(big.Int).Mul(numerator, denominatorInv)
		basis.Mod(basis, Prime)

		// Multiply by share value
		term.Mul(term, basis)
		term.Mod(term, Prime)

		// Add to result
		result.Add(result, term)
		result.Mod(result, Prime)

		fmt.Printf("Share %d: X=%d, Y=%s\n", i, share.X, share.Y.String())
		fmt.Printf("  numerator=%s, denominator=%s\n", numerator.String(), denominator.String())
		fmt.Printf("  basis=%s, term=%s\n", basis.String(), term.String())
		fmt.Printf("  result=%s\n", result.String())
	}

	return result
}

func main() {
	// Test with the shares from the test
	shares := []split.Share{
		{X: 1, Y: big.NewInt(0x48656c6c6f)}, // "Hello"
		{X: 2, Y: big.NewInt(0x5e737b3cece92dc17cc1407af3cd68a76b0d896e35693c434823284b6fecea5d)},
		{X: 3, Y: big.NewInt(0x769de8e9621d3e915ac4403e9d04b3f169a0ec336b625f033ae1b38a63ae8480)},
		{X: 4, Y: big.NewInt(0xc2b1ef21d8f3524f0c6b5cb615ab014090cea1af013a76d00ba1c10d7711d789)},
		{X: 5, Y: big.NewInt(0xdf3f4ec9ffd5e8c8f630be4e415712dced02288953066a6fbf1495a3255fe313)},
	}

	result := lagrangeInterpolation(shares[:3])
	fmt.Printf("\nFinal result: %s\n", result.String())
	fmt.Printf("Expected: 0x48656c6c6f\n")
	fmt.Printf("Match: %v\n", result.Cmp(big.NewInt(0x48656c6c6f)) == 0)
}
