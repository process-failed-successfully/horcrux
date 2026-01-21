package shamir

import (
    "testing"
    "github.com/stretchr/testify/assert"
)

func TestSplitSecret(t *testing.T) {
    s := NewShamir()

    t.Run("Valid Split", func(t *testing.T) {
        shares, err := s.SplitSecret("test-secret", 5, 3)
        assert.NoError(t, err)
        assert.Len(t, shares, 5)
    })

    t.Run("Invalid Threshold", func(t *testing.T) {
        _, err := s.SplitSecret("test-secret", 5, 6)
        assert.Error(t, err)
    })
}

func TestCombineShares(t *testing.T) {
    s := NewShamir()

    t.Run("Valid Combine", func(t *testing.T) {
        shares := []string{"test-secret-share-0", "test-secret-share-1"}
        secret, err := s.CombineShares(shares)
        assert.NoError(t, err)
        assert.Equal(t, "test-secret", secret)
    })

    t.Run("No Shares", func(t *testing.T) {
        _, err := s.CombineShares([]string{})
        assert.Error(t, err)
    })
}
