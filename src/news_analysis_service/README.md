# News service

## How to run AI model in docker

- docker model pull ai/llama3.2:1B-Q8_0
- docker model run ai/llama3.2:1B-Q8_0

## How to run RabbitMQ in docker

- docker run --name my-rabbit -p 5672:5672 rabbitmq:4.2.4-management

## Good source materials

- [litellm](https://github.com/BerriAI/litellm/tree/main)
- [Docker DMR](https://docs.docker.com/ai/model-runner/api-reference)

## Fix to the problem with code running on WSL2 and models hosted on Windowses localhost

```bash
echo [wsl2] > %USERPROFILE%\.wslconfig
echo networkingMode=mirrored >> %USERPROFILE%\.wslconfig
wsl --shutdown
```
