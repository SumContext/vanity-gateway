
# Vanity Gateway

OpenAI-compatible API gateway that routes requests to multiple LLM providers.

## Supported Providers

- **requests** - Direct HTTP to OpenAI-compatible APIs (Groq, etc.)
- **langchain_openai** - LangChain for OpenAI and compatible providers
- **langchain_aws** - AWS Bedrock (Claude 4.5, Amazon Nova)

## Configuration

Edit `vg_cfg/vg_cfg.json`:

```json
{
  "providers": {
    "groq-fast": {
      "api": "requests",
      "url": "https://api.groq.com/openai/v1/chat/completions",
      "key_path": "vg_cfg/Groq.key",
      "model": "openai/gpt-oss-20b"
    },
    "openai-gpt4": {
      "api": "langchain_openai",
      "url": "https://api.openai.com/v1",
      "key_path": "vg_cfg/openai.key",
      "model": "gpt-4o"
    },
    "aws-nova-micro": {
      "api": "langchain_aws",
      "key_path": "vg_cfg/aws.key",
      "model": "amazon.nova-micro-v1:0",
      "region": "us-east-1"
    }
  }
}
```

### Provider Configuration

**requests** - Requires `url`, `key_path`, `model`  
**langchain_openai** - Requires `url`, `key_path`, `model`  
**langchain_aws** - Requires `key_path`, `model`, `region`

### AWS Credentials

Create `vg_cfg/aws.key` with AWS credentials:
```ini
[default]
aws_access_key_id = YOUR_ACCESS_KEY
aws_secret_access_key = YOUR_SECRET_KEY
```

**Available AWS Bedrock Models:**
- Amazon Nova: `amazon.nova-micro-v1:0`, `amazon.nova-lite-v1:0`, `amazon.nova-pro-v1:0`
- Claude 4.5: `us.anthropic.claude-sonnet-4-5-20250929-v1:0`, `us.anthropic.claude-opus-4-5-20251101-v1:0`, `us.anthropic.claude-haiku-4-5-20251001-v1:0`

List available models:
```bash
aws bedrock list-foundation-models --region us-east-1
aws bedrock list-inference-profiles --region us-east-1
```

## Setup

```bash
cd ~/sync
git clone git@github.com:SumContext/vanity-gateway.git
cd ~/sync/vanity-gateway/
./create_certs.sh 

cd ~/sync/vanity-gateway/
nix develop
./vanity-gateway.py
INFO:     Started server process [9535]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on https://0.0.0.0:8443 (Press CTRL+C to quit)

```

and in a different terminal

```bash
cd ~/sync/vanity-gateway/
nix develop
./ex_client.py 
The first President of the United States was **George Washington**. He served from 1789 to 1797.
```

read [`ex_client.py`](/ex_client.py) example
Server runs on `https://0.0.0.0:8443`

## Usage

```bash
curl -k -X POST 'https://localhost:8443/chat/completions?nickname=aws-nova-micro' \
  -H "Authorization: Bearer $(cat vg_cfg/test.key)" \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "Hello"}]}'
```

**URL Parameters:**
- `nickname` (required) - Provider name from config
- `temperature`, `max_tokens`, etc. - Override model parameters

## Testing

Run all tests:
```bash
python run_tests.py
```

Test specific modules:
```bash
python -m pytest tests/test_vg_io_aws.py -v
python -m pytest tests/test_vg_io_oai.py -v
python -m pytest tests/test_vg_io_rqs.py -v
```

See [TESTING.md](TESTING.md) for details.
