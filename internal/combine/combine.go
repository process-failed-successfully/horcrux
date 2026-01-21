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

	// Check for duplicate shares
	seen := make(map[int]bool)
	for _, share := range shares {
		if seen[share.X] {
			return "", errors.New("duplicate shares detected")
		}
		seen[share.X] = true
	}

	// Use Lagrange interpolation to reconstruct the secret
	secret := lagrangeInterpolation(shares, threshold)

	// Convert the secret to a hex string
	return fmt.Sprintf("%x", secret.Bytes()), nil
}

// lagrangeInterpolation performs Lagrange interpolation to reconstruct the secret
// We evaluate the polynomial at x=0 to get the constant term (the secret)
func lagrangeInterpolation(shares []split.Share, threshold int) *big.Int {
	// Initialize the result to 0
	result := big.NewInt(0)

	// We want to evaluate the polynomial at x=0
	x_eval := big.NewInt(0)

	// Iterate through each share
	for i := 0; i < threshold; i++ {
		// Calculate the Lagrange basis polynomial
		basis := big.NewInt(1)
		x_i := big.NewInt(int64(shares[i].X))

		for j := 0; j < threshold; j++ {
			if i == j {
				continue
			}

			x_j := big.NewInt(int64(shares[j].X))

			// numerator = (x_eval - x_j) = (0 - x_j) = -x_j
			numerator := new(big.Int).Neg(x_j)

			// denominator = (x_i - x_j)
			denominator := new(big.Int).Sub(x_i, x_j)

			// Multiply the basis by (numerator / denominator)
			basis.Mul(basis, numerator)
			basis.Div(basis, denominator)
		}

		// Multiply the basis by the share value and add to the result
		term := new(big.Int).Mul(basis, shares[i].Y)
		result.Add(result, term)
	}

	return result
}
