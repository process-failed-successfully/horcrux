package combine

import (
	"fmt"
	"math/big"
	"testing"

	"github.com/process-failed-successfully/horcrux/internal/split"
)

func TestDebugCombine(t *testing.T) {
	// Test case 1: Simple case with 3 shares
	shares1 := []split.Share{
		{X: 1, Y: new(big.Int).SetString("3312346087361086972778638432884213896243642722468651582313143524850489626660", 16)},
		{X: 2, Y: new(big.Int).SetString("68888688932910845741554125461173614362372121925690956081760996489431279570908", 16)},
		{X: 3, Y: new(big.Int).SetString("80936939326293027543629014135460627868299294194376599302809927585186211228568", 16)},
	}

	secret1, err := CombineShares(shares1, 3)
	if err != nil {
		t.Fatalf("Error combining shares: %v", err)
	}

	if secret1 != "48656c6c6f" {
		t.Errorf("Expected secret 48656c6c6f, got %s", secret1)
	}
	t.Logf("Test case 1 passed: Got expected secret %s", secret1)

	// Test case 2: Different combination of shares
	shares2 := []split.Share{
		{X: 1, Y: new(big.Int).SetString("3312346087361086972778638432884213896243642722468651582313143524850489626660", 16)},
		{X: 2, Y: new(big.Int).SetString("68888688932910845741554125461173614362372121925690956081760996489431279570908", 16)},
		{X: 4, Y: new(big.Int).SetString("39457097267507632379003304455745254414025159528525581245459936812115284599640", 16)},
	}

	secret2, err := CombineShares(shares2, 3)
	if err != nil {
		t.Fatalf("Error combining shares: %v", err)
	}

	if secret2 != "48656c6c6f" {
		t.Errorf("Expected secret 48656c6c6f, got %s", secret2)
	}
	t.Logf("Test case 2 passed: Got expected secret %s", secret2)
}
