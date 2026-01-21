package combine

import (
	"errors"
	"math/big"
)

// Share represents a single share in Shamir's Secret Sharing
type Share struct {
	X *big.Int
	Y *big.Int
}

// CombineShares reconstructs the secret from a subset of shares
func CombineShares(shares []Share) ([]byte, error) {
	if len(shares) < 2 {
		return nil, errors.New("at least 2 shares are required to reconstruct the secret")
	}

	// Implement Shamir's Secret Sharing combination using Lagrange interpolation
	secret := big.NewInt(0)
	modulus := big.NewInt(0)
	// Set modulus to a large prime (simplified for this example)
	modulus.SetString("6277101735386680763835789423207666416102355444464034512896", 10)

	// Lagrange interpolation
	for i, share := range shares {
		numerator := big.NewInt(1)
		denominator := big.NewInt(1)

		for j, otherShare := range shares {
			if i == j {
				continue
			}
			// numerator *= (0 - otherShare.X)
			numerator.Mul(numerator, big.NewInt(0).Sub(big.NewInt(0), otherShare.X))
			// denominator *= (share.X - otherShare.X)
			denominator.Mul(denominator, big.NewInt(0).Sub(share.X, otherShare.X))
		}

		// Compute Lagrange coefficient: numerator / denominator mod modulus
		invDenominator := big.NewInt(0).ModInverse(denominator, modulus)
		lagrange := big.NewInt(0).Mul(numerator, invDenominator)
		lagrange.Mod(lagrange, modulus)

		// Add to secret: secret += share.Y * lagrange
		term := big.NewInt(0).Mul(share.Y, lagrange)
		secret.Add(secret, term)
		secret.Mod(secret, modulus)
	}

	return secret.Bytes(), nil
}
