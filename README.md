# use_rag

A minimal, standalone implementation for LLM-to-graph extraction, inspired by Microsoft's GraphRAG project. Extract entities, relationships, and claims from text without requiring the full GraphRAG package.

## Installation

```bash
# Clone or copy the use_rag folder to your project

# For Level 2 (config files):
pip install pyyaml

# For Level 4 (automated extraction):
pip install litellm
pip install python-dotenv  # for .env file support
```

## Environment Setup

Level 4 requires API keys. Create a `.env` file:

```bash
cp .env.example .env
# Edit .env with your API key
```

### Supported Providers

| Provider  | Models                                                         | Environment Variable  |
|-----------|----------------------------------------------------------------|----------------------|
| OpenAI    | `gpt-5.2`                                                      | `OPENAI_API_KEY`     |
| Anthropic | `claude-sonnet-4-5`, `claude-haiku-4-5`, `claude-opus-4-5`     | `ANTHROPIC_API_KEY`  |
| Google    | `gemini/gemini-3-flash-preview`, `gemini/gemini-3-pro-preview` | `GEMINI_API_KEY`     |

## Quick Start

### Level 1: Manual Prompt Generation

Generate prompts to copy-paste into ChatGPT/Claude.

1. Edit the configuration at the top of `level1_manual.py`:
   ```python
   TEXT_FILE = "text/01.txt"  # Path to your input text file
   ```

2. Run:
   ```bash
   uv run python level1_manual.py
   ```

3. Copy the generated prompt to ChatGPT/Claude.

### Level 2: Config-Based Prompts

Use YAML configuration for customization.

1. Edit the configuration at the top of `level2_config.py`:
   ```python
   CONFIG = DEFAULT_CONFIG_FILE  # Uses default_settings.yaml (auto-created)
   ```

2. Run:
   ```bash
   uv run python level2_config.py
   ```

3. Edit `default_settings.yaml` to customize entity types, model, etc.

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
    print(f"{rel.source} -> {rel.target}: {rel.description} (weight={rel.weight})")
```

### Level 4: Automated Extraction

End-to-end extraction with LLM API and CSV export.

1. Edit the configuration at the top of `level4_automated.py`:
   ```python
   CONFIG = DEFAULT_CONFIG_FILE  # Uses default_settings.yaml (auto-created)
   MODEL = None                  # Override model (None = use config)
   EXTRACT_CLAIMS = None         # Override claims extraction (None = use config)
   TEXT_FILE = "text/01.txt"     # Path to input text file
   OUTPUT_DIR = "output"         # Directory for CSV output
   ```

2. Run:
   ```bash
   uv run python level4_automated.py
   ```

3. Results are exported to:
   - `output/entities.csv`
   - `output/relationships.csv`
   - `output/claims.csv` (if claims extraction enabled)

## Configuration

On first run, `default_settings.yaml` is auto-generated:

```yaml
llm:
  model: "gemini/gemini-3-flash-preview"

extract_graph:
  entity_types:
    - organization
    - person
    - geo
    - event
  max_gleanings: 1

extract_claims:
  enabled: true
  entity_specs: "organization, person, geo, event"
  description: "Any claims or facts that could be relevant to information discovery."
  max_gleanings: 1
```

See `example_settings.yaml` for all available options.

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
    weight: float      # Relationship strength (1-10)
```

### Claim
```python
@dataclass
class Claim:
    subject: str           # Entity that is the subject
    object: str | None     # Entity that is the object (or None)
    type: str              # Claim type/category
    status: str            # TRUE, FALSE, or SUSPECTED
    start_date: str | None # ISO-8601 date
    end_date: str | None   # ISO-8601 date
    description: str       # Detailed claim description
    source_text: str       # Original text supporting the claim
```

## CSV Output Format

### entities.csv
| name | type | description |
|------|------|-------------|
| APPLE INC | ORGANIZATION | A technology company founded in 1976 |

### relationships.csv
| source | target | description | weight |
|--------|--------|-------------|--------|
| STEVE JOBS | APPLE INC | Co-founded the company | 9.0 |

### claims.csv
| subject | object | type | status | start_date | end_date | description | source_text |
|---------|--------|------|--------|------------|----------|-------------|-------------|
| APPLE INC | | FOUNDING | TRUE | 1976-04-01 | | Founded in Cupertino | ... |

## Gleaning (Iterative Extraction)

Level 4 extractors use "gleaning" to find entities that may have been missed:

1. Initial extraction prompt
2. Follow-up with `CONTINUE_PROMPT` to find more entities
3. Check with `LOOP_PROMPT` if extraction is complete (Y/N)
4. Repeat until LLM says "N" or `max_gleanings` is reached

Control gleaning with `max_gleanings`:
- `0` - Disable gleaning (single extraction only)
- `1` - One follow-up iteration (default)
- `2+` - Multiple follow-up iterations
- `-1` - Unlimited gleaning until LLM says no more

## API Reference

### Config Functions
- `load_config(config_path)` - Load YAML configuration
- `get_default_config()` - Get default configuration dictionary
- `export_default_settings(output_path)` - Export default settings to YAML file
- `create_extractors_from_config(config_path)` - Create `(LLMClient, GraphExtractor, ClaimExtractor)`

### Prompt Functions
- `generate_graph_prompt(text, entity_types=None)` - Generate graph extraction prompt
- `generate_claims_prompt(text, entity_specs=None, claim_description=None)` - Generate claims prompt

### Parser Functions
- `parse_graph_output(llm_output)` - Parse to `(list[Entity], list[Relationship])`
- `parse_claims_output(llm_output)` - Parse to `list[Claim]`

### Classes
- `LLMClient(model, api_key)` - LLM API wrapper
- `GraphExtractor(client, entity_types, max_gleanings=1)` - Automated graph extraction
- `ClaimExtractor(client, entity_specs, claim_description, max_gleanings=1)` - Automated claim extraction

## License

This implementation is inspired by Microsoft's GraphRAG project. The prompt templates are adapted from GraphRAG (MIT License).
