package split

import (
	"crypto/rand"
	"encoding/hex"
	"errors"
	"fmt"
	"math/big"
)

// Share represents a single share of the secret
type Share struct {
	X int    // The x-coordinate (share index)
	Y *big.Int // The y-coordinate (share value)
}

// SplitSecret splits a secret into n shares, requiring k shares to reconstruct
func SplitSecret(secret string, n, k int) ([]Share, error) {
	if k <= 1 {
		return nil, errors.New("threshold k must be greater than 1")
	}
	if n < k {
		return nil, errors.New("number of shares n must be at least k")
	}

	// Convert secret to a big integer
	secretBytes, err := hex.DecodeString(secret)
	if err != nil {
		return nil, fmt.Errorf("invalid secret format: %v", err)
	}
	secretInt := new(big.Int).SetBytes(secretBytes)

	// Generate random coefficients for the polynomial
	coefficients, err := generateRandomCoefficients(k-1)
	if err != nil {
		return nil, fmt.Errorf("failed to generate coefficients: %v", err)
	}

	// Generate shares
	shares := make([]Share, n)
	for i := 1; i <= n; i++ {
		x := i
		y := evaluatePolynomial(secretInt, coefficients, x)
		shares[i-1] = Share{X: x, Y: y}
	}

	return shares, nil
}

// generateRandomCoefficients generates k-1 random coefficients for the polynomial
func generateRandomCoefficients(k int) ([]*big.Int, error) {
	coefficients := make([]*big.Int, k)
	for i := 0; i < k; i++ {
		coeff, err := rand.Int(rand.Reader, big.NewInt(1<<256-1))
		if err != nil {
			return nil, err
		}
		coefficients[i] = coeff
	}
	return coefficients, nil
}

// evaluatePolynomial evaluates the polynomial at point x
func evaluatePolynomial(a0 *big.Int, coefficients []*big.Int, x int) *big.Int {
	result := new(big.Int).Set(a0)
	xBig := big.NewInt(int64(x))

	for i, coeff := range coefficients {
		// term = coeff * x^(i+1)
		term := new(big.Int).Set(coeff)
		term.Mul(term, new(big.Int).Exp(xBig, big.NewInt(int64(i+1)), nil))
		result.Add(result, term)
	}

	return result
}
