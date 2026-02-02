
in one terminal we have

```bash
[owner@nixos:~/sync/vanity]$ nix develop
[vanity-gateway-dev:~/sync/vanity] ./req_test.py 
The first President of the United States was **George Washington**.
```

accessed by a proxy we created in another terminal with:

```bash
[vanity-gateway-dev:~/sync/vanity] ./vanity-gateway.py 
INFO:     Started server process [4131]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on https://0.0.0.0:8443 (Press CTRL+C to quit)
Forwarding to: https://api.groq.com/openai/v1/chat/completions
INFO:     127.0.0.1:53584 - "POST /chat/completions HTTP/1.1" 200 OK
```

currently only works with requests to requests

don't forget to run 

./create_certs.sh
