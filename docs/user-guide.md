# Google Drive Organizer - User Guide

## Quick Start

### Prerequisites

1. **Python 3.10+**
   ```bash
   python3 --version
   ```

2. **Google Drive API Credentials**
   - Create project in Google Cloud Console
   - Enable Drive API
   - Download OAuth client secret
   - Save as `config/credentials.json`

3. **Dependencies**
   ```bash
   pip3 install -r requirements.txt
   ```

4. **Fast Tools** (recommended for performance)
   ```bash
   brew install fd fzf ripgrep tree nnn
   ```

### Initial Setup

```bash
# Navigate to project
cd ~/.config/opencode/systems/google-drive-organizer

# Test installation
python3 -c "import yaml; print('✓ YAML available')"
python3 -c "import pandas; print('✓ Pandas available')"

# Run a quick scan test
python3 src/main.py scan . --verbose
```

## Usage

### Run Organization

```bash
# Autonomous organization
python3 src/main.py organize .

# Scan files only
python3 src/main.py scan .

# Find duplicates
python3 src/main.py duplicates .

# Analyze files
python3 src/main.py analyze .
```

### Check Status

```bash
# Check last run
python3 src/main.py status

# View statistics
python3 src/main.py stats
```

### Configuration

Edit `config/settings.yaml` to customize behavior:

```yaml
confidence_thresholds:
  auto_execute: 0.9
  review: 0.5
  skip: 0.5

automation:
  schedule_scan: weekly
  schedule_organization: weekly
  auto_cleanup_days: 7

ollama:
  enabled: true
  model: llama2
  temperature: 0.3
```

## Commands

| Command | Description |
|---------|-------------|
| `scan` | Scan files and generate inventory |
| `organize` | Auto-organize files based on AI analysis |
| `duplicates` | Find duplicate files |
| `analyze` | Analyze files with semantic engine |
| `status` | Show system status and statistics |
| `help` | Show this help message |

## Output

All commands output JSON for easy integration with other tools:
```bash
python3 src/main.py scan . | jq '.status'
```

## Troubleshooting

### Common Issues

**Issue**: Import errors
- **Solution**: Make sure you're in project root: `cd ~/.config/opencode/systems/google-drive-organizer`
- **Solution**: Run `pip3 install -r requirements.txt` to install dependencies

**Issue**: Google Drive API not connecting
- **Solution**: Ensure OAuth credentials are in `config/credentials.json`
- **Solution**: Verify API is enabled in Google Cloud Console

**Issue**: Ollama not responding
- **Solution**: Run `ollama pull llama2` to download model
- **Solution**: Check Ollama is running: `ollama list`
- **Solution**: Verify API URL: http://localhost:11434

**Issue**: CLI not found
- **Solution**: Add project bin directory to PATH:
  ```bash
  export PATH="$PATH:~/.config/opencode/systems/google-drive-organizer/bin:$PATH"
  ```

## Getting Help

```bash
# Run integration tests
./tests/integration_test.sh

# View detailed logs
tail -50 logs/executor-*.log

# Check git status
git status
git log --oneline -5
```

## Best Practices

1. **Start with a test run**: Use `scan` command with small directory first
2. **Check before committing**: Run tests and verify all pass
3. **Review proposals**: Use `--dry-run` flag to see what will change
4. **Keep backups**: Rollback scripts are automatically generated
5. **Monitor logs**: Check `logs/` directory for detailed execution info
