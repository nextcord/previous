# Previous

The bot for ~~annoying nextcord members~~ managing some of nextcord's unique tasks.

## Running the bot

You need a [consul](https://consul.io) instance running

1. [Install docker](https://docs.docker.com/get-docker/)
2. [Setup consul](#Consul)
3. Copy .env.example to .env
4. Set each variable to your values
  `CONSUL_HOST` by default in dev mode is `http://host.docker.internal:8500`
  `CONSUL_TOKEN` is found at the top of the output of starting consul in dev, the uuid
5. Start docker
  `docker-compose up --build` (use `-d` for no output to console but to `docker logs`)

### Stopping

```bash
docker-compose down (or ctrl + c when attached)
consul leave
```

### Consul

This is an example of how to setup consul.

```bash
sudo apt install consul
consul agent -dev -client 0.0.0.0
```

**NOTE:** This is not fit for production, only for testing. Follow the consul guide for production.

[More info](https://learn.hashicorp.com/tutorials/consul/get-started-agent)
