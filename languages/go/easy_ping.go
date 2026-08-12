package main

import "fmt"

func ping() string {
	return "pong"
}

func main() {
	if ping() != "pong" {
		panic("ping failed")
	}
	fmt.Println("easy_ping: pong")
}
