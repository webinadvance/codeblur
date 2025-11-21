import tkinter as tk
from tkinter import ttk, messagebox
import pyperclip
import json
import os
import random
import string

class CodeBlur:
    def __init__(self, root):
        self.root = root
        self.root.title("CODEBLUR")
        self.root.geometry("900x700")

        # Neubrutalist monochrome with blue accent color scheme
        self.bg_color = "#FFFFFF"
        self.primary_color = "#000000"  # Pure black
        self.secondary_color = "#E0E0E0"  # Light gray
        self.accent_color = "#0066FF"  # Bright blue accent
        self.text_color = "#000000"
        self.border_color = "#000000"
        self.hover_color = "#CCCCCC"

        self.root.configure(bg=self.bg_color)

        # Storage file for mappings
        self.mappings_file = "obfuscation_mappings.json"
        self.mappings = self.load_mappings()

        # State tracking for 2-state button
        self.clear_button_armed = False
        self.clear_button = None

        # Undo history - stores (text_content, mappings) tuples
        self.undo_stack = []
        self.max_undo_levels = 20

        # Create UI
        self.create_widgets()

        # Load clipboard on startup
        self.load_clipboard()

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

    def create_neubrutalist_button(self, parent, text, command, bg_color, size="normal"):
        """Create a Neubrutalist style button with thick border and solid shadow"""
        # Container frame for shadow effect
        shadow_frame = tk.Frame(parent, bg=self.border_color, highlightthickness=0)

        # Determine text color based on background
        text_color = self.bg_color if bg_color in [self.primary_color, self.accent_color] else self.text_color

        # Size settings
        if size == "large":
            font_size = 12
            padx = 24
            pady = 16
        else:  # small
            font_size = 9
            padx = 12
            pady = 8

        # Button with thick border
        btn = tk.Button(
            shadow_frame,
            text=text,
            command=command,
            font=("Consolas", font_size, "bold"),
            bg=bg_color,
            fg=text_color,
            activebackground=bg_color,
            activeforeground=text_color,
            relief=tk.FLAT,
            borderwidth=5,
            highlightbackground=self.border_color,
            highlightthickness=5,
            cursor="hand2",
            padx=padx,
            pady=pady
        )
        btn.pack(padx=(0, 5), pady=(0, 5))

        return shadow_frame

    def create_widgets(self):
        """Create the UI components"""
        # Top frame with buttons
        top_frame = tk.Frame(self.root, bg=self.bg_color)
        top_frame.pack(fill=tk.X, padx=8, pady=8)

        # Neubrutalist buttons with monochrome colors and blue accent
        btn2 = self.create_neubrutalist_button(top_frame, "COPY AND CLOSE", self.copy_and_close, self.accent_color, size="large")
        btn2.pack(side=tk.LEFT, padx=(0, 8))

        btn3 = self.create_neubrutalist_button(top_frame, "AUTO-OBFUSCATE STRINGS", self.auto_obfuscate_strings, self.accent_color, size="small")
        btn3.pack(side=tk.LEFT, padx=(0, 8))

        btn4 = self.create_neubrutalist_button(top_frame, "REMOVE COMMENTS", self.remove_all_comments, self.accent_color, size="small")
        btn4.pack(side=tk.LEFT, padx=(0, 8))

        btn5 = self.create_neubrutalist_button(top_frame, "DEOBFUSCATE", self.copy_deobfuscated, "#00CC00", size="small")
        btn5.pack(side=tk.LEFT, padx=(0, 8))

        self.clear_button = self.create_neubrutalist_button(top_frame, "CLEAR", self.clear_mappings_2state, self.secondary_color, size="small")
        self.clear_button.pack(side=tk.LEFT, padx=(0, 8))

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
        except Exception as e:
            pass

    def apply_existing_mappings(self):
        """Apply existing mappings to the loaded text"""
        text_content = self.text_area.get(1.0, "end-1c")

        for original, obfuscated in self.mappings.items():
            text_content = text_content.replace(original, obfuscated)

        self.text_area.delete(1.0, tk.END)
        self.text_area.insert(1.0, text_content)
        self.highlight_obfuscated_text()

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

    def copy_deobfuscated(self):
        """Copy deobfuscated text (all mappings reversed) to clipboard and show in UI"""
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

    def copy_and_close(self):
        """Copy the obfuscated text to clipboard and close the application"""
        text_content = self.text_area.get(1.0, tk.END).strip()
        if text_content:
            pyperclip.copy(text_content)
        self.root.destroy()

    def clear_mappings_2state(self):
        """2-state button: first click arms, second click executes"""
        if not self.clear_button_armed:
            # First click - arm the button
            self.clear_button_armed = True
            # Change button appearance to show armed state
            self.update_clear_button_text("CONFIRM CLEAR?")
            # Reset after 3 seconds if not clicked again
            self.root.after(3000, self.reset_clear_button)
        else:
            # Second click - execute clear
            self.clear_mappings()
            self.reset_clear_button()

    def update_clear_button_text(self, text):
        """Update the clear button text"""
        # Find the actual button widget inside the shadow frame
        for widget in self.clear_button.winfo_children():
            if isinstance(widget, tk.Button):
                widget.config(text=text, bg="#FF0000" if "CONFIRM" in text else self.secondary_color)
                break

    def reset_clear_button(self):
        """Reset clear button to initial state"""
        self.clear_button_armed = False
        self.update_clear_button_text("CLEAR")

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
