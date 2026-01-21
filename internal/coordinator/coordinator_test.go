package coordinator

import (
    "bytes"
    "net/http"
    "net/http/httptest"
    "testing"
    "github.com/gin-gonic/gin"
    "github.com/stretchr/testify/assert"
)

func TestHandleClientRequest(t *testing.T) {
    // Set Gin to test mode
    gin.SetMode(gin.TestMode)

    // Create a test router
    r := gin.Default()
    coord := NewCoordinator()
    coord.RegisterRoutes(r)

    // Test valid request
    t.Run("Valid Request", func(t *testing.T) {
        jsonBody := []byte(`{"data": "test secret"}`)
        req, _ := http.NewRequest("POST", "/coordinator/request", bytes.NewBuffer(jsonBody))
        req.Header.Set("Content-Type", "application/json")

        w := httptest.NewRecorder()
        r.ServeHTTP(w, req)

        assert.Equal(t, http.StatusOK, w.Code)
        assert.Contains(t, w.Body.String(), "Request processed successfully")
    })

    // Test invalid request
    t.Run("Invalid Request", func(t *testing.T) {
        jsonBody := []byte(`{"invalid": "data"}`)
        req, _ := http.NewRequest("POST", "/coordinator/request", bytes.NewBuffer(jsonBody))
        req.Header.Set("Content-Type", "application/json")

        w := httptest.NewRecorder()
        r.ServeHTTP(w, req)

        assert.Equal(t, http.StatusBadRequest, w.Code)
        assert.Contains(t, w.Body.String(), "Invalid request format")
    })
}
