package peer

import (
    "bytes"
    "net/http"
    "net/http/httptest"
    "testing"
    "github.com/gin-gonic/gin"
    "github.com/stretchr/testify/assert"
)

func TestHandleStoreShare(t *testing.T) {
    // Set Gin to test mode
    gin.SetMode(gin.TestMode)

    // Create a test router
    r := gin.Default()
    p := NewPeer()
    p.RegisterRoutes(r)

    // Test valid share
    t.Run("Valid Share", func(t *testing.T) {
        jsonBody := []byte(`{"share_id": "share123", "data": "share data"}`)
        req, _ := http.NewRequest("POST", "/peer/store", bytes.NewBuffer(jsonBody))
        req.Header.Set("Content-Type", "application/json")

        w := httptest.NewRecorder()
        r.ServeHTTP(w, req)

        assert.Equal(t, http.StatusOK, w.Code)
        assert.Contains(t, w.Body.String(), "Share stored successfully")
    })

    // Test invalid share
    t.Run("Invalid Share", func(t *testing.T) {
        jsonBody := []byte(`{"invalid": "data"}`)
        req, _ := http.NewRequest("POST", "/peer/store", bytes.NewBuffer(jsonBody))
        req.Header.Set("Content-Type", "application/json")

        w := httptest.NewRecorder()
        r.ServeHTTP(w, req)

        assert.Equal(t, http.StatusBadRequest, w.Code)
        assert.Contains(t, w.Body.String(), "Invalid share format")
    })
}
