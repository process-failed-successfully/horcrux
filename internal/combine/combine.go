package combine

import (
	"errors"
	"fmt"
	"math/big"

	"github.com/process-failed-successfully/horcrux/internal/split"
)

// CombineShares reconstructs the secret from a subset of shares
func CombineShares(shares []split.Share, threshold int) (string, error) {
	if len(shares) < threshold {
		return "", errors.New("insufficient shares to reconstruct secret")
	}

	// Check for duplicate x-values
	xValues := make(map[int]bool)
	for _, share := range shares {
		if xValues[share.X] {
			return "", errors.New("duplicate share detected")
		}
		xValues[share.X] = true
	}

	// Perform Lagrange interpolation
	secretInt := lagrangeInterpolation(shares)

	// Convert the secret back to hex string
	secretHex := fmt.Sprintf("%x", secretInt)

	return secretHex, nil
}

// lagrangeInterpolation performs Lagrange interpolation to find the secret at x=0
func lagrangeInterpolation(shares []split.Share) *big.Int {
	prime := new(big.Int).Lsh(big.NewInt(1), 256) // 2^256, a large prime-like number
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
			numerator.Mod(numerator, prime)

			// denominator *= (share.X - other.X)
			denomDiff := big.NewInt(int64(share.X - other.X))
			denominator.Mul(denominator, denomDiff)
			denominator.Mod(denominator, prime)
		}

		// Calculate the Lagrange basis polynomial term
		// term = share.Y * (numerator / denominator)
		term := new(big.Int).Set(share.Y)

		// Compute modular inverse of denominator
		denominatorInv := new(big.Int).ModInverse(denominator, prime)
		if denominatorInv == nil {
			// This shouldn't happen with valid shares
			continue
		}

		// Multiply numerator by inverse of denominator
		basis := new(big.Int).Mul(numerator, denominatorInv)
		basis.Mod(basis, prime)

		// Multiply by share value
		term.Mul(term, basis)
		term.Mod(term, prime)

		// Add to result
		result.Add(result, term)
		result.Mod(result, prime)
	}

	return result
}
