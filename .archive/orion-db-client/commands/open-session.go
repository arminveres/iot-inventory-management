package commands

import (
	"github.com/hyperledger-labs/orion-sdk-go/pkg/bcdb"
	"github.com/hyperledger-labs/orion-sdk-go/pkg/config"
	"time"
)

func OpenSession(db bcdb.BCDB, userID string) (bcdb.DBSession, error) {
	sessionConf := &config.SessionConfig{
		UserConfig: &config.UserConfig{
			UserID:         userID,
			CertPath:       "./crypto/" + userID + "/" + userID + ".pem",
			PrivateKeyPath: "./crypto/" + userID + "/" + userID + ".key",
		},
		TxTimeout:    20 * time.Second,
		QueryTimeout: 10 * time.Second,
	}

	session, err := db.Session(sessionConf)
	if err != nil {
		return nil, err
	}

	return session, nil
}
