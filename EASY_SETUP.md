# 🎯 Easy Setup: Just Edit Your Username Here!

Instead of editing multiple paths in `config.yaml`, just update your username in `config/user_settings.txt`:

## Quick Setup

1. **Open** `config/user_settings.txt`
2. **Replace** `YourUsername` with your actual Windows username
3. **Save** the file
4. **Run** the engine - all paths will automatically update!

### Example:

**Before:**
```
USERNAME=YourUsername
```

**After:**
```
USERNAME=John
```

Now all these paths automatically become:
- `C:/Users/John/Downloads`
- `C:/Users/John/Documents`
- `C:/Users/John/Desktop`
- etc.

## How It Works

The config system reads `user_settings.txt` and automatically replaces:
- `{USERNAME}` placeholders
- All instances of `YourUsername`

This way, you **never have to edit** `config.yaml` directly for basic setup!

## Advanced: Custom Paths

You can also set custom paths in `user_settings.txt`:

```
USERNAME=John
DOWNLOADS_PATH=D:/MyDownloads
DOCUMENTS_PATH=E:/MyDocuments
```

Then use them in `config.yaml`:
```yaml
watched_directories:
  - path: "{DOWNLOADS_PATH}"
    enabled: true
```

## Benefits

✅ **One place to edit** - just your username  
✅ **Automatic path generation** - no manual find/replace  
✅ **Easy to change** - update once, affects everywhere  
✅ **Keep config.yaml clean** - no personal info in the main config  

---

**Just update `config/user_settings.txt` and you're ready to go!** 🚀
