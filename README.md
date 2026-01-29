# use_rag

A minimal, standalone implementation for LLM-to-graph extraction, inspired by Microsoft's GraphRAG project. Extract entities, relationships, and claims from text without requiring the full GraphRAG package.

## Features

- **4 levels of implementation** - from manual copy-paste to full automation
- **No required dependencies** for Levels 1-3 (pure Python)
- **Compatible prompts** - uses the same prompt format as GraphRAG
- **Structured output** - parse LLM responses into typed dataclasses

## Installation

```bash
# Clone or copy the use_rag folder to your project

# For Level 2 (config files):
pip install pyyaml

# For Level 4 (automated extraction):
pip install litellm   # or: pip install openai
pip install python-dotenv  # optional, for .env file support
```

## Environment Setup

Level 4 requires API keys for your LLM provider. You can set them via environment variables or use a `.env` file.

### Option 1: Using .env file (recommended)

1. Copy the example file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your API key(s):
   ```bash
   # For OpenAI (gpt-5.2)
   OPENAI_API_KEY=sk-your-key-here

   # For Anthropic (claude-sonnet-4-5, claude-haiku-4-5, claude-opus-4-5)
   ANTHROPIC_API_KEY=sk-ant-your-key-here

   # For Google (gemini/gemini-3-flash-preview, gemini/gemini-3-pro-preview)
   GEMINI_API_KEY=your-key-here
   ```

3. Load the `.env` file in your script:
   ```python
   from dotenv import load_dotenv
   load_dotenv()  # Load .env file before using LLMClient

   from use_rag import LLMClient
   client = LLMClient(model="gemini/gemini-3-flash-preview")  # Uses GEMINI_API_KEY from .env
   ```

### Option 2: Export environment variables

```bash
# OpenAI
export OPENAI_API_KEY='sk-your-key-here'

# Anthropic
export ANTHROPIC_API_KEY='sk-ant-your-key-here'

# Google Gemini
export GEMINI_API_KEY='your-key-here'
```

### Supported Providers

| Provider  | Models                                                      | Environment Variable  |
|-----------|-------------------------------------------------------------|----------------------|
| OpenAI    | `gpt-5.2`                                                   | `OPENAI_API_KEY`     |
| Anthropic | `claude-sonnet-4-5`, `claude-haiku-4-5`, `claude-opus-4-5`  | `ANTHROPIC_API_KEY`  |
| Google    | `gemini/gemini-3-flash-preview`, `gemini/gemini-3-pro-preview` | `GEMINI_API_KEY`     |

The `LLMClient` automatically detects the provider from the model name and uses the appropriate API key.

## Quick Start

### Level 1: Manual Prompt Generation

Generate prompts to copy-paste into ChatGPT/Claude:

```python
from use_rag import generate_graph_prompt, generate_claims_prompt

text = "Apple Inc. was founded by Steve Jobs in Cupertino, California in 1976."

# Generate graph extraction prompt
prompt = generate_graph_prompt(text)
print(prompt)  # Copy this to ChatGPT/Claude

# Generate claims extraction prompt
claims_prompt = generate_claims_prompt(
    text,
    entity_specs="organization, person",
    claim_description="key facts about companies and founders"
)
```

### Level 2: Config-Based Prompts

Use YAML configuration for customization:

```python
from use_rag import generate_graph_prompt_from_config, create_extractors_from_config

# Generate prompts from config
prompt = generate_graph_prompt_from_config(text, config_path="settings.yaml")

# Or create fully configured extractors (Level 4)
client, graph_extractor, claim_extractor = create_extractors_from_config("settings.yaml")
entities, rels = graph_extractor.extract(text)
```

Example `settings.yaml`:
```yaml
llm:
  model: "gemini/gemini-3-flash-preview"

extract_graph:
  entity_types:
    - organization
    - person
    - geo
    - event
  max_gleanings: 1  # -1 for unlimited

extract_claims:
  enabled: true
  entity_specs: "organization, person"
  description: "Any claims or facts that could be relevant to information discovery."
  max_gleanings: 1
```

See `example_settings.yaml` for a complete configuration reference with all options.

### Level 3: Parse LLM Output

Parse the LLM's response into structured objects:

```python
from use_rag import parse_graph_output, parse_claims_output

# Example LLM output
llm_output = '''("entity"<|>APPLE INC<|>ORGANIZATION<|>A technology company)
##
("entity"<|>STEVE JOBS<|>PERSON<|>Co-founder of Apple)
##
("relationship"<|>STEVE JOBS<|>APPLE INC<|>Founded the company<|>9)
<|COMPLETE|>'''

# Parse into structured objects
entities, relationships = parse_graph_output(llm_output)

for entity in entities:
    print(f"{entity.name} ({entity.type}): {entity.description}")

for rel in relationships:
    print(f"{rel.source} -> {rel.target} (weight={rel.weight})")
```

### Level 4: Automated Extraction

End-to-end extraction with LLM API, including automatic "gleaning" to find missed entities:

