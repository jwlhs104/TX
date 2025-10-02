# Documentation Organization

All documentation has been organized into the `docs/` directory for better clarity.

## 📁 Directory Structure

```
TX/
├── README.md                      # Main project overview (kept in root)
│
├── docs/                          # 📚 All documentation
│   ├── README.md                  # Documentation index (start here)
│   ├── QUICKSTART.md              # 5-minute quick start guide
│   ├── NEW_FEATURES.md            # Feature overview
│   ├── IMPROVEMENTS.md            # Technical improvements
│   ├── CLEANUP_SUMMARY.md         # File reorganization
│   ├── CLAUDE.md                  # Code architecture reference
│   └── ORGANIZATION.md            # This file
│
├── data/                          # Data files
│   └── README.md                  # Data format documentation
│
├── cli.py, config.py, etc.        # Python source files
├── tests/                         # Unit tests
├── utils/                         # Utility scripts
├── output/                        # Generated outputs
└── logs/                          # Log files
```

## 📖 Documentation Guide

### Quick Reference

| Document | Purpose | Audience |
|----------|---------|----------|
| **README.md** (root) | Project overview & results | Everyone |
| **docs/README.md** | Documentation index | Everyone |
| **docs/QUICKSTART.md** | Get started in 5 minutes | New users |
| **docs/NEW_FEATURES.md** | Feature highlights | All users |
| **docs/IMPROVEMENTS.md** | Technical details | Developers |
| **docs/CLAUDE.md** | Code architecture | AI/Developers |
| **data/README.md** | Data formats | Data engineers |

### Reading Path by Role

#### 👤 New User
1. `README.md` (root) - Overview
2. `docs/QUICKSTART.md` - Setup & run
3. `docs/NEW_FEATURES.md` - Explore features

#### 💻 Developer
1. `docs/CLAUDE.md` - Architecture
2. `docs/IMPROVEMENTS.md` - Design decisions
3. `docs/QUICKSTART.md` - Workflows

#### 🔄 Migrating User
1. `docs/IMPROVEMENTS.md` - What changed
2. `docs/ORGANIZATION.md` - Where things moved
3. `docs/QUICKSTART.md` - New workflows

## 🗂️ What Moved

### From Root → docs/
- `QUICKSTART.md` → `docs/QUICKSTART.md`
- `IMPROVEMENTS.md` → `docs/IMPROVEMENTS.md`
- `NEW_FEATURES.md` → `docs/NEW_FEATURES.md`
- `CLEANUP_SUMMARY.md` → `docs/CLEANUP_SUMMARY.md`
- `CLAUDE.md` → `docs/CLAUDE.md`

### Why This Organization?

✅ **Cleaner root** - Only essential files visible
✅ **Better navigation** - All docs in one place
✅ **Easier maintenance** - Organized by purpose
✅ **Professional structure** - Industry standard
✅ **Discoverability** - Clear documentation hierarchy

## 🔗 Link Updates

All internal documentation links have been updated to reflect the new structure:

- Absolute paths: `/docs/QUICKSTART.md`
- Relative paths from docs: `QUICKSTART.md` or `../README.md`
- Relative paths from root: `docs/QUICKSTART.md`

## 📌 Quick Access

From project root:
```bash
# View documentation index
cat docs/README.md

# Open quick start guide
cat docs/QUICKSTART.md

# List all documentation
ls docs/
```

## 🎯 Best Practices

### When Adding New Documentation

1. **Place in docs/** - Keep root clean
2. **Update docs/README.md** - Add to index
3. **Use relative links** - For portability
4. **Follow naming** - Use UPPERCASE.md for guides

### When Referencing Docs

From root files:
```markdown
[Quick Start](docs/QUICKSTART.md)
```

From docs/ files:
```markdown
[Main README](../README.md)
[Quick Start](QUICKSTART.md)
```

From code files:
```python
# See docs/CLAUDE.md for architecture details
```

## 📊 File Count Summary

- **Root directory**: 15 essential files
- **docs/ directory**: 7 documentation files
- **Total reduction**: ~30% fewer files in root

## 🌟 Benefits

| Aspect | Before | After |
|--------|--------|-------|
| Root files | 20+ | 15 |
| Doc location | Scattered | Centralized |
| Navigation | Confusing | Clear |
| First impression | Cluttered | Professional |

---

**Organization Date**: 2025-10-02
**Status**: Complete ✅
