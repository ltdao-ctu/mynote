# Ollama

## Quickstart

```bash
# install ollama
brew install --cask ollama

# install continue.dev
code --install-extension Continue.continue

# general purpose llm
ollama run llama2

# coding llm
ollama run deepseek-coder:6.7b

# autocomplete llm
ollama run starcoder2:3b
```

## Configure Continue VSCode Extension

* Select the Continue extension from the primary side bar
* Click the settings cog on the bottom right-hand side of the Continue column
* Paste the `config.json` settings (cf. [gist](https://gist.github.com/pythoninthegrass/9ec5d6e9e05b96272bb21d8a8ce2ca11))

## Commands

* `"""`: multiline message
* `/bye`: quit llm

## Further Reading

[ollama/ollama: Get up and running with Llama 2, Mistral, Gemma, and other large language models.](https://github.com/ollama/ollama)

[Continue](https://continue.dev/docs/intro)

[DeepSeek](https://chat.deepseek.com/coder)