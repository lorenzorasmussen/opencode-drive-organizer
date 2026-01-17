# Google Drive Autonomous Organization System

Fully automated AI-powered file organization for Google Drive with zero human intervention after initial setup.

## Research Integration

This system implements findings from four comprehensive research documents:

1. **File Organization Research**: 00-ORGANIZED convention, keyword-based semantic organization, fast duplicate detection
2. **Semantic Analysis Report**: 10-dimensional semantic analysis with risk assessment and predictive analytics
3. **Google Drive Organization**: Proven structure from 15-minute organization run
4. **Advanced Features**: Fast duplicate detection (xxHash/Blake3), performance monitoring, tool integration, local LLM

## Architecture

### 1. Sync Layer (Hybrid for Maximum Flexibility)
- **Google Drive Desktop**: Real-time sync of active folders
- **rclone**: CLI-based sync for pattern-based downloads, large files
- **Google Drive API**: Selective on-demand fetching, metadata operations

### 2. Analysis Layer (10-Dimensional Semantic Analysis)
- **10-Dimensional Semantic Engine**: Type, Location, Age, Size, Git Activity, Reversibility, Personal Data, Context, Predictive Factors
- **Confidence Scoring**: Weighted multi-factor scoring (85%+ confidence = autonomous)
- **Risk Assessment**: Critical, High, Medium, Low risk levels with appropriate actions

### 3. AI Orchestrator (OpenCode Agents + Local LLM)
- **@explore**: Pattern detection, folder structure analysis
- **@librarian**: Content categorization, semantic analysis
- **@document-writer**: Report generation, documentation
- **Local LLM (Ollama)**: Privacy-first AI for low-confidence files
- **Agent caching**: 24-hour TTL for reduced API calls
- **Feedback loop**: Manual corrections improve accuracy over time

### 4. Execution Layer (Confidence-Based Automation)
- **Confidence thresholds**:
  - 0.9-1.0: Execute immediately, no review
  - 0.7-0.9: Execute with optional review
  - 0.5-0.7: Generate proposal, require confirmation
  - <0.5: Skip, escalate to human
- **Rollback safety**: One-command undo with full operation logs
- **Validation gates**: 3-5 folders, naming compliance, no duplicates

### 5. Performance Optimization
- **Fast duplicate detection**: xxHash/Blake3 (2.3s/GB vs MD5 4.5s/GB)
- **Smart caching**: Agent responses, folder IDs, file metadata
- **Batch processing**: 100 files per API call
- **Parallel operations**: GNU parallel for safe file moves
- **Tool integration**: fd (10x find), fzf (fuzzy search), ripgrep (100x grep)

## Features

- ✅ **Autonomous AI Orchestration**: Confidence-based execution with learning loop
- ✅ **10-Dimensional Analysis**: Risk-aware, predictive categorization
- ✅ **Rollback Safety**: One-click undo for all operations
- ✅ **Hybrid Sync**: Google Drive Desktop + rclone + API
- ✅ **Performance Optimized**: Fast tools, intelligent caching, batch operations
- ✅ **Security First**: Encrypted credentials, pre-commit hooks
- ✅ **Comprehensive Logging**: All operations audit-trailed
- ✅ **Learning System**: Improves accuracy from user feedback
- ✅ **Fast Duplicate Detection**: xxHash/Blake3 for large datasets
- ✅ **Performance Monitoring**: Disk usage thresholds, daemon alerts
- ✅ **Local LLM**: Ollama integration for privacy-first AI

## Installation

### Prerequisites

1. **Python 3.10+**
   ```bash
   python3 --version
   ```

2. **Google Drive API Credentials**
   - Create project in Google Cloud Console
   - Enable Drive API
   - Download OAuth client secret
   - Save as `config/client_secret.json`

3. **Dependencies**
   ```bash
   pip3 install -r requirements.txt
   ```

4. **Fast tools (for performance)**
   ```bash
   brew install fd fzf ripgrep tree nnn
   brew install rdfind jdupes  # Fast duplicate detection
   ```

5. **rclone (for sync)**
   ```bash
   brew install rclone
   ```

6. **Ollama (for local AI)**
   ```bash
   brew install ollama
   ollama pull llama2
   ```

### Setup

```bash
# Clone or create directory structure
cd ~/.config/opencode/systems/google-drive-organizer

# Initial OAuth setup
python3 src/setup.py --oauth

# Verify installation
bash tests/integration_test.sh
```

## Usage

### Run Autonomous Organization

```bash
@opencode-google-drive-organizer organize
```

System autonomously: scans → analyzes → organizes → reports

### Status Check

```bash
@opencode-google-drive-organizer status
```

Shows last execution, current confidence levels, pending operations.

### Rollback (Emergency Undo)

```bash
@opencode-google-drive-organizer rollback --date 2025-01-14
```

Executes inverse operations to undo last organization.

## Configuration

Edit `config/settings.yaml` to customize:

- **Confidence Threshold**: When to auto-execute (default: 0.7)
- **Batch Size**: API operations per batch (default: 100)
- **Schedule**: When to run (default: weekly Sundays)
- **Folder Template**: Customize default structure

## Project Structure

```
~/.config/opencode/systems/google-drive-organizer/
├── config/               # Credentials and settings
├── src/                  # All Python source code
├── data/                 # Inventories, proposals, cache
├── logs/                 # Execution logs
├── output/               # Reports and rollback scripts
├── bin/                  # CLI entry point
├── tests/                # Test suite
├── agent/                # OpenCode agent config
└── docs/                 # User guides
```

## License

MIT

## Contributing

Open source contribution welcome via GitHub issues.
