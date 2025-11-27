import tkinter as tk
from tkinter import ttk, messagebox
import pyperclip
import json
import os
import random
import string
import threading

class CodeBlur:
    # =========================================================================
    # OBFUSCATION LEVELS CONFIGURATION
    # =========================================================================
    # Each level defines what actions to perform when AUTO-OBFUSCATE is clicked.
    # Levels are cumulative - clicking again advances to the next level.
    # After all levels are done, clicking again resets to level 0 (no action).
    #
    # To add a new level: add an entry here and implement the action method.
    # Action methods must exist as instance methods (e.g., self._action_obfuscate_identifiers)
    # =========================================================================
    OBFUSCATION_LEVELS = {
        1: {
            "name": "BLUR",
            "description": "Obfuscate unknown identifiers (variables, functions, classes)",
            "actions": ["obfuscate_identifiers"],
        },
        2: {
            "name": "STEALTH",
            "description": "Replace comments with placeholders and collapse empty lines",
            "actions": ["remove_comments", "remove_empty_lines"],
        },
        3: {
            "name": "PHANTOM",
            "description": "Obfuscate string contents, GUIDs, and paths",
            "actions": ["obfuscate_strings", "obfuscate_guids", "obfuscate_paths"],
        },
        4: {
            "name": "SKELETON",
            "description": "Remove function/method bodies, keep only signatures",
            "actions": ["remove_function_bodies"],
        },
    }

    def __init__(self, root):
        self.root = root
        self.root.title("CODEBLUR")
        self.root.geometry("900x700")

        # Track current obfuscation level (0 = not started)
        self.current_obfuscation_level = 0

        # Loading state for async obfuscation
        self.is_obfuscating = False

        # Neubrutalist monochrome with blue accent color scheme
        self.bg_color = "#FFFFFF"
        self.primary_color = "#000000"  # Pure black
        self.secondary_color = "#E0E0E0"  # Light gray
        self.accent_color = "#0066FF"  # Bright blue accent
        self.text_color = "#000000"
        self.border_color = "#000000"
        self.hover_color = "#CCCCCC"

        self.root.configure(bg=self.bg_color)

        # User data directory (cross-platform)
        self.app_data_dir = self.get_app_data_dir()
        os.makedirs(self.app_data_dir, exist_ok=True)

        # Storage file for mappings (in user data dir)
        self.mappings_file = os.path.join(self.app_data_dir, "obfuscation_mappings.json")
        self.mappings = self.load_mappings()


        # Known words dictionary (language-agnostic)
        # Multiple word files are merged together
        package_dir = os.path.dirname(os.path.abspath(__file__))

        # Array of word files to load and merge (in package directory)
        self.word_files = [
            os.path.join(package_dir, "known_words.json"),      # Common programming words
            os.path.join(package_dir, "brand_words.json"),      # Brand/IT company names
            os.path.join(package_dir, "package_words.json"),    # NuGet/npm package names
        ]

        # User can also add custom words in app data dir
        self.user_words_file = os.path.join(self.app_data_dir, "custom_words.json")

        self.known_words = self.load_all_known_words()

        # State tracking for 3-state button (CLEAR -> CONFIRM -> CLOSE)
        self.clear_button_state = 0  # 0=clear, 1=confirm, 2=close
        self.clear_button = None

        # Undo history - stores (text_content, mappings) tuples
        self.undo_stack = []
        self.max_undo_levels = 20

        # Create UI
        self.create_widgets()

        # Load clipboard on startup
        self.load_clipboard()

    def get_app_data_dir(self):
        """Get cross-platform app data directory"""
        import platform
        system = platform.system()

        if system == "Windows":
            base = os.environ.get("APPDATA", os.path.expanduser("~"))
        elif system == "Darwin":  # macOS
            base = os.path.join(os.path.expanduser("~"), "Library", "Application Support")
        else:  # Linux and others
            base = os.environ.get("XDG_DATA_HOME", os.path.join(os.path.expanduser("~"), ".local", "share"))

        return os.path.join(base, "codeblur")

    def load_mappings(self):
        """Load existing mappings from JSON file"""
        if os.path.exists(self.mappings_file):
            try:
                with open(self.mappings_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def save_mappings(self):
        """Save mappings to JSON file"""
        with open(self.mappings_file, 'w', encoding='utf-8') as f:
            json.dump(self.mappings, f, indent=2, ensure_ascii=False)

    def load_all_known_words(self):
        """Load and merge all known words from multiple files"""
        all_words = set()

        # Load from each word file in the array
        for word_file in self.word_files:
            if os.path.exists(word_file):
                try:
                    with open(word_file, 'r', encoding='utf-8') as f:
                        words = json.load(f)
                        all_words.update(words)
                except:
                    pass

        # Load user's custom words if exists
        if os.path.exists(self.user_words_file):
            try:
                with open(self.user_words_file, 'r', encoding='utf-8') as f:
                    words = json.load(f)
                    all_words.update(words)
            except:
                pass

        # If no words loaded, use hardcoded defaults
        if not all_words:
            all_words = self.get_default_known_words()

        return all_words

    def get_default_known_words(self):
        """Return default set of known words (generic, language-agnostic)"""
        return {
            # Common programming verbs
            "get", "set", "is", "has", "can", "should", "will", "did",
            "on", "off", "add", "remove", "create", "delete", "update",
            "find", "fetch", "load", "save", "send", "receive",
            "start", "stop", "init", "reset", "clear", "close", "open",
            "show", "hide", "toggle", "enable", "disable",
            "click", "change", "submit", "focus", "blur",
            "render", "mount", "unmount", "destroy",
            "push", "pop", "shift", "slice", "splice", "concat",
            "join", "split", "trim", "replace", "match", "test", "search",
            "parse", "stringify", "encode", "decode",
            "extend", "implement", "override",
            # Common nouns
            "data", "info", "list", "item", "items", "array", "object",
            "error", "success", "fail", "complete", "pending",
            "event", "handler", "listener", "callback",
            "request", "response", "status", "message",
            "id", "key", "value", "index", "length", "size", "count",
            "name", "type", "state", "config", "options",
            "result", "output", "input", "params", "args",
            "url", "path", "route", "query", "body", "header",
            "text", "font", "style", "display", "position",
            "component", "module", "service", "controller", "model", "view",
            "min", "max", "sum", "avg", "total", "current", "next", "prev",
            "first", "last", "before", "after",
            "timeout", "interval", "delay", "wait",
            # Common prepositions/connectors
            "to", "from", "by", "with", "in", "out", "up", "down",
            "all", "any", "some", "none", "each", "every",
            # Common suffixes/prefixes
            "async", "sync", "Async", "Sync",
            "local", "global", "public", "private", "static",
            # Common keywords (multi-language)
            "true", "false", "null", "new", "this", "self",
            "if", "else", "for", "while", "do", "switch", "case",
            "try", "catch", "finally", "throw", "return",
            "function", "class", "const", "let", "var",
            "import", "export", "default", "require",
        }

    def generate_ai_identifier(self, original_word):
        """Generate AI-like identifier for anonymization"""
        # Check if we already have a mapping
        if original_word in self.mappings:
            return self.mappings[original_word]

        # Generate patterns like: PERSON001, ENTITY042, etc. (no underscores)
        categories = ['PERSON', 'ENTITY', 'ORG', 'ITEM', 'NAME', 'ID', 'REF']
        category = random.choice(categories)

        # Find next available number for this category
        existing_nums = []
        for mapped_value in self.mappings.values():
            if mapped_value.startswith(category) and len(mapped_value) > len(category):
                try:
                    # Extract number after category name
                    num_part = mapped_value[len(category):]
                    if num_part.isdigit():
                        existing_nums.append(int(num_part))
                except:
                    pass

        next_num = max(existing_nums) + 1 if existing_nums else 1
        new_identifier = f"{category}{next_num:03d}"

        return new_identifier

    def create_neubrutalist_button(self, parent, text, command, bg_color):
        """Create a Neubrutalist style button with thick border and solid shadow"""
        # Container frame for shadow effect
        shadow_frame = tk.Frame(parent, bg=self.border_color, highlightthickness=0)

        # Determine text color based on background
        text_color = self.bg_color if bg_color in [self.primary_color, self.accent_color] else self.text_color

        # Button with thick border - all same size
        btn = tk.Button(
            shadow_frame,
            text=text,
            command=command,
            font=("Consolas", 10, "bold"),
            bg=bg_color,
            fg=text_color,
            activebackground=bg_color,
            activeforeground=text_color,
            relief=tk.FLAT,
            borderwidth=5,
            highlightbackground=self.border_color,
            highlightthickness=5,
            cursor="hand2",
            padx=16,
            pady=10
        )
        btn.pack(padx=(0, 5), pady=(0, 5))

        return shadow_frame

    def create_widgets(self):
        """Create the UI components"""
        # Top frame container for button rows
        buttons_container = tk.Frame(self.root, bg=self.bg_color)
        buttons_container.pack(fill=tk.X, padx=8, pady=8)

        # Row 1
        row1 = tk.Frame(buttons_container, bg=self.bg_color)
        row1.pack(pady=(0, 8))

        btn2 = self.create_neubrutalist_button(row1, "COPY AND CLOSE", self.copy_and_close, self.accent_color)
        btn2.pack(side=tk.LEFT, padx=4)

        self.obfuscate_button = self.create_neubrutalist_button(row1, "BLUR", self.obfuscate_all, "#FF6600")
        self.obfuscate_button.pack(side=tk.LEFT, padx=4)

        btn5 = self.create_neubrutalist_button(row1, "DEOBFUSCATE", self.deobfuscate_and_show, "#00CC00")
        btn5.pack(side=tk.LEFT, padx=4)

        self.clear_button = self.create_neubrutalist_button(row1, f"CLEAR ({len(self.mappings)})", self.clear_mappings_2state, self.secondary_color)
        self.clear_button.pack(side=tk.LEFT, padx=4)

        # Row 2
        row2 = tk.Frame(buttons_container, bg=self.bg_color)
        row2.pack()

        btn3 = self.create_neubrutalist_button(row2, "OBFUSCATE STRINGS", self.auto_obfuscate_strings, self.accent_color)
        btn3.pack(side=tk.LEFT, padx=4)

        btn4 = self.create_neubrutalist_button(row2, "REMOVE COMMENTS", self.remove_all_comments, self.accent_color)
        btn4.pack(side=tk.LEFT, padx=4)

        # Main text area with thick border and shadow - zero padding
        text_shadow_frame = tk.Frame(self.root, bg=self.border_color)
        text_shadow_frame.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 8))

        text_border_frame = tk.Frame(
            text_shadow_frame,
            bg="#FFFFFF",
            highlightbackground=self.border_color,
            highlightthickness=6
        )
        text_border_frame.pack(fill=tk.BOTH, expand=True, padx=(0, 8), pady=(0, 8))

        # Scrollbar
        scrollbar = tk.Scrollbar(text_border_frame, width=20, bg=self.accent_color, troughcolor="#FFFFFF")
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Text area
        self.text_area = tk.Text(
            text_border_frame,
            wrap=tk.WORD,
            yscrollcommand=scrollbar.set,
            font=("Consolas", 11),
            bg="#FFFFFF",
            fg=self.text_color,
            borderwidth=0,
            highlightthickness=0,
            padx=12,
            pady=12,
            selectbackground=self.accent_color,
            selectforeground="#FFFFFF",
            insertwidth=0,
            insertofftime=0,
            spacing1=2,
            spacing3=2,
            cursor="hand2",
            exportselection=False
        )
        self.text_area.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        scrollbar.config(command=self.text_area.yview)

        # Bind mouse click event
        self.text_area.bind("<Button-1>", self.on_text_clicked)

        # Bind Ctrl+Z for undo
        self.root.bind("<Control-z>", lambda e: self.undo())

        # Bind Ctrl+V to load clipboard
        self.root.bind("<Control-v>", lambda e: self.load_clipboard())

        # Bind Ctrl+C to copy all text
        self.root.bind("<Control-c>", lambda e: self.copy_all_text())

        # Disable text selection
        self.text_area.bind("<B1-Motion>", lambda e: "break")
        self.text_area.bind("<Double-Button-1>", lambda e: "break")
        self.text_area.bind("<Triple-Button-1>", lambda e: "break")
        self.text_area.bind("<Control-a>", lambda e: "break")
        self.text_area.bind("<Shift-Left>", lambda e: "break")
        self.text_area.bind("<Shift-Right>", lambda e: "break")
        self.text_area.bind("<Shift-Up>", lambda e: "break")
        self.text_area.bind("<Shift-Down>", lambda e: "break")
        self.text_area.bind("<Shift-Home>", lambda e: "break")
        self.text_area.bind("<Shift-End>", lambda e: "break")

        # Tag for obfuscated text - Neubrutalist style with blue accent
        self.text_area.tag_config(
            "obfuscated",
            background=self.accent_color,
            foreground="#FFFFFF",
            font=("Consolas", 11, "bold"),
            relief=tk.RAISED,
            borderwidth=1
        )

    def save_state(self):
        """Save current state to undo stack"""
        text_content = self.text_area.get(1.0, "end-1c")
        mappings_copy = dict(self.mappings)
        self.undo_stack.append((text_content, mappings_copy))

        # Limit undo stack size
        if len(self.undo_stack) > self.max_undo_levels:
            self.undo_stack.pop(0)

    def undo(self):
        """Undo last action"""
        if not self.undo_stack:
            return

        # Get previous state
        text_content, mappings = self.undo_stack.pop()

        # Save current scroll position
        scroll_position = self.text_area.yview()

        # Restore previous state
        self.mappings = mappings
        self.save_mappings()

        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(1.0, text_content)

        # Restore scroll position
        self.text_area.yview_moveto(scroll_position[0])

        # Re-highlight
        self.highlight_obfuscated_text()

    def load_clipboard(self):
        """Load text from clipboard"""
        try:
            clipboard_text = pyperclip.paste()
            if clipboard_text:
                self.save_state()
                self.text_area.delete(1.0, tk.END)
                self.text_area.insert(1.0, clipboard_text)
                self.apply_existing_mappings()
                # Always start at level 0
                self.reset_obfuscation_level()
        except Exception as e:
            pass

    def apply_existing_mappings(self):
        """Apply existing mappings to the loaded text (camelCase-aware)"""
        import re
        text_content = self.text_area.get(1.0, "end-1c")

        # Find all identifiers and apply mappings through camelCase splitting
        identifier_pattern = r'\b[a-zA-Z_][a-zA-Z0-9_]*\b'

        def replace_with_mappings(match):
            word = match.group(0)
            return self.apply_mappings_to_word(word)

        text_content = re.sub(identifier_pattern, replace_with_mappings, text_content)

        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(1.0, text_content)
        self.highlight_obfuscated_text()

    def apply_mappings_to_word(self, word):
        """Apply existing mappings to a word (camelCase-aware, no new mappings created)"""
        # Check if whole word is already obfuscated
        if word in self.mappings.values():
            return word

        # Check if whole word has a mapping
        if word in self.mappings:
            return self.mappings[word]

        # Check if it's an obfuscated identifier pattern
        if self.is_obfuscated_identifier(word):
            return word

        # Split into camelCase parts
        parts = self.split_camel_case(word)

        if len(parts) <= 1:
            # Single word - check if it has a mapping
            if word in self.mappings:
                return self.mappings[word]
            return word

        # Process composite word - apply existing mappings to parts
        result_parts = []
        for part in parts:
            if self.is_obfuscated_identifier(part):
                result_parts.append(part)
            elif part.isdigit():
                result_parts.append(part)
            elif part in self.mappings:
                result_parts.append(self.mappings[part])
            else:
                result_parts.append(part)

        return ''.join(result_parts)

    def highlight_obfuscated_text(self):
        """Highlight all obfuscated text in the text area"""
        for obfuscated in self.mappings.values():
            start = "1.0"
            while True:
                start = self.text_area.search(obfuscated, start, tk.END)
                if not start:
                    break
                end = f"{start}+{len(obfuscated)}c"
                self.text_area.tag_add("obfuscated", start, end)
                start = end
        # Update clear button count
        self.update_clear_button_text()

    def get_word_at_click(self, event):
        """Get the word at the click position"""
        # Get the index of the click
        index = self.text_area.index(f"@{event.x},{event.y}")

        # Get the line and column
        line, col = map(int, index.split('.'))

        # Get the entire line
        line_text = self.text_area.get(f"{line}.0", f"{line}.end")

        # Find word boundaries - treat underscore as separator
        if col >= len(line_text) or not line_text[col].isalnum():
            return None

        # Find start of word (stop at underscore)
        start = col
        while start > 0 and line_text[start - 1].isalnum():
            start -= 1

        # Find end of word (stop at underscore)
        end = col
        while end < len(line_text) and line_text[end].isalnum():
            end += 1

        word = line_text[start:end]
        return word.strip() if word else None

    def on_text_clicked(self, event):
        """Handle text click event - obfuscate or deobfuscate word"""
        word = self.get_word_at_click(event)
        if word and len(word) > 0:
            # Check if the word is already obfuscated
            is_obfuscated = False
            for original, obfuscated in self.mappings.items():
                if obfuscated == word:
                    is_obfuscated = True
                    break

            # If word is already obfuscated, deobfuscate it
            if is_obfuscated:
                self.deobfuscate_word(word)
            else:
                self.obfuscate_word(word)

    def obfuscate_word(self, word):
        """Obfuscate the selected word"""
        # Save state before making changes
        self.save_state()

        # Generate identifier
        identifier = self.generate_ai_identifier(word)

        # Store mapping
        self.mappings[word] = identifier
        self.save_mappings()

        # Save current scroll position
        scroll_position = self.text_area.yview()

        # Replace in text and count occurrences
        text_content = self.text_area.get(1.0, "end-1c")
        count = text_content.count(word)
        text_content = text_content.replace(word, identifier)

        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(1.0, text_content)

        # Restore scroll position
        self.text_area.yview_moveto(scroll_position[0])

        # Highlight obfuscated text
        self.highlight_obfuscated_text()

    def auto_obfuscate_strings(self):
        """Auto-obfuscate all string contents (text within quotes)"""
        import re

        # Save state before making changes
        self.save_state()

        # Save current scroll position
        scroll_position = self.text_area.yview()

        # Get current text content
        text_content = self.text_area.get(1.0, "end-1c")

        # Find all comment regions to exclude from obfuscation
        comment_ranges = []

        # Multi-line comments (/* ... */)
        for match in re.finditer(r'/\*.*?\*/', text_content, re.DOTALL):
            comment_ranges.append((match.start(), match.end()))

        # Single-line comments (// and ///)
        for match in re.finditer(r'//[^\n]*', text_content):
            comment_ranges.append((match.start(), match.end()))

        # Python comments (#)
        for match in re.finditer(r'#[^\n]*', text_content):
            comment_ranges.append((match.start(), match.end()))

        def is_in_comment(pos):
            """Check if a position is within any comment range"""
            return any(start <= pos < end for start, end in comment_ranges)

        def has_interpolation(content):
            """Check if string has interpolation syntax like {variable}"""
            return '{' in content and '}' in content

        # Find all strings within quotes (both single and double quotes)
        # Pattern matches strings with proper escape handling
        # Matches: "string content" or 'string content' including escaped quotes
        # Important: [^"\\\n\r] prevents matching across line breaks
        double_quote_pattern = r'"(?:[^"\\\n\r]|\\[^\n\r])*"'
        single_quote_pattern = r"'(?:[^'\\\n\r]|\\[^\n\r])*'"

        strings_to_replace = []

        # Find double-quoted strings
        for match in re.finditer(double_quote_pattern, text_content):
            # Skip if string is inside a comment
            if is_in_comment(match.start()):
                continue

            full_string = match.group(0)
            string_content = full_string[1:-1]  # Remove quotes

            # Skip empty strings, already obfuscated strings, and interpolated strings
            if (string_content and
                not any(string_content == obf for obf in self.mappings.values()) and
                not has_interpolation(string_content)):
                strings_to_replace.append((match.start(), match.end(), full_string, string_content, '"'))

        # Find single-quoted strings
        for match in re.finditer(single_quote_pattern, text_content):
            # Skip if string is inside a comment
            if is_in_comment(match.start()):
                continue

            full_string = match.group(0)
            string_content = full_string[1:-1]  # Remove quotes

            # Skip empty strings, already obfuscated strings, and interpolated strings
            if (string_content and
                not any(string_content == obf for obf in self.mappings.values()) and
                not has_interpolation(string_content)):
                strings_to_replace.append((match.start(), match.end(), full_string, string_content, "'"))

        if not strings_to_replace:
            return

        # Sort by position (reverse order to replace from end to start, avoiding position shifts)
        strings_to_replace.sort(key=lambda x: x[0], reverse=True)

        # Obfuscate each string
        obfuscated_count = 0
        for start, end, full_string, string_content, quote_char in strings_to_replace:
            # Check if this string content is already mapped
            if string_content not in self.mappings:
                identifier = self.generate_ai_identifier(string_content)
                self.mappings[string_content] = identifier
                obfuscated_count += 1
            else:
                identifier = self.mappings[string_content]

            # Replace the string content in the text
            new_string = f"{quote_char}{identifier}{quote_char}"
            text_content = text_content[:start] + new_string + text_content[end:]

        # Save mappings
        self.save_mappings()

        # Update text area
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(1.0, text_content)

        # Restore scroll position
        self.text_area.yview_moveto(scroll_position[0])

        # Highlight obfuscated text
        self.highlight_obfuscated_text()

    def split_camel_case(self, word):
        """Split camelCase or PascalCase word into parts"""
        import re
        # Split on transitions: lowercase->uppercase, or before sequences of uppercase followed by lowercase
        parts = re.findall(r'[A-Z]?[a-z]+|[A-Z]+(?=[A-Z][a-z]|\d|\W|$)|\d+', word)
        return parts if parts else [word]

    def is_obfuscated_identifier(self, word):
        """Check if word matches our obfuscated identifier pattern (e.g., ENTITY001, PERSON042, GUID001)"""
        import re
        # Match pattern: CATEGORY + NUMBERS (e.g., PERSON001, ENTITY042, ORG003, GUID001, COMMENT001, BODY001, PATH001)
        categories = ['PERSON', 'ENTITY', 'ORG', 'ITEM', 'NAME', 'ID', 'REF', 'GUID', 'COMMENT', 'BODY', 'PATH']
        pattern = r'^(' + '|'.join(categories) + r')\d+$'
        return bool(re.match(pattern, word))

    def auto_obfuscate_word(self, word):
        """Obfuscate a single word for auto-obfuscate, preserving known parts"""
        # Check if word matches our obfuscated identifier pattern (idempotent)
        if self.is_obfuscated_identifier(word):
            return word

        # Check if word is already an obfuscated value (idempotent - don't re-obfuscate)
        if word in self.mappings.values():
            return word

        # Check if the whole word is known (case-insensitive check)
        if word in self.known_words or word.lower() in {w.lower() for w in self.known_words}:
            return word

        # Split into camelCase parts
        parts = self.split_camel_case(word)

        if len(parts) <= 1:
            # Single word, not in dictionary - obfuscate it
            if word not in self.mappings:
                identifier = self.generate_ai_identifier(word)
                self.mappings[word] = identifier
            return self.mappings[word]

        # Process composite word - keep known parts, obfuscate unknown
        result_parts = []
        unknown_sequence = []

        for part in parts:
            # Check if this part is an obfuscated identifier (e.g., ENTITY001)
            if self.is_obfuscated_identifier(part):
                # Flush any unknown sequence first
                if unknown_sequence:
                    unknown_combined = ''.join(unknown_sequence)
                    if unknown_combined not in self.mappings:
                        identifier = self.generate_ai_identifier(unknown_combined)
                        self.mappings[unknown_combined] = identifier
                    result_parts.append(self.mappings[unknown_combined])
                    unknown_sequence = []
                result_parts.append(part)
                continue

            # Check if this part is pure digits (part of obfuscated identifier like "001" in "ID001")
            if part.isdigit():
                # Flush any unknown sequence first
                if unknown_sequence:
                    unknown_combined = ''.join(unknown_sequence)
                    if unknown_combined not in self.mappings:
                        identifier = self.generate_ai_identifier(unknown_combined)
                        self.mappings[unknown_combined] = identifier
                    result_parts.append(self.mappings[unknown_combined])
                    unknown_sequence = []
                result_parts.append(part)
                continue

            # Check if this part is known (case-insensitive)
            is_known = part in self.known_words or part.lower() in {w.lower() for w in self.known_words}

            if is_known:
                # If we have accumulated unknown parts, obfuscate them as a group
                if unknown_sequence:
                    unknown_combined = ''.join(unknown_sequence)
                    if unknown_combined not in self.mappings:
                        identifier = self.generate_ai_identifier(unknown_combined)
                        self.mappings[unknown_combined] = identifier
                    result_parts.append(self.mappings[unknown_combined])
                    unknown_sequence = []
                result_parts.append(part)
            else:
                unknown_sequence.append(part)

        # Handle any remaining unknown parts at the end
        if unknown_sequence:
            unknown_combined = ''.join(unknown_sequence)
            if unknown_combined not in self.mappings:
                identifier = self.generate_ai_identifier(unknown_combined)
                self.mappings[unknown_combined] = identifier
            result_parts.append(self.mappings[unknown_combined])

        return ''.join(result_parts)

    def obfuscate_all(self):
        """Execute next obfuscation level (each level is idempotent) - async"""
        # Prevent multiple clicks while processing
        if self.is_obfuscating:
            return

        self.is_obfuscating = True
        max_level = max(self.OBFUSCATION_LEVELS.keys())

        # Advance to next level (cycle back to 1 if at max)
        self.current_obfuscation_level += 1
        if self.current_obfuscation_level > max_level:
            self.current_obfuscation_level = 1

        # Disable button while processing
        self.set_obfuscate_button_enabled(False)

        # Save state before making changes
        self.save_state()

        # Run obfuscation in background thread
        def do_obfuscation():
            level_config = self.OBFUSCATION_LEVELS[self.current_obfuscation_level]
            for action_name in level_config["actions"]:
                action_method = getattr(self, f"_action_{action_name}", None)
                if action_method:
                    action_method()

            # Schedule UI update on main thread
            self.root.after(0, self.on_obfuscation_complete)

        thread = threading.Thread(target=do_obfuscation, daemon=True)
        thread.start()

    def on_obfuscation_complete(self):
        """Called when obfuscation is done - update UI"""
        self.is_obfuscating = False

        # Re-enable and update button text
        self.set_obfuscate_button_enabled(True)
        self.update_obfuscate_button_text()

    def set_obfuscate_button_enabled(self, enabled):
        """Enable or disable the obfuscate button"""
        for widget in self.obfuscate_button.winfo_children():
            if isinstance(widget, tk.Button):
                if enabled:
                    widget.config(state=tk.NORMAL, bg="#FF6600")
                else:
                    widget.config(state=tk.DISABLED, bg="#CCCCCC")
                break

    def update_obfuscate_button_text(self):
        """Update AUTO-OBFUSCATE button to show current level"""
        # Find the actual button widget inside the shadow frame
        for widget in self.obfuscate_button.winfo_children():
            if isinstance(widget, tk.Button):
                # Always show next level name (level 0 shows level 1 name)
                next_level = self.current_obfuscation_level + 1
                max_level = max(self.OBFUSCATION_LEVELS.keys())
                if next_level > max_level:
                    next_level = 1
                level_name = self.OBFUSCATION_LEVELS[next_level]["name"]
                widget.config(text=level_name)
                break

    def reset_obfuscation_level(self):
        """Reset obfuscation level to 0"""
        self.current_obfuscation_level = 0
        self.update_obfuscate_button_text()

    # =========================================================================
    # OBFUSCATION LEVEL ACTIONS
    # =========================================================================
    # Each action method must be named _action_<action_name> where action_name
    # matches what's in OBFUSCATION_LEVELS config.
    # =========================================================================

    def _action_obfuscate_identifiers(self):
        """Action: Obfuscate all unknown identifiers"""
        import re

        # Save current scroll position
        scroll_position = self.text_area.yview()

        # Get current text content
        text_content = self.text_area.get(1.0, "end-1c")

        # Find all identifiers (words starting with letter or underscore)
        identifier_pattern = r'\b[a-zA-Z_][a-zA-Z0-9_]*\b'

        def replace_identifier(match):
            word = match.group(0)
            return self.auto_obfuscate_word(word)

        # Replace all identifiers
        text_content = re.sub(identifier_pattern, replace_identifier, text_content)

        # Save mappings
        self.save_mappings()

        # Update text area
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(1.0, text_content)

        # Restore scroll position
        self.text_area.yview_moveto(scroll_position[0])

        # Highlight obfuscated text
        self.highlight_obfuscated_text()

    def _action_remove_comments(self):
        """Action: Replace all comments with placeholders (can be deobfuscated)"""
        import re

        # Save current scroll position
        scroll_position = self.text_area.yview()

        # Get current text content
        text_content = self.text_area.get(1.0, "end-1c")

        # Collect all comments with their positions
        # Order matters: check multi-line before single-line to avoid partial matches
        comments_to_replace = []

        # Multi-line comments /* ... */ (C, C++, C#, Java, JS, Go, Rust, etc.)
        for match in re.finditer(r'/\*.*?\*/', text_content, flags=re.DOTALL):
            comments_to_replace.append((match.start(), match.end(), match.group(0)))

        # XML/HTML comments <!-- ... -->
        for match in re.finditer(r'<!--.*?-->', text_content, flags=re.DOTALL):
            comments_to_replace.append((match.start(), match.end(), match.group(0)))

        # Lua multi-line comments --[[ ... ]]
        for match in re.finditer(r'--\[\[.*?\]\]', text_content, flags=re.DOTALL):
            comments_to_replace.append((match.start(), match.end(), match.group(0)))

        # C# XML documentation comments /// (must check before //)
        for match in re.finditer(r'///[^\n]*', text_content):
            # Check not already covered by multi-line
            if not any(s <= match.start() < e for s, e, _ in comments_to_replace):
                comments_to_replace.append((match.start(), match.end(), match.group(0)))

        # Single-line comments // (C, C++, C#, Java, JS, Go, Rust, etc.)
        for match in re.finditer(r'//[^\n]*', text_content):
            # Check not already covered
            if not any(s <= match.start() < e for s, e, _ in comments_to_replace):
                comments_to_replace.append((match.start(), match.end(), match.group(0)))

        # Python/Shell/Ruby comments #
        # Be careful: # in C# is preprocessor, but usually at line start
        for match in re.finditer(r'#[^\n]*', text_content):
            if not any(s <= match.start() < e for s, e, _ in comments_to_replace):
                comments_to_replace.append((match.start(), match.end(), match.group(0)))

        # SQL single-line comments -- (but not --[[ which is Lua)
        for match in re.finditer(r'--(?!\[\[)[^\n]*', text_content):
            if not any(s <= match.start() < e for s, e, _ in comments_to_replace):
                comments_to_replace.append((match.start(), match.end(), match.group(0)))

        if not comments_to_replace:
            return

        # Sort by position (reverse to avoid position shifts)
        comments_to_replace.sort(key=lambda x: x[0], reverse=True)

        # Replace each comment with placeholder
        for start, end, comment_text in comments_to_replace:
            # Skip if already a placeholder
            if re.match(r'^/\*\s*COMMENT\d+\s*\*/$', comment_text):
                continue
            if re.match(r'^//\s*COMMENT\d+\s*$', comment_text):
                continue
            if re.match(r'^#\s*COMMENT\d+\s*$', comment_text):
                continue
            if re.match(r'^///\s*COMMENT\d+\s*$', comment_text):
                continue
            if re.match(r'^--\s*COMMENT\d+\s*$', comment_text):
                continue
            if re.match(r'^<!--\s*COMMENT\d+\s*-->$', comment_text):
                continue

            # Extract just the content (without comment markers)
            # This way deobfuscate replaces COMMENT001 with just the content
            if comment_text.startswith('/*') and comment_text.endswith('*/'):
                comment_content = comment_text[2:-2].strip()
                comment_style = 'block'
            elif comment_text.startswith('<!--') and comment_text.endswith('-->'):
                comment_content = comment_text[4:-3].strip()
                comment_style = 'html'
            elif comment_text.startswith('--[[') and comment_text.endswith(']]'):
                comment_content = comment_text[4:-2].strip()
                comment_style = 'lua'
            elif comment_text.startswith('///'):
                comment_content = comment_text[3:].strip()
                comment_style = 'xmldoc'
            elif comment_text.startswith('//'):
                comment_content = comment_text[2:].strip()
                comment_style = 'line'
            elif comment_text.startswith('#'):
                comment_content = comment_text[1:].strip()
                comment_style = 'hash'
            elif comment_text.startswith('--'):
                comment_content = comment_text[2:].strip()
                comment_style = 'sql'
            else:
                comment_content = comment_text
                comment_style = 'block'

            # Skip empty comments
            if not comment_content:
                continue

            # Skip if content already mapped
            if comment_content in self.mappings.values():
                continue

            # Generate or reuse mapping for the CONTENT only
            if comment_content not in self.mappings:
                existing_nums = []
                for mapped_value in self.mappings.values():
                    if mapped_value.startswith('COMMENT') and len(mapped_value) > 7:
                        try:
                            num_part = mapped_value[7:]
                            if num_part.isdigit():
                                existing_nums.append(int(num_part))
                        except:
                            pass
                next_num = max(existing_nums) + 1 if existing_nums else 1
                placeholder = f"COMMENT{next_num:03d}"
                self.mappings[comment_content] = placeholder

            placeholder = self.mappings[comment_content]

            # Determine comment style for placeholder
            if comment_style == 'block':
                replacement = f"/* {placeholder} */"
            elif comment_style == 'html':
                replacement = f"<!-- {placeholder} -->"
            elif comment_style == 'lua':
                replacement = f"--[[ {placeholder} ]]"
            elif comment_style == 'xmldoc':
                replacement = f"/// {placeholder}"
            elif comment_style == 'line':
                replacement = f"// {placeholder}"
            elif comment_style == 'hash':
                replacement = f"# {placeholder}"
            elif comment_style == 'sql':
                replacement = f"-- {placeholder}"
            else:
                replacement = f"/* {placeholder} */"

            text_content = text_content[:start] + replacement + text_content[end:]

        self.save_mappings()
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(1.0, text_content)
        self.text_area.yview_moveto(scroll_position[0])
        self.highlight_obfuscated_text()

    def _action_remove_empty_lines(self):
        """Action: Remove excessive empty lines and whitespace-only lines"""
        import re

        # Save current scroll position
        scroll_position = self.text_area.yview()

        # Get current text content
        text_content = self.text_area.get(1.0, "end-1c")

        # Remove lines that are only whitespace
        lines = text_content.split('\n')
        cleaned_lines = []
        for line in lines:
            stripped = line.rstrip()
            if stripped:
                cleaned_lines.append(stripped)
            elif cleaned_lines and cleaned_lines[-1]:
                # Preserve single blank line between code blocks
                cleaned_lines.append('')

        text_content = '\n'.join(cleaned_lines)

        # Remove excessive blank lines (more than 1 consecutive)
        text_content = re.sub(r'\n\s*\n\s*\n+', '\n\n', text_content)

        # Remove trailing empty lines
        text_content = text_content.rstrip('\n')

        # Update text area
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(1.0, text_content)

        # Restore scroll position
        self.text_area.yview_moveto(scroll_position[0])

        # Re-highlight obfuscated text if any
        self.highlight_obfuscated_text()

    def _action_obfuscate_strings(self):
        """Action: Obfuscate string contents"""
        import re

        # Save current scroll position
        scroll_position = self.text_area.yview()

        # Get current text content
        text_content = self.text_area.get(1.0, "end-1c")

        # Find all comment regions to exclude from obfuscation
        comment_ranges = []
        for match in re.finditer(r'/\*.*?\*/', text_content, re.DOTALL):
            comment_ranges.append((match.start(), match.end()))
        for match in re.finditer(r'//[^\n]*', text_content):
            comment_ranges.append((match.start(), match.end()))
        for match in re.finditer(r'#[^\n]*', text_content):
            comment_ranges.append((match.start(), match.end()))

        def is_in_comment(pos):
            return any(start <= pos < end for start, end in comment_ranges)

        def has_interpolation(content):
            return '{' in content and '}' in content

        # Find strings (double and single quotes)
        double_quote_pattern = r'"(?:[^"\\\n\r]|\\[^\n\r])*"'
        single_quote_pattern = r"'(?:[^'\\\n\r]|\\[^\n\r])*'"

        strings_to_replace = []

        for match in re.finditer(double_quote_pattern, text_content):
            if is_in_comment(match.start()):
                continue
            full_string = match.group(0)
            string_content = full_string[1:-1]
            if (string_content and
                not any(string_content == obf for obf in self.mappings.values()) and
                not has_interpolation(string_content)):
                strings_to_replace.append((match.start(), match.end(), full_string, string_content, '"'))

        for match in re.finditer(single_quote_pattern, text_content):
            if is_in_comment(match.start()):
                continue
            full_string = match.group(0)
            string_content = full_string[1:-1]
            if (string_content and
                not any(string_content == obf for obf in self.mappings.values()) and
                not has_interpolation(string_content)):
                strings_to_replace.append((match.start(), match.end(), full_string, string_content, "'"))

        if not strings_to_replace:
            return

        # Sort by position (reverse to avoid position shifts)
        strings_to_replace.sort(key=lambda x: x[0], reverse=True)

        for start, end, full_string, string_content, quote_char in strings_to_replace:
            if string_content not in self.mappings:
                identifier = self.generate_ai_identifier(string_content)
                self.mappings[string_content] = identifier
            else:
                identifier = self.mappings[string_content]
            new_string = f"{quote_char}{identifier}{quote_char}"
            text_content = text_content[:start] + new_string + text_content[end:]

        self.save_mappings()
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(1.0, text_content)
        self.text_area.yview_moveto(scroll_position[0])
        self.highlight_obfuscated_text()

    def _action_obfuscate_guids(self):
        """Action: Obfuscate GUIDs/UUIDs with placeholders"""
        import re

        # Save current scroll position
        scroll_position = self.text_area.yview()

        # Get current text content
        text_content = self.text_area.get(1.0, "end-1c")

        # GUID patterns:
        # Standard: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
        # With braces: {xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx}
        # Without dashes: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx (32 hex chars)
        guid_pattern = r'\{?[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\}?'

        guids_found = list(re.finditer(guid_pattern, text_content))

        if not guids_found:
            return

        # Process in reverse order to avoid position shifts
        for match in reversed(guids_found):
            guid = match.group(0)

            # Skip if already obfuscated (is a placeholder)
            if guid in self.mappings.values():
                continue

            # Generate or reuse mapping
            if guid not in self.mappings:
                # Generate GUID placeholder like GUID001, GUID002
                existing_nums = []
                for mapped_value in self.mappings.values():
                    if mapped_value.startswith('GUID') and len(mapped_value) > 4:
                        try:
                            num_part = mapped_value[4:]
                            if num_part.isdigit():
                                existing_nums.append(int(num_part))
                        except:
                            pass
                next_num = max(existing_nums) + 1 if existing_nums else 1
                placeholder = f"GUID{next_num:03d}"
                self.mappings[guid] = placeholder

            placeholder = self.mappings[guid]
            text_content = text_content[:match.start()] + placeholder + text_content[match.end():]

        self.save_mappings()
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(1.0, text_content)
        self.text_area.yview_moveto(scroll_position[0])
        self.highlight_obfuscated_text()

    def _action_obfuscate_paths(self):
        """Action: Obfuscate file paths, URLs, and API routes"""
        import re

        # Save current scroll position
        scroll_position = self.text_area.yview()

        # Get current text content
        text_content = self.text_area.get(1.0, "end-1c")

        # Get next PATH number
        existing_nums = []
        for mapped_value in self.mappings.values():
            if mapped_value.startswith('PATH') and len(mapped_value) > 4:
                try:
                    num_part = mapped_value[4:]
                    if num_part.isdigit():
                        existing_nums.append(int(num_part))
                except:
                    pass
        path_counter = max(existing_nums) + 1 if existing_nums else 1

        paths_to_replace = []

        # Pattern for various path formats:
        # 1. Windows paths: C:\Users\..., \\server\share, ..\folder
        # 2. Unix paths: /usr/local/..., ./folder, ../folder
        # 3. URLs: http://, https://, ftp://, file://
        # 4. API routes: /api/v1/users, /users/{id}
        # 5. Relative paths: folder/subfolder, ./src/components

        # URLs (http, https, ftp, file, ws, wss)
        url_pattern = r'(?:https?|ftp|file|wss?)://[^\s\'"<>)}\]]+'

        # Windows absolute paths (C:\, D:\, etc.) - in strings
        windows_abs_pattern = r'[A-Za-z]:\\(?:[^\\/:*?"<>|\s\'"]|\\)+'

        # UNC paths (\\server\share)
        unc_pattern = r'\\\\[^\s\'"<>]+'

        # Unix absolute paths (/usr, /home, /var, etc.)
        unix_abs_pattern = r'(?<=["\'])\/(?:[a-zA-Z0-9_\-./]+)+(?=["\'])'

        # API routes and relative paths starting with /
        api_route_pattern = r'(?<=["\'])/[a-zA-Z0-9_\-{}./:\[\]@]+(?=["\'])'

        # Relative paths with ./ or ../
        relative_pattern = r'\.\.?/[a-zA-Z0-9_\-./]+'

        # Generic path-like patterns (folder/file.ext)
        generic_path_pattern = r'(?<=["\'])[a-zA-Z0-9_\-]+(?:/[a-zA-Z0-9_\-./]+)+(?=["\'])'

        # Find URLs
        for match in re.finditer(url_pattern, text_content):
            path = match.group(0)
            if path and not path.startswith('PATH') and path not in self.mappings.values():
                paths_to_replace.append((match.start(), match.end(), path))

        # Find Windows paths
        for match in re.finditer(windows_abs_pattern, text_content):
            path = match.group(0)
            if path and not path.startswith('PATH') and path not in self.mappings.values():
                paths_to_replace.append((match.start(), match.end(), path))

        # Find UNC paths
        for match in re.finditer(unc_pattern, text_content):
            path = match.group(0)
            if path and not path.startswith('PATH') and path not in self.mappings.values():
                paths_to_replace.append((match.start(), match.end(), path))

        # Find Unix paths (lookbehind for quote)
        for match in re.finditer(unix_abs_pattern, text_content):
            path = match.group(0)
            if path and len(path) > 1 and not path.startswith('PATH') and path not in self.mappings.values():
                paths_to_replace.append((match.start(), match.end(), path))

        # Find API routes
        for match in re.finditer(api_route_pattern, text_content):
            path = match.group(0)
            if path and len(path) > 1 and not path.startswith('PATH') and path not in self.mappings.values():
                paths_to_replace.append((match.start(), match.end(), path))

        # Find relative paths
        for match in re.finditer(relative_pattern, text_content):
            path = match.group(0)
            if path and not path.startswith('PATH') and path not in self.mappings.values():
                paths_to_replace.append((match.start(), match.end(), path))

        # Find generic paths
        for match in re.finditer(generic_path_pattern, text_content):
            path = match.group(0)
            if path and len(path) > 3 and not path.startswith('PATH') and path not in self.mappings.values():
                # Skip if looks like a version number or simple ratio
                if not re.match(r'^[0-9.]+$', path):
                    paths_to_replace.append((match.start(), match.end(), path))

        if not paths_to_replace:
            return

        # Remove duplicates and sort by position (reverse)
        seen = set()
        unique_paths = []
        for item in paths_to_replace:
            key = (item[0], item[1])
            if key not in seen:
                seen.add(key)
                unique_paths.append(item)

        unique_paths.sort(key=lambda x: x[0], reverse=True)

        # Replace paths with placeholders
        for start, end, path in unique_paths:
            # Skip if already obfuscated
            if path in self.mappings.values():
                continue

            # Generate or reuse mapping
            if path not in self.mappings:
                placeholder = f"PATH{path_counter:03d}"
                self.mappings[path] = placeholder
                path_counter += 1
            else:
                placeholder = self.mappings[path]

            text_content = text_content[:start] + placeholder + text_content[end:]

        self.save_mappings()
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(1.0, text_content)
        self.text_area.yview_moveto(scroll_position[0])
        self.highlight_obfuscated_text()

    def _action_remove_function_bodies(self):
        """Action: Remove function/method bodies, keep only signatures (C#, JS, TS)"""
        import re

        # Save current scroll position
        scroll_position = self.text_area.yview()

        # Get current text content
        text_content = self.text_area.get(1.0, "end-1c")

        # Get next available BODY number
        existing_nums = []
        for mapped_value in self.mappings.values():
            if mapped_value.startswith('BODY') and len(mapped_value) > 4:
                try:
                    num_part = mapped_value[4:]
                    if num_part.isdigit():
                        existing_nums.append(int(num_part))
                except:
                    pass
        body_counter = max(existing_nums) + 1 if existing_nums else 1

        def find_matching_brace(text, start_pos):
            """Find the closing brace position"""
            if start_pos >= len(text) or text[start_pos] != '{':
                return -1

            depth = 1
            i = start_pos + 1

            while i < len(text) and depth > 0:
                char = text[i]
                if char == '{':
                    depth += 1
                elif char == '}':
                    depth -= 1
                elif char == '"' or char == "'" or char == '`':
                    # Skip string content
                    quote = char
                    i += 1
                    while i < len(text):
                        if text[i] == '\\' and i + 1 < len(text):
                            i += 2
                            continue
                        if text[i] == quote:
                            break
                        i += 1
                i += 1

            return i - 1 if depth == 0 else -1

        # Find all opening braces and check if they follow a function signature pattern
        # Work character by character to find ")" followed by optional whitespace/type annotation then "{"

        result = text_content
        offset = 0  # Track position shifts due to replacements

        # Find all potential function signatures: pattern is )...{ where ... is whitespace or return type hints
        i = 0
        while i < len(result):
            # Find next opening brace
            brace_pos = result.find('{', i)
            if brace_pos == -1:
                break

            # Look backwards from brace to find if there's a ) before it (function signature)
            # Check up to 200 chars back for the closing paren of signature
            search_start = max(0, brace_pos - 200)
            segment = result[search_start:brace_pos]

            # Find the last ) in this segment
            paren_pos = segment.rfind(')')

            if paren_pos != -1:
                # Check what's between ) and { - should be whitespace, type annotations, or keywords
                between = segment[paren_pos + 1:]
                # Allow: whitespace, :, type names, async, =>, where clauses
                between_stripped = between.strip()

                # Valid patterns between ) and {:
                # - empty or whitespace only
                # - : ReturnType (TypeScript)
                # - where T : constraint (C#)
                # - => (but not arrow function expression - those start with = before ()
                is_valid_function = False

                if not between_stripped:
                    is_valid_function = True
                elif re.match(r'^:\s*[\w<>\[\],\s\?|&]+$', between_stripped):
                    # TypeScript return type
                    is_valid_function = True
                elif re.match(r'^where\s+', between_stripped):
                    # C# generic constraint
                    is_valid_function = True

                if is_valid_function:
                    # Now find the start of the signature (go back to find the line start or previous statement)
                    # Find the start of this line
                    line_start = result.rfind('\n', 0, search_start + paren_pos)
                    if line_start == -1:
                        line_start = 0
                    else:
                        line_start += 1

                    # Get the full signature
                    signature = result[line_start:brace_pos].rstrip()

                    # Skip if this looks like a control structure (if, while, for, etc.)
                    sig_stripped = signature.strip()
                    control_keywords = ['if', 'else', 'while', 'for', 'foreach', 'switch', 'catch', 'finally', 'lock', 'using', 'try']
                    is_control = False
                    for kw in control_keywords:
                        if sig_stripped == kw or sig_stripped.startswith(kw + ' ') or sig_stripped.startswith(kw + '('):
                            is_control = True
                            break

                    # Also skip class/interface/struct/namespace/enum declarations
                    declaration_keywords = ['class', 'interface', 'struct', 'namespace', 'enum', 'record']
                    for kw in declaration_keywords:
                        if kw + ' ' in sig_stripped or sig_stripped.endswith(kw):
                            is_control = True
                            break

                    if not is_control:
                        # Find matching closing brace
                        close_pos = find_matching_brace(result, brace_pos)

                        if close_pos != -1 and close_pos > brace_pos + 1:
                            # Extract body content
                            body_content = result[brace_pos + 1:close_pos].strip()

                            # Skip if empty or already a placeholder
                            if body_content and not re.match(r'^BODY\d+$', body_content):
                                # Generate placeholder
                                if body_content not in self.mappings:
                                    placeholder = f"BODY{body_counter:03d}"
                                    self.mappings[body_content] = placeholder
                                    body_counter += 1
                                else:
                                    placeholder = self.mappings[body_content]

                                # Replace body with placeholder
                                new_block = f"{{ {placeholder} }}"
                                result = result[:brace_pos] + new_block + result[close_pos + 1:]

                                # Continue from after the replacement
                                i = brace_pos + len(new_block)
                                continue

            i = brace_pos + 1

        self.save_mappings()
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(1.0, result)
        self.text_area.yview_moveto(scroll_position[0])
        self.highlight_obfuscated_text()

    def remove_all_comments(self):
        """Remove all comments from code (supports multiple languages)"""
        import re

        # Save state before making changes
        self.save_state()

        # Save current scroll position
        scroll_position = self.text_area.yview()

        # Get current text content
        text_content = self.text_area.get(1.0, "end-1c")

        # Remove multi-line comments (/* ... */)
        # Used in: C, C++, C#, Java, JavaScript, Go, Rust, etc.
        text_content = re.sub(r'/\*.*?\*/', '', text_content, flags=re.DOTALL)

        # Remove single-line comments starting with //
        # Used in: C, C++, C#, Java, JavaScript, Go, Rust, Swift, Kotlin, etc.
        text_content = re.sub(r'//[^\n]*', '', text_content)

        # Remove single-line comments starting with #
        # Used in: Python, Ruby, Perl, Shell scripts, etc.
        text_content = re.sub(r'#[^\n]*', '', text_content)

        # Remove XML/HTML comments (<!-- ... -->)
        text_content = re.sub(r'<!--.*?-->', '', text_content, flags=re.DOTALL)

        # Remove SQL comments (-- ...)
        text_content = re.sub(r'--[^\n]*', '', text_content)

        # Remove Lua comments (-- ... and --[[ ... ]])
        text_content = re.sub(r'--\[\[.*?\]\]', '', text_content, flags=re.DOTALL)

        # Remove Visual Basic comments (' ...)
        text_content = re.sub(r"'[^\n]*", '', text_content)

        # Remove triple-slash XML documentation comments (/// ...)
        # Already handled by // pattern above

        # Remove lines that become empty after comment removal
        lines = text_content.split('\n')
        cleaned_lines = []
        for line in lines:
            stripped = line.rstrip()
            # Keep the line if it has content or is an intentional blank line
            if stripped or (not stripped and line == '\n'):
                cleaned_lines.append(line)
            elif not stripped and cleaned_lines and cleaned_lines[-1].strip():
                # Preserve single blank lines between code blocks
                cleaned_lines.append('')

        text_content = '\n'.join(cleaned_lines)

        # Remove excessive blank lines (more than 2 consecutive)
        text_content = re.sub(r'\n\s*\n\s*\n+', '\n\n', text_content)

        # Update text area
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(1.0, text_content)

        # Restore scroll position
        self.text_area.yview_moveto(scroll_position[0])

        # Re-highlight obfuscated text if any
        self.highlight_obfuscated_text()

    def deobfuscate_word(self, obfuscated_word):
        """Deobfuscate the clicked obfuscated word back to original"""
        # Find the original word for this obfuscated identifier
        original_word = None
        for original, obfuscated in self.mappings.items():
            if obfuscated == obfuscated_word:
                original_word = original
                break

        if original_word:
            # Save state before making changes
            self.save_state()

            # Save current scroll position
            scroll_position = self.text_area.yview()

            # Replace obfuscated text back to original
            text_content = self.text_area.get(1.0, "end-1c")
            count = text_content.count(obfuscated_word)
            text_content = text_content.replace(obfuscated_word, original_word)

            self.text_area.delete(1.0, tk.END)
            self.text_area.insert(1.0, text_content)

            # Restore scroll position
            self.text_area.yview_moveto(scroll_position[0])

            # Remove from mappings
            del self.mappings[original_word]
            self.save_mappings()

            # Re-highlight remaining obfuscated text
            self.highlight_obfuscated_text()

    def deobfuscate_and_show(self):
        """Deobfuscate text and show in UI (also copy to clipboard)"""
        # Save state before making changes
        self.save_state()

        # Save current scroll position
        scroll_position = self.text_area.yview()

        # Get current text content
        text_content = self.text_area.get(1.0, "end-1c")

        # Reverse all mappings to restore original text
        deobfuscated_text = text_content
        for original, obfuscated in self.mappings.items():
            deobfuscated_text = deobfuscated_text.replace(obfuscated, original)

        # Copy to clipboard
        if deobfuscated_text:
            pyperclip.copy(deobfuscated_text)

        # Display deobfuscated text in UI
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(1.0, deobfuscated_text)

        # Restore scroll position
        self.text_area.yview_moveto(scroll_position[0])

        # Clear highlights since text is now deobfuscated
        self.text_area.tag_remove("obfuscated", "1.0", tk.END)

        # Reset obfuscation level
        self.reset_obfuscation_level()

        # Update clear button
        self.update_clear_button_text()

    def copy_all_text(self):
        """Copy all text to clipboard"""
        text_content = self.text_area.get(1.0, "end-1c")
        if text_content:
            pyperclip.copy(text_content)

    def copy_and_close(self):
        """Copy the obfuscated text to clipboard and close the application"""
        text_content = self.text_area.get(1.0, tk.END).strip()
        if text_content:
            pyperclip.copy(text_content)
        self.root.destroy()

    def clear_mappings_2state(self):
        """3-state button: CLEAR -> CONFIRM -> CLOSE"""
        if self.clear_button_state == 0:
            # First click - show confirm
            self.clear_button_state = 1
            self.update_clear_button_text("CONFIRM?")
            # Reset after 3 seconds if not clicked again
            self.root.after(3000, self.reset_clear_button)
        elif self.clear_button_state == 1:
            # Second click - execute clear
            self.clear_mappings()
            self.clear_button_state = 2
            self.update_clear_button_text("CLOSE")
            # Reset after 3 seconds if not clicked again
            self.root.after(3000, self.reset_clear_button)
        else:
            # Third click - close app
            self.root.destroy()

    def update_clear_button_text(self, text=None):
        """Update the clear button text"""
        # Find the actual button widget inside the shadow frame
        for widget in self.clear_button.winfo_children():
            if isinstance(widget, tk.Button):
                if text is None:
                    # Default: show count
                    widget.config(text=f"CLEAR ({len(self.mappings)})", bg=self.secondary_color)
                elif text == "CONFIRM?":
                    widget.config(text=text, bg="#FF0000")
                elif text == "CLOSE":
                    widget.config(text=text, bg="#FF6600")
                else:
                    widget.config(text=text, bg=self.secondary_color)
                break

    def reset_clear_button(self):
        """Reset clear button to initial state"""
        self.clear_button_state = 0
        self.update_clear_button_text()

    def clear_mappings(self):
        """Clear all mappings and restore original text"""
        # Save state before making changes
        self.save_state()

        # Save current scroll position
        scroll_position = self.text_area.yview()

        # Get current text content
        text_content = self.text_area.get(1.0, "end-1c")

        # Reverse all mappings to restore original text
        for original, obfuscated in self.mappings.items():
            text_content = text_content.replace(obfuscated, original)

        # Clear mappings
        self.mappings = {}
        self.save_mappings()

        # Update text area with deobfuscated text
        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(1.0, text_content)

        # Restore scroll position
        self.text_area.yview_moveto(scroll_position[0])

        # Clear highlights
        self.text_area.tag_remove("obfuscated", "1.0", tk.END)

        # Reset obfuscation level
        self.reset_obfuscation_level()

    def show_mappings(self):
        """Show all current mappings in a new window"""
        mappings_window = tk.Toplevel(self.root)
        mappings_window.title("MAPPINGS")
        mappings_window.geometry("700x500")
        mappings_window.configure(bg=self.bg_color)

        # Title
        title_frame = tk.Frame(mappings_window, bg=self.bg_color, padx=24, pady=24)
        title_frame.pack(fill=tk.X)

        title_label = tk.Label(
            title_frame,
            text="OBFUSCATION MAPPINGS",
            font=("Consolas", 14, "bold"),
            bg=self.bg_color,
            fg=self.text_color
        )
        title_label.pack()

        # Text area with border and shadow
        text_shadow_frame = tk.Frame(mappings_window, bg=self.border_color)
        text_shadow_frame.pack(fill=tk.BOTH, expand=True, padx=24, pady=(0, 24))

        text_border_frame = tk.Frame(
            text_shadow_frame,
            bg="#FFFFFF",
            highlightbackground=self.border_color,
            highlightthickness=6
        )
        text_border_frame.pack(fill=tk.BOTH, expand=True, padx=(0, 8), pady=(0, 8))

        # Scrollbar
        scrollbar = tk.Scrollbar(text_border_frame, width=20, bg=self.accent_color)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Create text widget
        mappings_text = tk.Text(
            text_border_frame,
            wrap=tk.NONE,
            yscrollcommand=scrollbar.set,
            font=("Consolas", 11),
            bg="#FFFFFF",
            fg=self.text_color,
            borderwidth=0,
            highlightthickness=0,
            padx=16,
            pady=16
        )
        mappings_text.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=mappings_text.yview)

        # Populate with mappings
        if self.mappings:
            mappings_text.insert("1.0", "ORIGINAL → OBFUSCATED\n")
            mappings_text.insert("end", "=" * 60 + "\n\n")
            for original, obfuscated in sorted(self.mappings.items()):
                mappings_text.insert("end", f"{original} → {obfuscated}\n")
        else:
            mappings_text.insert("1.0", "NO MAPPINGS YET\n\nSelect words in the main window to create mappings.")

        mappings_text.config(state=tk.DISABLED)

def main():
    root = tk.Tk()
    app = CodeBlur(root)
    root.mainloop()

if __name__ == "__main__":
    main()
