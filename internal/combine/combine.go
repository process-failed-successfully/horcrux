package combine

import (
	"errors"
	"fmt"
	"math/big"

	"github.com/process-failed-successfully/horcrux/internal/split"
)

// Prime modulus for finite field arithmetic
// This should match the prime used in the split operation
var prime = new(big.Int).SetBytes([]byte{
	0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
	0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
	0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF,
	0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFD,
})

// modInverse computes the modular inverse of a modulo prime
func modInverse(a *big.Int) *big.Int {
	// Using Fermat's Little Theorem: a^(p-2) ≡ a^(-1) mod p
	// Since p is prime and a < p
	pMinus2 := new(big.Int).Sub(prime, big.NewInt(2))
	return new(big.Int).Exp(a, pMinus2, prime)
}

// modDiv performs modular division: (a / b) mod prime
func modDiv(a, b *big.Int) *big.Int {
	invB := modInverse(b)
	result := new(big.Int).Mul(a, invB)
	return result.Mod(result, prime)
}

// modMul performs modular multiplication: (a * b) mod prime
func modMul(a, b *big.Int) *big.Int {
	result := new(big.Int).Mul(a, b)
	return result.Mod(result, prime)
}

// modAdd performs modular addition: (a + b) mod prime
func modAdd(a, b *big.Int) *big.Int {
	result := new(big.Int).Add(a, b)
	return result.Mod(result, prime)
}

// modSub performs modular subtraction: (a - b) mod prime
func modSub(a, b *big.Int) *big.Int {
	result := new(big.Int).Sub(a, b)
	return result.Mod(result, prime)
}

// modNeg performs modular negation: (-a) mod prime
func modNeg(a *big.Int) *big.Int {
	result := new(big.Int).Neg(a)
	return result.Mod(result, prime)
}

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
	// The formula is: f(0) = sum(y_i * product((0 - x_j)/(x_i - x_j)) for j != i)

	// Iterate through each share
	for i := 0; i < threshold; i++ {
		// Calculate the Lagrange basis polynomial
		x_i := big.NewInt(int64(shares[i].X))

		// Calculate numerator product: product((0 - x_j)) for j != i
		numeratorProduct := big.NewInt(1)
		// Calculate denominator product: product((x_i - x_j)) for j != i
		denominatorProduct := big.NewInt(1)

		for j := 0; j < threshold; j++ {
			if i == j {
				continue
			}

			x_j := big.NewInt(int64(shares[j].X))

			// numerator = (0 - x_j) = -x_j mod prime
			numerator := modNeg(x_j)
			numeratorProduct = modMul(numeratorProduct, numerator)

			// denominator = (x_i - x_j) mod prime
			denominator := modSub(x_i, x_j)
			denominatorProduct = modMul(denominatorProduct, denominator)
		}

		// Calculate basis = numeratorProduct / denominatorProduct mod prime
		basis := modDiv(numeratorProduct, denominatorProduct)

		// Multiply the basis by the share value and add to the result
		term := modMul(basis, shares[i].Y)
		result = modAdd(result, term)
	}

	return result
}
