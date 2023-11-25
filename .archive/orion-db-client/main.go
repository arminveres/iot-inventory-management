package main

import (
	"fmt"
	// "strconv"

	"orion-db-client/commands"
)

const dbName = "db1"

func main() {
	db, err := commands.CreateConnection()
	if err != nil {
		print("error occured creating a connection!")
		return
	}
	session, err := commands.OpenSession(db, "admin")
	dbtx, err := session.DBsTx()

	err = dbtx.CreateDB(dbName, nil)
	txID, receipt, err := dbtx.Commit(true)
	if err != nil {
		print("error occured!")
		return
	}
	fmt.Println("transaction with txID " + txID + " got committed in the block " + receipt.Response.GetHeader().String()) //+ strconv.Itoa(int(receipt.GetHeader().GetBaseHeader().GetNumber())))

	// 	err = dbtx.DeleteDB(dbName)
	// 	txID, receipt, err := dbtx.Commit(true)
	// 	fmt.Println("transaction with txID " + txID + " got committed in the block " + receipt.Response.GetHeader().String())

}