```python
from dotenv import load_dotenv
load_dotenv()  # Load API keys from .env file

from use_rag import LLMClient, GraphExtractor, ClaimExtractor

# Initialize client - auto-detects provider from model name
client = LLMClient(model="gpt-5.2")                        # Uses OPENAI_API_KEY
# client = LLMClient(model="claude-sonnet-4-5")            # Uses ANTHROPIC_API_KEY
# client = LLMClient(model="gemini/gemini-3-flash-preview") # Uses GEMINI_API_KEY

# Extract entities and relationships (with gleaning enabled by default)
extractor = GraphExtractor(
    client,
    entity_types=["organization", "person", "geo"],
    max_gleanings=1  # Number of follow-up iterations (default: 1)
)
entities, relationships = extractor.extract(text)

# Extract claims
claim_extractor = ClaimExtractor(
    client,
    entity_specs="organization, person",
    claim_description="red flags or notable facts",
    max_gleanings=1
)
claims = claim_extractor.extract(text)

# Disable gleaning for faster (but possibly less complete) extraction
fast_extractor = GraphExtractor(client, max_gleanings=0)
```

## Data Models

### Entity
```python
@dataclass
class Entity:
    name: str          # Entity name (uppercase)
    type: str          # Entity type (e.g., ORGANIZATION, PERSON)
    description: str   # Description of the entity
```

### Relationship
```python
@dataclass
class Relationship:
    source: str        # Source entity name
    target: str        # Target entity name
    description: str   # Description of the relationship
    weight: float      # Relationship strength (default: 1.0)
```

### Claim
```python
@dataclass
class Claim:
    subject: str           # Entity that is the subject of the claim
    object: str | None     # Entity that is the object (or None)
    type: str              # Claim type/category
    status: str            # TRUE, FALSE, or SUSPECTED
    start_date: str | None # ISO-8601 date
    end_date: str | None   # ISO-8601 date
    description: str       # Detailed claim description
    source_text: str       # Original text supporting the claim
```

## Output Format

The LLM output uses these delimiters (compatible with GraphRAG):

- **Record delimiter**: `##`
- **Tuple delimiter**: `<|>`
- **Completion marker**: `<|COMPLETE|>`

Example entity: `("entity"<|>APPLE INC<|>ORGANIZATION<|>A technology company)`

Example relationship: `("relationship"<|>STEVE JOBS<|>APPLE INC<|>Founded<|>9)`

## Gleaning (Iterative Extraction)

Level 4 extractors automatically use "gleaning" to find entities that may have been missed. This works by:

1. Sending the initial extraction prompt
2. Sending `CONTINUE_PROMPT` to ask for more entities
3. Using `LOOP_PROMPT` to check if extraction is complete (Y/N)
4. Repeating until the LLM says "N" or `max_gleanings` is reached

Control gleaning with the `max_gleanings` parameter:
- `max_gleanings=0` - Disable gleaning (single extraction only)
- `max_gleanings=1` - One follow-up iteration (default)
- `max_gleanings=2+` - Multiple follow-up iterations
- `max_gleanings=-1` - Unlimited gleaning until LLM says no more

For manual gleaning (Levels 1-3), use the prompts directly:

```python
from use_rag import (
    GRAPH_EXTRACTION_PROMPT,
    GRAPH_CONTINUE_PROMPT,
    GRAPH_LOOP_PROMPT,
)

# 1. Send initial prompt, get response
# 2. Send GRAPH_CONTINUE_PROMPT to get more entities
# 3. Send GRAPH_LOOP_PROMPT - if response starts with "Y", repeat step 2
```

## API Reference

### Level 1 Functions
- `generate_graph_prompt(text, entity_types=None)` - Generate graph extraction prompt
- `generate_claims_prompt(text, entity_specs=None, claim_description=None)` - Generate claims prompt

### Level 2 Functions
- `load_config(config_path)` - Load YAML configuration
- `get_default_config()` - Get default configuration dictionary
- `get_llm_config(config)` - Extract LLM settings from config
- `get_graph_config(config)` - Extract graph extraction settings
- `get_claims_config(config)` - Extract claims extraction settings
- `generate_graph_prompt_from_config(text, config_path=None)` - Generate prompt from config
- `generate_claims_prompt_from_config(text, config_path=None, entity_specs=None)` - Generate claims prompt from config
- `create_extractors_from_config(config_path=None)` - Create `(LLMClient, GraphExtractor, ClaimExtractor)` from config

### Level 3 Functions
- `parse_graph_output(llm_output)` - Parse to `(list[Entity], list[Relationship])`
- `parse_claims_output(llm_output)` - Parse to `list[Claim]`

### Level 4 Classes
- `LLMClient(model, api_key)` - LLM API wrapper
  - `complete(prompt)` - Send single prompt
  - `chat(messages)` - Send conversation (for gleaning)
- `GraphExtractor(client, entity_types, max_gleanings=1)` - Automated graph extraction
- `ClaimExtractor(client, entity_specs, claim_description, max_gleanings=1)` - Automated claim extraction

## Default Values

- **Entity types**: `["organization", "person", "geo", "event"]`
- **Claim description**: `"Any claims or facts that could be relevant to information discovery."`
- **Model**: `gemini/gemini-3-flash-preview`
- **max_gleanings**: `1`

## License

This implementation is inspired by Microsoft's GraphRAG project. The prompt templates are adapted from GraphRAG (MIT License).
