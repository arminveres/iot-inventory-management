package commands

import (
	"github.com/hyperledger-labs/orion-sdk-go/pkg/bcdb"
	"github.com/hyperledger-labs/orion-sdk-go/pkg/config"
	"github.com/hyperledger-labs/orion-server/pkg/logger"
)

func CreateConnection() (bcdb.BCDB, error) {
	logger, err := logger.New(
		&logger.Config{
			Level:         "debug",
			OutputPath:    []string{"stdout"},
			ErrOutputPath: []string{"stderr"},
			Encoding:      "console",
			Name:          "bcdb-client",
		},
	)
	if err != nil {
		return nil, err
	}

	conConf := &config.ConnectionConfig{
		ReplicaSet: []*config.Replica{
			{
				ID:       "bdb-node-1",
				Endpoint: "http://127.0.0.1:6001",
			},
		},
		RootCAs: []string{
			"./crypto/CA/CA.pem",
		},
		Logger: logger,
	}

	db, err := bcdb.Create(conConf)
	if err != nil {
		return nil, err
	}

	return db, nil
}
