# CodeBlur

A powerful GUI tool for obfuscating and deobfuscating code strings with intelligent clipboard integration. Perfect for anonymizing code samples, protecting sensitive information, or sharing code snippets safely.

## Features

- 🎨 **Clean Neubrutalist UI** - Modern, minimalist design with bold colors
- 🔄 **Auto-Obfuscate Strings** - Automatically replace all string literals with AI-like identifiers
- 🗑️ **Remove Comments** - Strip comments from code in all major languages
- 📋 **Clipboard Integration** - Ctrl+V to load, one-click to copy
- ↩️ **Undo Support** - Ctrl+Z to undo up to 20 actions
- 🎯 **Click to Obfuscate** - Click any word to obfuscate/deobfuscate it
- 💾 **Persistent Mappings** - Mappings saved automatically for consistency
- 🟢 **Deobfuscate Button** - Restore original text with one click

## Installation

```bash
pip install codeblur
```

## Usage

Launch the application:

```bash
codeblur
```

Or run from Python:

```python
from codeblur import main
main()
```

## Keyboard Shortcuts

- **Ctrl+V** - Load text from clipboard
- **Ctrl+Z** - Undo last action

## Buttons

- **COPY AND CLOSE** - Copy obfuscated text to clipboard and exit
- **AUTO-OBFUSCATE STRINGS** - Automatically obfuscate all string literals
- **REMOVE COMMENTS** - Remove all comments from code
- **DEOBFUSCATE** - Show and copy deobfuscated text (restores original strings)
- **CLEAR** - Clear all mappings (2-click confirmation)

## Supported Languages

Comment removal works with:
- C, C++, C#, Java, JavaScript, Go, Rust, Swift, Kotlin
- Python, Ruby, Perl, Shell scripts
- HTML, XML
- SQL, Lua, Visual Basic

## How It Works

1. **Load Code**: Press Ctrl+V or paste code into the editor
2. **Obfuscate**: Click "AUTO-OBFUSCATE STRINGS" or click individual words
3. **Remove Comments**: Optional - click "REMOVE COMMENTS"
4. **Copy**: Click "COPY AND CLOSE" to copy and exit
5. **Deobfuscate**: Click "DEOBFUSCATE" to restore original text

## Example

**Before:**
```csharp
var response = await client.GetAsync("/api/users");
// Fetch user data
Console.WriteLine("Request completed");
```

**After Auto-Obfuscate:**
```csharp
var response = await client.GetAsync("PERSON001");
// Fetch user data
Console.WriteLine("ID001");
```

**After Remove Comments:**
```csharp
var response = await client.GetAsync("PERSON001");
Console.WriteLine("ID001");
```

## Features in Detail

### Auto-Obfuscate Strings
- Skips interpolated strings (preserves `{variables}`)
- Skips strings inside comments
- Generates identifiers like PERSON001, ENTITY042, ORG003
- Consistent mapping - same string always gets same identifier

### Click to Obfuscate/Deobfuscate
- Click any word to obfuscate it
- Click an obfuscated identifier to restore original
- Blue highlighting shows obfuscated text

### Undo System
- Tracks up to 20 actions
- Restores both text and mappings
- Press Ctrl+Z to undo

### 2-State Clear Button
- First click: Button turns red "CONFIRM CLEAR?"
- Second click: Executes clear operation
- Auto-resets after 3 seconds

## License

MIT License
