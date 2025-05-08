# Scripts Repository

This directory contains various scripts used in the project for data processing, ETL operations, and workflow automation.

## Directory Structure

- **python/**: Python scripts for data processing, analysis, and automation
- **sql/**: SQL scripts for database operations and queries
- **bash/**: Shell scripts for system operations and automation
- **kestra/**: Kestra workflow YAML definitions
- **dlt/**: DLT (Data Load Tool) pipeline scripts

## Usage

Scripts in this repository can be executed directly or through the application's workflow orchestration system (Kestra).

### Python Scripts

Python scripts can be executed directly:

```bash
python scripts/python/script_name.py [arguments]
```

Or through Kestra workflows that reference these scripts.

### SQL Scripts

SQL scripts can be executed against your database:

```bash
psql -h hostname -d database -U username -f scripts/sql/script_name.sql
```

### Bash Scripts

Bash scripts can be executed directly:

```bash
bash scripts/bash/script_name.sh [arguments]
```

Make sure to set the appropriate permissions:

```bash
chmod +x scripts/bash/script_name.sh
```

### Kestra Workflows

Kestra workflow YAML files can be deployed to your Kestra instance:

```bash
kestra flow create -f scripts/kestra/workflow_name.yaml
```

### DLT Pipelines

DLT pipeline scripts can be executed directly:

```bash
python scripts/dlt/pipeline_name.py
```

## Adding New Scripts

When adding new scripts to this repository:

1. Place the script in the appropriate subdirectory based on its type
2. Include a header comment that describes the script's purpose, inputs, outputs, and usage
3. Update any relevant documentation
4. If the script is to be used in a Kestra workflow, make sure it's properly referenced

## Script Naming Conventions

Use descriptive names for your scripts following these conventions:

- Python: `snake_case.py`
- SQL: `snake_case.sql`
- Bash: `snake_case.sh`
- Kestra: `kebab-case.yaml`
- DLT: `snake_case.py`

## Script Templates

### Python Script Template

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script Name: script_name.py
Description: Brief description of what this script does
Author: Your Name
Date: YYYY-MM-DD
Usage: python script_name.py [arguments]
"""

import argparse
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Description of your script')
    parser.add_argument('--arg1', help='Description of arg1')
    parser.add_argument('--arg2', help='Description of arg2')
    
    args = parser.parse_args()
    
    # Your code here
    logger.info('Script started')
    
    # Process
    
    logger.info('Script completed')

if __name__ == '__main__':
    main()
```

### SQL Script Template

```sql
-- Script Name: script_name.sql
-- Description: Brief description of what this script does
-- Author: Your Name
-- Date: YYYY-MM-DD
-- Usage: psql -h hostname -d database -U username -f script_name.sql

-- Your SQL code here
```

### Bash Script Template

```bash
#!/bin/bash
# Script Name: script_name.sh
# Description: Brief description of what this script does
# Author: Your Name
# Date: YYYY-MM-DD
# Usage: ./script_name.sh [arguments]

# Exit on error
set -e

# Your code here
echo "Script started"

# Process

echo "Script completed"
```

### Kestra Workflow Template

```yaml
# Workflow Name: workflow-name
# Description: Brief description of what this workflow does
# Author: Your Name
# Date: YYYY-MM-DD

id: workflow-name
namespace: default
tasks:
  - id: task1
    type: io.kestra.plugin.core.log.Log
    message: "Hello World"
```

### DLT Pipeline Template

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Pipeline Name: pipeline_name.py
Description: Brief description of what this pipeline does
Author: Your Name
Date: YYYY-MM-DD
Usage: python pipeline_name.py
"""

import dlt
from dlt.common.typing import TDataItem, TDataItems
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def main():
    """Main function."""
    # Your pipeline code here
    logger.info('Pipeline started')
    
    # Define source
    
    # Define destination
    
    # Create and run pipeline
    
    logger.info('Pipeline completed')

if __name__ == '__main__':
    main()
```
