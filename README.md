# Previous

The bot for ~~annoying nextcord members~~ managing some of nextcord's unique tasks.

## Running the bot

### Development

1. [Install docker](https://docs.docker.com/get-docker/)
2. Copy .env.example to .env
3. Set each variable to your values
  `CONSUL_HOST` by default in dev mode is `http://consul:8500`
  `CONSUL_TOKEN` is empty in dev mode, set it blank
4. Start docker
  `docker-compose up --build` (use `-d` for no output to console but to `docker logs`)

### Stopping

```bash
docker-compose down (or ctrl + c when attached)
```
