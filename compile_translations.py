"""
Script to compile .po files to .mo files for gettext.
Run this after editing .po translation files.

Uses Python's built-in Tools/i18n/msgfmt implementation for reliable
MO file generation with proper UTF-8 support.
"""
import os
import ast
import struct
import array


def parse_po_file(po_path):
    """Parse a .po file and return a dict of msgid -> msgstr."""
    messages = {}
    current_msgid = []
    current_msgstr = []
    in_msgid = False
    in_msgstr = False

    def _save():
        if current_msgid is not None and current_msgstr is not None:
            msgid = ''.join(current_msgid)
            msgstr = ''.join(current_msgstr)
            if msgid or msgstr:
                messages[msgid] = msgstr

    with open(po_path, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()

            # Skip comments
            if line.startswith('#'):
                continue

            # Blank line => save current entry
            if not line:
                _save()
                current_msgid = []
                current_msgstr = []
                in_msgid = False
                in_msgstr = False
                continue

            if line.startswith('msgid '):
                _save()
                in_msgid = True
                in_msgstr = False
                current_msgid = [ast.literal_eval(line[6:])]
                current_msgstr = []
            elif line.startswith('msgstr '):
                in_msgid = False
                in_msgstr = True
                current_msgstr = [ast.literal_eval(line[7:])]
            elif line.startswith('"'):
                text = ast.literal_eval(line)
                if in_msgid:
                    current_msgid.append(text)
                elif in_msgstr:
                    current_msgstr.append(text)

        _save()

    return messages


def generate_mo(messages):
    """Generate .mo file binary content from messages dict.

    Follows the GNU gettext MO file format specification.
    """
    # Sort keys; the empty string (header) sorts first
    keys = sorted(messages.keys())

    offsets = []
    ids = strs = b''
    for key in keys:
        # Encode strings to UTF-8 bytes
        key_bytes = key.encode('utf-8')
        val_bytes = messages[key].encode('utf-8')
        offsets.append((len(ids), len(key_bytes), len(strs), len(val_bytes)))
        ids += key_bytes + b'\x00'
        strs += val_bytes + b'\x00'

    # The header is 7 32-bit unsigned integers
    num_strings = len(keys)
    # Offsets for the table of original strings
    keys_start = 7 * 4 + num_strings * 2 * 8  # 2 tables of (length, offset) pairs
    # Offsets for the table of translated strings
    values_start = keys_start + len(ids)

    # Build the key/value offset tables
    key_offsets = []
    value_offsets = []
    for o in offsets:
        key_offsets += [o[1], o[0] + keys_start]
        value_offsets += [o[3], o[2] + values_start]

    output = struct.pack(
        'Iiiiiii',
        0x950412de,        # Magic number (LE)
        0,                 # Version
        num_strings,       # Number of strings
        7 * 4,             # Offset of originals table
        7 * 4 + num_strings * 8,  # Offset of translations table
        0,                 # Hash table size
        0,                 # Hash table offset
    )
    output += array.array('i', key_offsets).tobytes()
    output += array.array('i', value_offsets).tobytes()
    output += ids
    output += strs

    return output


def compile_po_to_mo(po_path, mo_path):
    """Compile a .po file to .mo format."""
    messages = parse_po_file(po_path)
    mo_data = generate_mo(messages)

    os.makedirs(os.path.dirname(mo_path), exist_ok=True)
    with open(mo_path, 'wb') as f:
        f.write(mo_data)

    print(f"Compiled: {po_path} -> {mo_path} ({len(messages)} strings)")


def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    locales_dir = os.path.join(base_dir, 'locales')
    
    for lang in os.listdir(locales_dir):
        po_path = os.path.join(locales_dir, lang, 'LC_MESSAGES', 'messages.po')
        mo_path = os.path.join(locales_dir, lang, 'LC_MESSAGES', 'messages.mo')
        if os.path.exists(po_path):
            compile_po_to_mo(po_path, mo_path)
            print(f"Compiled {lang} translations")


if __name__ == '__main__':
    main()
