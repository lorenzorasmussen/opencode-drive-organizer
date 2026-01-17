# Google Drive Organizer Agent

## Purpose

Autonomous AI-powered file organization for Google Drive with zero human intervention after initial OAuth setup.

## How It Works

1. **Scan**: Scan local files using file scanner
2. **Analyze**: Use pattern discovery and semantic analyzer to categorize
3. **Propose**: Generate intelligent folder structure proposals
4. **Organize**: Move/categorize files based on analysis
5. **Monitor**: Track disk usage and system performance
6. **Learn**: Improve accuracy from user feedback

## Architecture

### Components

- **File Scanner**: Fast file discovery with filtering
- **Duplicate Detector**: xxHash/Blake3 tiered hashing
- **Semantic Analyzer**: 10-dimensional risk-aware categorization
- **Pattern Discovery**: Detect naming and organization patterns
- **Learning System**: Learn from manual corrections
- **Config Manager**: Load/save configuration
- **Performance Monitor**: Track execution times and disk usage
- **Tool Integration**: Fast tools (fd, fzf, ripgrep, nnn)

### Confidence-Based Automation

| Confidence | Action |
|------------|--------|
| 0.9-1.0 | Execute immediately, no review |
| 0.7-0.9 | Execute, log for optional review |
| 0.5-0.7 | Generate proposal, require human confirmation |
| <0.5 | Skip, escalate to human |

### Commands

### Initial Setup (One-Time)

```bash
cd ~/.config/opencode/systems/google-drive-organizer

# Configure settings
edit config/settings.yaml

# Install dependencies
pip3 install -r requirements.txt

# Run first scan
python3 src/main.py scan .
```

### Run Organization

```bash
python3 src/main.py organize .
```

System autonomously: scans → analyzes → organizes → reports

### Check Status

```bash
python3 src/main.py status
```

Shows last execution, current confidence levels, pending operations.

### Rollback (Emergency Undo)

Rollback scripts are automatically generated in `output/rollback-scripts/` for each organization run.

### Configuration

Edit `config/settings.yaml` to customize:

- **Confidence Threshold**: When to auto-execute (default: 0.9)
- **Batch Size**: Files per operation (default: 100)
- **Schedule**: When to run (default: weekly Sundays)
- **Folder Template**: Customize default structure
```

## Usage Examples

```bash
# Scan current directory
python3 src/main.py scan .

# Organize with dry-run
python3 src/main.py organize . --dry-run

# Find duplicates
python3 src/main.py duplicates .

# Analyze patterns
python3 src/main.py analyze .

# Get system status
python3 src/main.py status
```
