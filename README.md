# MCE Cluster Generator

A comprehensive tool for generating cluster configurations for MCE (Multi-Cluster Engine) environments with GitOps integration.

## Features

- **Flexible Template System**: YAML-based templates for different cluster flavors (default, PortWorks, PowerFlex, etc.)
- **Comprehensive Validation**: Pydantic-based validation for all input parameters
- **GitOps Integration**: Automatic branch creation, file generation, and commit/push workflows
- **Path Validation**: Ensures correct repository structure exists or creates it
- **Rich CLI Interface**: User-friendly command-line interface with colored output
- **Extensive Logging**: Configurable logging with file and console output
- **Error Handling**: Comprehensive error handling with custom exceptions

## Installation

### From Source

```bash
# Clone the repository
git clone <repository-url>
cd mce-cluster-generator

# Install in development mode
pip install -e .

# Or install dependencies directly
pip install -r requirements.txt
```

### Using pip (when published)

```bash
pip install mce-cluster-generator
```

## Quick Start

### 1. Generate a cluster configuration (dry-run)

```bash
mce-gen generate \
  --cluster-name "my-cluster" \
  --site "datacenter-1" \
  --nodes 3 \
  --mce-name "mce-prod" \
  --environment "prod" \
  --flavor "default" \
  --dry-run
```

### 2. Generate and commit to GitOps repository

```bash
mce-gen generate \
  --cluster-name "my-cluster" \
  --site "datacenter-1" \
  --nodes 3 \
  --mce-name "mce-prod" \
  --environment "prod" \
  --flavor "default" \
  --repo-path "/path/to/gitops/repo"
```

### 3. List available flavors

```bash
mce-gen list-flavors
```

### 4. Preview configuration

```bash
mce-gen preview \
  --cluster-name "my-cluster" \
  --site "datacenter-1" \
  --nodes 3 \
  --mce-name "mce-prod" \
  --environment "prod" \
  --flavor "default"
```

## Configuration

### Input Parameters

- **cluster-name**: Kubernetes-compliant cluster name (lowercase, alphanumeric, hyphens)
- **site**: Site where the cluster will be deployed
- **nodes**: Number of worker nodes (1-100)
- **mce-name**: MCE instance name
- **environment**: Environment type (`prod` or `prep`)
- **flavor**: Cluster flavor template to use (default: `default`)

### Available Flavors

- **default**: Standard cluster configuration
- **portworks**: PortWorks storage integration
- **powerflex**: PowerFlex storage integration

## Output Structure

The generator creates files following this path structure:

```
sites/<site>/mce-tenant-cluster/mce-<environment>/<mce-name>/ocp4-<cluster-name>.yaml
```

Example:
```
sites/datacenter-1/mce-tenant-cluster/mce-prod/mce-main/ocp4-my-cluster.yaml
```

## Template System

### Creating Custom Flavors

1. Create a new YAML template in `src/mce_cluster_generator/templates/`
2. Use Jinja2 syntax for variable substitution
3. Available variables:
   - `{{ cluster_name }}`
   - `{{ number_of_nodes }}`
   - `{{ site }}`
   - `{{ mce_name }}`
   - `{{ environment }}`
   - `{{ private_registry }}` (default: registry.internal.company.com)

### Example Template

```yaml
clusterName: "{{ cluster_name }}"
platform: agent
nodePool:
  - name: "{{ cluster_name }}-nodepool"
    replicas: {{ number_of_nodes }}
    labels:
      allowDeletion: false
      minReplicas: "{{ number_of_nodes - 1 }}"
      maxReplicas: "{{ number_of_nodes + 1 }}"
    agentLabelSelector:
      nodeLabelKey: infraenv
      nodeLabelValue: classic-baremetal
    configs:
      - "nm-conf-{{ cluster_name }}"
      - worker-kubeconfig
mcConfig:
  - "nm-conf-{{ cluster_name }}"
  - worker-kubeconfig
```

## GitOps Integration

### Workflow

1. **Repository Initialization**: Clone or open existing GitOps repository
2. **Branch Creation**: Create feature branch `add-cluster-<cluster-name>-<site>`
3. **Path Validation**: Ensure directory structure exists or create it
4. **File Generation**: Generate cluster configuration file
5. **Commit**: Commit changes with descriptive message
6. **Push**: Push branch to remote repository

### Manual GitOps Steps

After running the generator:

1. Create a merge/pull request for the generated branch
2. Review the generated configuration
3. Merge to main branch
4. Apply configurations through your GitOps workflow

## CLI Reference

### Global Options

- `--log-level`: Set logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `--log-file`: Path to log file

### Commands

#### `generate`

Generate cluster configuration and optionally commit to GitOps repository.

Options:
- `--cluster-name`: Cluster name (required)
- `--site`: Deployment site (required)
- `--nodes`: Number of nodes (required)
- `--mce-name`: MCE instance name (required)
- `--environment`: Environment (prod/prep) (required)
- `--flavor`: Template flavor (default: default)
- `--repo-path`: GitOps repository path
- `--remote-url`: Remote repository URL
- `--dry-run`: Generate without Git operations
- `--output-file`: Output file for dry-run

#### `list-flavors`

List all available cluster flavors.

#### `validate-flavor`

Validate a specific flavor template.

#### `preview`

Preview generated configuration without creating files.

## Development

### Project Structure

```
src/mce_cluster_generator/
├── __init__.py
├── cli.py                    # CLI interface
├── models/                   # Pydantic models
│   ├── input.py             # Input validation
│   └── cluster.py           # Cluster configuration
├── generators/              # Core generation logic
│   ├── template_loader.py   # Template management
│   └── cluster_generator.py # Main generator
├── git_ops/                 # GitOps integration
│   ├── repository.py        # Git operations
│   └── path_validator.py    # Path validation
├── templates/               # Flavor templates
│   ├── default.yaml
│   ├── portworks.yaml
│   └── powerflex.yaml
└── utils/                   # Utilities
    ├── logging_config.py    # Logging setup
    └── exceptions.py        # Custom exceptions
```

### Adding New Features

1. **New Flavors**: Add YAML templates in `templates/` directory
2. **Validation Rules**: Extend Pydantic models in `models/`
3. **CLI Commands**: Add new commands in `cli.py`
4. **Error Handling**: Add custom exceptions in `utils/exceptions.py`

### Testing

```bash
# Run tests (when available)
pytest tests/

# Validate a flavor
mce-gen validate-flavor default

# Test generation with dry-run
mce-gen generate --cluster-name test --site test --nodes 1 --mce-name test --environment prep --dry-run
```

## Error Handling

The generator includes comprehensive error handling:

- **ValidationError**: Input parameter validation failures
- **TemplateError**: Template loading or rendering issues
- **GitOpsError**: Git operation failures
- **PathValidationError**: Repository path issues
- **ConfigurationError**: Configuration problems

## Logging

Logging levels and outputs:

- **DEBUG**: Detailed operation information
- **INFO**: General operation progress
- **WARNING**: Non-fatal issues
- **ERROR**: Operation failures
- **CRITICAL**: System-level failures

## Security Considerations

- Validates all input parameters
- Prevents path traversal attacks
- Does not expose sensitive information in logs
- Follows security best practices for Git operations

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Update documentation
6. Submit a pull request

## License

[Your License Here]

## Support

For issues and feature requests, please use the GitHub issue tracker.