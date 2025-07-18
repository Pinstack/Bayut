# Git Hooks for Code Quality

This project uses Git hooks to automatically enforce code quality standards before commits and pushes.

## Available Hooks

### Pre-Commit Hook (`.git/hooks/pre-commit`)

**When it runs:** Before each commit
**What it checks:**
- ✅ Black formatting
- ✅ Ruff linting
- ✅ Pytest tests

**Purpose:** Ensures basic code quality before committing changes.

### Pre-Push Hook (`.git/hooks/pre-push`)

**When it runs:** Before pushing to remote repository
**What it checks:**
- ✅ Black formatting
- ✅ Ruff linting
- ✅ Flake8 comprehensive linting
- ✅ Pytest tests
- ⚠️ Vulture dead code detection (warning only)

**Purpose:** Ensures comprehensive code quality before sharing code with others.

## How It Works

### Automatic Enforcement

1. **Pre-Commit:** When you run `git commit`, the hook automatically runs
2. **Pre-Push:** When you run `git push`, the hook automatically runs
3. **Blocking:** If any check fails, the operation is blocked
4. **Guidance:** Clear error messages tell you how to fix issues

### Example Output

```bash
$ git push
🔍 Running Pre-Push Code Quality Checks...
==========================================
📦 Checking development dependencies...

🎨 Running Black (code formatter)...
✅ Black passed!

🔧 Running Ruff (fast linter)...
✅ Ruff passed!

🐍 Running Flake8 (comprehensive linter)...
✅ Flake8 passed!

🧪 Running Pytest (tests)...
✅ All tests passed!

🦅 Running Vulture (dead code detection)...
✅ Vulture completed!

🎉 All code quality checks passed!
==================================
✅ Push allowed - code meets quality standards!
```

## Requirements

### Environment Setup

1. **Virtual Environment:** Must be activated (`source .venv/bin/activate`)
2. **Dependencies:** Development tools automatically installed if missing
3. **Project Root:** Must run from project root directory

### Dependencies

The hooks automatically install these tools if missing:
- `ruff` - Fast linter and formatter
- `black` - Code formatter
- `flake8` - Comprehensive linter
- `vulture` - Dead code detection
- `pytest` - Testing framework

## Troubleshooting

### Hook Not Running

**Problem:** Git hooks not executing
**Solution:** Ensure hooks are executable:
```bash
chmod +x .git/hooks/pre-commit
chmod +x .git/hooks/pre-push
```

### Virtual Environment Issues

**Problem:** "Virtual environment not activated" error
**Solution:** Activate the virtual environment:
```bash
source .venv/bin/activate
```

### Formatting Issues

**Problem:** Black formatting check fails
**Solution:** Run the format script:
```bash
./scripts/format.sh
```

### Linting Issues

**Problem:** Ruff or Flake8 checks fail
**Solution:** Fix issues manually or use auto-fix:
```bash
ruff check --fix src/ tests/ bayut.py
```

### Test Failures

**Problem:** Pytest tests fail
**Solution:** Fix failing tests before committing/pushing

## Bypassing Hooks (Emergency Only)

⚠️ **Warning:** Only use in emergencies when you need to push critical fixes

### Skip Pre-Commit Hook
```bash
git commit --no-verify -m "Emergency fix"
```

### Skip Pre-Push Hook
```bash
git push --no-verify
```

## Customization

### Modifying Hook Behavior

Edit the hook files in `.git/hooks/`:
- `pre-commit` - Modify pre-commit checks
- `pre-push` - Modify pre-push checks

### Adding New Checks

To add a new code quality check:

1. Edit the appropriate hook file
2. Add your check after the existing checks
3. Use the same pattern:
   ```bash
   echo "🔍 Running Your Check..."
   if ! your_check_command; then
       echo "❌ Your check failed."
       echo "   Operation blocked for code quality reasons."
       exit 1
   fi
   echo "✅ Your check passed!"
   ```

## Benefits

### For Developers
- **Catch Issues Early:** Problems found before sharing code
- **Consistent Quality:** All code meets the same standards
- **Automated Workflow:** No need to remember to run checks manually

### For the Project
- **Maintainable Code:** Consistent formatting and style
- **Reliable Tests:** All commits have passing tests
- **Professional Standards:** Code quality enforced automatically

## Integration with CI/CD

These hooks complement CI/CD pipelines by:
- **Catching Issues Locally:** Problems found before reaching CI
- **Faster Feedback:** Immediate feedback during development
- **Reduced CI Failures:** Fewer failed builds due to code quality issues

---

**Note:** These hooks are part of the project's commitment to maintaining high code quality standards. They help ensure that all code in the repository meets professional standards. 