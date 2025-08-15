# Diagrams and Sections

This project can generate architecture visuals using the [diagrams](https://diagrams.mingrammer.com/) library or other languages such as Mermaid.

## Section-to-diagram mapping

Each `--diagram-section` flag passed to the CLI maps to a section heading in the generated Markdown. When a section is listed, the content generator inserts a code block in that section using the requested diagram language. During generation the CLI will warn if any flagged section is missing a corresponding diagram block.

Example mapping:

| Section name | Diagram purpose        |
|--------------|-----------------------|
| `Architecture` | Overall system layout |
| `Data Flow`    | How information moves |
| `Deployment`   | Runtime or infra view |

## Supplying section flags

Repeat `--diagram-section` for every section that requires its own diagram. Optionally use `--diagram-language` to switch from the default Python `diagrams` library to another syntax such as `mermaid`.

```bash
python -m app.cli generate 42 --db-key "$SUPABASE_KEY" \
  --diagram-section "Architecture" \
  --diagram-section "Data Flow" \
  --diagram-section "Deployment" \
  --diagram-language mermaid
```

## Example article with multiple diagrams

## Architecture
```python
from diagrams import Diagram
from diagrams.aws.compute import EC2

with Diagram("Service Layout"):
    EC2("app")
```

## Data Flow
```python
from diagrams import Diagram
from diagrams.aws.database import RDS
from diagrams.aws.integration import SQS

with Diagram("Processing"):
    RDS("db") >> SQS("queue")
```

## Deployment
```python
from diagrams import Diagram
from diagrams.aws.compute import ECS
from diagrams.aws.network import ELB

with Diagram("Prod"):
    ELB("lb") >> ECS("service")
```

Each section renders to its own image which is uploaded and referenced in the article markdown.

