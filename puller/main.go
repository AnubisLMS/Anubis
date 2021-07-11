package main

import (
	"fmt"
	"os"
	"io"
	"io/ioutil"
	"time"
	"context"
	"encoding/base64"
	"encoding/json"
	
	"github.com/docker/docker/api/types"
	"github.com/docker/docker/client"
)


func indexOf(s string, r rune) int {
	for i, sc := range s {
		if sc == r {
			return i
		}
	}
	return -1
}

func parseToken(token string) string {
	p, err := base64.URLEncoding.DecodeString(token)
	pp := string(p)
	col := indexOf(pp, ':')
	ppp := pp[:col]

	authConfig := types.AuthConfig{
		Username: ppp,
		Password: ppp,
	}
	encodedJSON, err := json.Marshal(authConfig)
	if err != nil {
		panic(err)
	}

	return base64.URLEncoding.EncodeToString(encodedJSON)
}


func getToken() string {
	data, err := ioutil.ReadFile("/anubis/.dockerconfigjson")
    if err != nil {
		panic(err)
    }

	return string(data)
}


func pullImage(image string) {
	authStr := parseToken(getToken())
	cli, err := client.NewClientWithOpts(client.FromEnv, client.WithAPIVersionNegotiation())
	if err != nil {
		panic(err)
	}
	out, err := cli.ImagePull(context.Background(), image, types.ImagePullOptions{RegistryAuth: authStr})
	if err != nil {
		fmt.Printf("Failed to pull image: %s %s\n", err, image)
	}

	defer out.Close()
	io.Copy(os.Stdout, out)
}

func main() {
	images := os.Args[1:]
	for _, image := range images {
		fmt.Printf("starting with image: %s\n", image)
	}

	for {
		dt := time.Now()
		fmt.Println("Pulling images @ ", dt.String())
		for _, image := range images {
			pullImage(image)
		}
		time.Sleep(10 * time.Second)
	}
}
