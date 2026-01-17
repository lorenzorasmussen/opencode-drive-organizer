# Google Drive Organizer - Troubleshooting Guide

## Common Errors

### 1. Import Errors

**Error**: `ModuleNotFoundError: No module named 'src.xxx'`

**Cause**: Python not finding modules in `src/` directory

**Solutions**:
```bash
# Make sure you're in project root
cd ~/.config/opencode/systems/google-drive-organizer

# Verify src/ directory exists
ls -la src/

# Try running from project root
python3 -c "import sys; sys.path.insert(0, '.'); from src.config_manager import ConfigManager; print('✓ Import works')"
```

### 2. Configuration Errors

**Error**: `FileNotFoundError: config/settings.yaml not found`

**Cause**: Config file doesn't exist yet

**Solution**: Config manager uses defaults if file missing
```bash
# Config manager creates defaults automatically
python3 -c "from src.config_manager import ConfigManager; cm = ConfigManager(); print(cm.get('ollama.enabled'))"
```

### 3. Google Drive API Errors

**Error**: `AuthenticationError: Could not authenticate`

**Cause**: Invalid or missing OAuth credentials

**Solutions**:
```bash
# Check if credentials file exists
ls -la config/credentials.json

# Verify format (valid JSON)
python3 -c "import json; json.load(open('config/credentials.json'))"

# Test API connection
python3 -c "
from src.google_drive_api import GoogleDriveAPI
api = GoogleDriveAPI()
print(f'Authenticated: {api.authenticated}')
"
```

### 4. Ollama Errors

**Error**: `ConnectionError: Cannot connect to Ollama API`

**Cause**: Ollama not running or wrong port

**Solutions**:
```bash
# Check if Ollama is running
ollama list

# Test connection
curl http://localhost:11434/api/tags

# Pull model if needed
ollama pull llama2
```

### 5. Tool Integration Errors

**Error**: `FileNotFoundError: fd not found`

**Cause**: Fast tools not installed

**Solution**: Tools fall back to Python implementations
```bash
# Install tools (optional)
brew install fd fzf ripgrep nnn

# Or continue with Python fallbacks
python3 src/main.py scan .  # Will use Python implementations
```

### 6. Permission Errors

**Error**: `PermissionError: [Errno 13] Permission denied`

**Cause**: File permissions or executable bit not set

**Solutions**:
```bash
# Make script executable
chmod +x bin/gdo

# Fix directory permissions
chmod 755 data/ logs/ output/

# Fix credentials file (important!)
chmod 600 config/credentials.json
```

### 7. CLI Errors

**Error**: `SystemExit: 2` (exit on error)

**Cause**: Invalid command or arguments

**Solutions**:
```bash
# Show help for valid commands
python3 src/main.py help

# Run with verbose for debugging
python3 src/main.py scan . --verbose

# Dry-run mode for testing
python3 src/main.py organize . --dry-run
```

### 8. Test Failures

**Error**: Tests failing with import or assertion errors

**Solutions**:
```bash
# Run integration test suite
./tests/integration_test.sh

# Run specific test
python3 -m pytest tests/test_config_manager.py::test_load_default_config -v

# Check Python version
python3 --version  # Should be 3.10+
```

### Debug Mode

Enable debug output:

```bash
# Set environment variable
export DEBUG=1

# Run command with debug output
python3 src/main.py scan . --debug
```

### Reset Configuration

If configuration gets corrupted:

```bash
# Reset to defaults
python3 -c "
from src.config_manager import ConfigManager
cm = ConfigManager()
cm.reset_to_defaults()
cm.save()
print('✓ Configuration reset to defaults')
"
```

## Log Locations

- **Execution logs**: `logs/executor-YYYY-MM-DD.log`
- **Duplicate results**: `data/duplicates/`
- **Organization proposals**: `data/proposals/`
- **Rollback scripts**: `output/rollback-scripts/rollback-YYYY-MM-DD.sh`

## Support

For issues not covered here:

1. Check the logs: `tail -50 logs/executor-*.log`
2. Run integration tests: `./tests/integration_test.sh`
3. Review documentation: `cat docs/user-guide.md`
4. Check git history: `git log --oneline -10`

## Getting More Help

```bash
# Check git status
git status

# View recent changes
git diff HEAD~3

# Revert last commit if needed
git revert HEAD
```
