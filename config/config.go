package config

// Config represents the configuration for HorcruxKV
type Config struct {
	StoragePath string
	NumNodes    int
}

// DefaultConfig returns a default configuration
func DefaultConfig() *Config {
	return &Config{
		StoragePath: "./data",
		NumNodes:    1,
	}
}
