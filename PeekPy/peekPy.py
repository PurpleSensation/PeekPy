import math, os, ast, shutil
from typing import List, Tuple
from .log import Log
global log
log :Log = Log()
def set_log(l):
    global log
    log = l

class ConsoleStream:
    def __init__(self, logger: Log, index: dict):
        """
        Initializes the ConsoleStream with a logger and an index of objects to print.
        :param logger: Log instance for logging the table data
        :param index: Index of objects to print (e.g. classes, methods, variables)

        
        """
        self.logger = logger
        self.index = index

    def print_object(self, name: str, print_code: bool = False, print_location=True):
        """
        Prints an object from the index with the specified name.
        :param name: The name of the object to print.
        :param print_code: Whether to print the code of the object.
        :param
        """
        matches = [key for key in self.index if key.lower() == name.lower()]
        matches = [key for key in matches if key == name] if len(matches) > 1 else matches
        if not matches:
            self.logger.log("No matches found.")
            return
        key = matches[0]
        obj = self.index[key]

        location = obj['location']
        parent = obj.get('parent', '')
        header = obj['header']

        if print_location:
            self.logger.log(f"In file '{location['file']}', line {location['line']}:", 'underline').up()

        # Get class information if available
        if obj['type'] == 'Method':
            class_key = parent
            parent = self.index[class_key]['name'] if class_key in self.index else ''
            # Incorporate 'class.' if class info is present
            if parent:
                def_index = header.find('def ')
                if def_index != -1:
                    header = header[def_index + 4:]
                    header = f"def {parent}.{header}"

        self.logger.log(header, 'italic').up()
        if obj['docstring']:
            self.logger.up().log(obj['docstring'], 'dim').down()
        else:
            self.logger.log('No description available.')

        if print_code:
            self.logger.sep().log(" Code:", 'underline')
            if obj['type'] == 'Class':
                init_code = obj.get('init_code')
                if init_code:
                    self.logger.log("Constructor (__init__) code:")
                    self.logger.log(init_code)
                else:
                    self.logger.log("No __init__ method found.")
            else:
                code_lines = obj['code'].splitlines()
                skip_lines = 1  # Header line
                if obj['docstring']:
                    docstring_lines = len(obj['docstring'].splitlines()) + 2  # Including triple quotes
                    skip_lines += docstring_lines
                code_body = '\n'.join(code_lines[skip_lines:])
                if code_body.strip():
                    self.logger.log(code_body, 'white')
                else:
                    self.logger.log('No additional code.')

        if print_location:
            self.logger.down()
        self.logger.down().sep()

    def print_block(self, block):
        node = block['node']
        node_obj = self.index[node['key']]
        if not block['references']:
            return  # Skip empty blocks

        # Get number of groups in the block
        num_groups = len(block['groups'])
        # Set logger level to zero
        self.logger.reset()
        # Connector message
        if num_groups > 1:
            self.logger.log(f"References in '{node_obj['name']}':", 'bold')
        else:
            file, cls = list(block['groups'].keys())[0]
            if cls:
                header = f"All in {file} > class {cls}"
            else:
                header = f"All in {file}"
            self.logger.log(f"References in '{node_obj['name']}' ({header}):", 'bold')

        self.logger.sep(2).up()
        for group_key, ref_nodes in block['groups'].items():
            file, cls = group_key
            if cls:
                header = f"In {file} > class {cls}:"
            else:
                header = f"In {file}:"

            if num_groups > 1:
                self.logger.log(header + ' ' * 20, 'underline').up()

            for ref_node in ref_nodes:
                indt_lvl = int(self.logger.indent_level)
                self.print_object(ref_node['key'], print_code=False, print_location=False)
                self.logger.indent_level = indt_lvl

            if num_groups > 1:
                self.logger.down()
        self.logger.down().sep()
class HTMLStream:
    def __init__(self, index):
        self.index = index
        self.output = []
        self.indent_level = 0
        self.visited_keys = set()
        self.template_start = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Code Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        h1, h2, h3, h4 { color: #333; }
        pre { background-color: #f8f8f8; padding: 10px; overflow: auto; border: 1px solid #ddd; }
        code { font-family: monospace; }
        .method-section { margin-bottom: 40px; }
        .method-header { background-color: #e8e8e8; padding: 10px; border: 1px solid #ccc; }
        .method-description { margin: 10px 0; padding: 10px; background-color: #f0f0f0; border-left: 4px solid #ccc; }
        .method-code { margin-top: 10px; }
        .method-link { color: blue; text-decoration: none; }
        a.method-link:hover { text-decoration: underline; }
        .method-header h2 { margin: 0; }
    </style>
</head>
<body>
"""
        self.template_end = """
</body>
</html>
"""

    def print_object(self, name: str, print_code: bool = False, print_location=True):
        matches = [key for key in self.index if key.lower() == name.lower()]
        matches = [key for key in matches if key == name] if len(matches) > 1 else matches
        if not matches:
            self.output.append("<p>No matches found.</p>")
            return
        key = matches[0]

        # Avoid processing the same object multiple times
        if key in self.visited_keys:
            return
        self.visited_keys.add(key)

        obj = self.index[key]
        obj_id = key.replace('.', '_')  # Use key as ID, replacing dots with underscores

        # Build HTML content
        indent = '  ' * 2
        # Start method section
        self.output.append(f'{indent}<div class="method-section" id="{obj_id}">')
        if print_location:
            location = obj['location']
            self.output.append(f'{indent}    <p><small>{location["file"]}, line {location["line"]}</small></p>')

        # Stack header and docstring
        codeblock_str = ""
        # Add header
        codeblock_str += obj['header'] + "\n"
        if obj['docstring']: codeblock_str += obj['docstring'] + "\n"
        else: codeblock_str += "No description available.\n"
        # Add code
        if print_code:
            # Get only the code body (excluding header and docstring)
            code_lines = obj['code'].splitlines()
            skip_lines = 1
            if obj['docstring']:
                docstring_lines = len(obj['docstring'].splitlines()) + 2
                skip_lines += docstring_lines
            code_body = '\n'.join(code_lines[skip_lines:])
            codeblock_str += code_body + "\n"
        
        # Append as code with links
        self.output.append(f'{indent}{self.highlight_code(codeblock_str)}')

        # End method section
        self.output.append(f'</div>')  # Close method-section

    def print_block(self, block):
        node = block['node']
        node_obj = self.index[node['key']]
        if not block['references']:
            return 

        num_groups = len(block['groups'])
        indent = '  ' * self.indent_level

        # Section header
        self.output.append(f"{indent}<h3>Referenced in '{node_obj['name']}':</h3>")

        self.indent_level += 1
        for _, ref_nodes in block['groups'].items():
            for ref_node in ref_nodes:
                self.print_object(ref_node['key'], print_code=False, print_location=False)
        self.indent_level -= 1

    def highlight_code(self, code):
        # Use Pygments for syntax highlighting
        from pygments import highlight
        from pygments.lexers import PythonLexer
        from pygments.formatters import HtmlFormatter

        formatter = HtmlFormatter(nowrap=True)
        highlighted = highlight(code, PythonLexer(), formatter)
        # No need to include style multiple times
        if not hasattr(self, 'style_included'):
            style = HtmlFormatter().get_style_defs('.highlight')
            self.output.insert(0, f'<style>{style}</style>')
            self.style_included = True
        return f'<pre class="highlight"><code>{highlighted}</code></pre>'

    def replace_methods_with_links(self, code):
        import re
        # Regex to find method calls
        pattern = re.compile(r'(\b\w+(?:\.\w+)*)\(')
        def replace_match(match):
            method_name = match.group(1)
            method_key = self.find_method_key(method_name)
            if method_key:
                method_id = method_key.replace('.', '_')
                return f'<a href="#{method_id}" class="method-link">{method_name}</a>('
            else:
                return match.group(0)
        return pattern.sub(replace_match, code)

    def find_method_key(self, method_name):
        # Attempt to find the method key in the index
        if method_name in self.index:
            return method_name
        # Try to match method names with class methods
        possible_keys = [key for key in self.index if key.endswith('.' + method_name)]
        if possible_keys:
            return possible_keys[0]
        return None

    def get_output(self):
        return self.template_start + '\n'.join(self.output) + self.template_end

    def export_to_file(self, filepath):
        html_content = self.get_output()
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)


class Logger:
    """A logging utility designed to facilitate debugging and output formatting for console applications."""
    def __init__(self):
        self.indent_level = 0
        self.max_level = 5
        self.output = []
        self.filters = {
            'remove_comments': True,         # New filter to remove comment-only lines
            'triple_quotes': True,
            'whitespaces': True,
            'remove_blank_lines': True,
            'max_line_length': 75,
            'break_after_separator': True,
            'remove_logger_calls': True,
        }
        # ANSI escape codes for formatting
        self.format_codes = {
            'reset': '\033[0m',
            'bold': '\033[1m',
            'dim': '\033[2m',
            'italic': '\033[3m',
            'underline': '\033[4m',
            'blink': '\033[5m',
            'reverse': '\033[7m',
            'hidden': '\033[8m',
            'strikethrough': '\033[9m',
            # Text colors
            'black': '\033[30m',
            'red': '\033[31m',
            'green': '\033[32m',
            'yellow': '\033[33m',
            'blue': '\033[34m',
            'magenta': '\033[35m',
            'cyan': '\033[36m',
            'white': '\033[37m',
            # Background colors
            'bg_black': '\033[40m',
            'bg_red': '\033[41m',
            'bg_green': '\033[42m',
            'bg_yellow': '\033[43m',
            'bg_blue': '\033[44m',
            'bg_magenta': '\033[45m',
            'bg_cyan': '\033[46m',
            'bg_white': '\033[47m',
            # Bright text colors
            'bright_black': '\033[90m',
            'bright_red': '\033[91m',
            'bright_green': '\033[92m',
            'bright_yellow': '\033[93m',
            'bright_blue': '\033[94m',
            'bright_magenta': '\033[95m',
            'bright_cyan': '\033[96m',
            'bright_white': '\033[97m',
            # Bright background colors
            'bg_bright_black': '\033[100m',
            'bg_bright_red': '\033[101m',
            'bg_bright_green': '\033[102m',
            'bg_bright_yellow': '\033[103m',
            'bg_bright_blue': '\033[104m',
            'bg_bright_magenta': '\033[105m',
            'bg_bright_cyan': '\033[106m',
            'bg_bright_white': '\033[107m',
        }

    # ----------- Level management -----------
    def up(self, message=None):
        if message is not None:
            self.log(message)
        if self.indent_level < self.max_level:
            self.indent_level += 1
        return self
    def down(self):
        if self.indent_level > 0:
            self.indent_level -= 1
        return self
    def reset(self):
        """Sets indent level to ground level."""
        self.indent_level = 0
        return self

    # ----------- Logging methods -----------
    def log(self, message: str, format: str = None):
        """
        Logs a message with optional formatting.
        :param message: The message to log.
        :param format: Optional format specifier ('bold', 'italic', 'underline').
        """
        indented_message = str(message)
        if format in self.format_codes:
            # Apply formatting using ANSI escape codes
            indented_message = f"{self.format_codes[format]}{indented_message}{self.format_codes['reset']}"
        self.output.append(self.indent_text(indented_message))
        return self
    def sep(self, big: int = 0):
        """
        Adds a separator line to the output.
        :param big: The type of separator (2: big, 1: small, 0: blank).
        """
        if big == 2:
            sep = '=' * 60
        elif big == 1:
            sep = self.indent_text('-' * 60)[1:60 - max(self.indent_level * 2 - 1, 0)]
        elif big == 0:
            sep = '<blank>'
        self.output.append(sep)
        return self
    def indent_text(self, text: str):
        indent = '  ' * self.indent_level
        lines = text.split('\n')
        indented_lines = [
            f"{indent}{line}" if line.strip() != '' else ''
            for line in lines
        ]
        return '\n'.join(indented_lines)

    # ----------- Output management -----------
    def get_output(self):
        # Apply post-processing filters
        output = '\n'.join(self.output)
        output = self.apply_filters(output)
        # Now substitute '<blank>' with '\n'
        output = output.replace('<blank>', ' ')
        return output
    def clear(self):
        self.output = []
        self.indent_level = 0
        return self

    # ----------- Filter management -----------
    def set_filter(self, filter_name, value):
        self.filters[filter_name] = value
        return self
    def apply_filters(self, text):
        # Apply filters based on self.filters
        lines = text.split('\n')

        # Remove lines containing 'self.logger.'
        if self.filters.get('remove_logger_calls', True):
            log_keywords = ['self.logger.', 'log.', 'Log ']
            lines = [line for line in lines if not any(kw in line for kw in log_keywords)]

        # Remove lines that contain only comments
        if self.filters.get('remove_comments', True):
            import re
            comment_pattern = re.compile(r'^\s*#.*$')
            lines = [line for line in lines if not comment_pattern.match(line)]

        if self.filters.get('triple_quotes', True):
            lines = [line.replace('"""', '') for line in lines]

        if self.filters.get('whitespaces', True):
            lines = [line.rstrip() for line in lines]

        if self.filters.get('remove_blank_lines', True):
            lines = [line for line in lines if line.strip() != '']

        if self.filters.get('break_after_separator', True):
            # Find big separators and add a newline after them
            new_lines = []
            for line in lines:
                new_lines.append(line)
                if line.startswith('===='):
                    new_lines.append('\n')
            lines = new_lines

        max_length = self.filters.get('max_line_length')
        if max_length:
            # Split long lines at spaces or enforce max length
            new_lines = []
            for line in lines:
                while len(line) > max_length:
                    # Copy indentation from the beginning of the line
                    line_indent = ''
                    for char in line:
                        if char == ' ' or char == '\t':
                            line_indent += char
                        else:
                            break

                    split_index = line.rfind(' ', 0, max_length)
                    if split_index == -1:
                        split_index = max_length
                    # Split the line at the last space before the max length, and then add the rest of the line to the next line. Account for this exception: if the line contains a separator, just remove the last bits of the separator to fit the line and skip adding a new line with the removed bits.
                    is_separator = False
                    if line[split_index-5:split_index] == '=====' or line[split_index-5:split_index] == '-----':
                        is_separator = True
                    if is_separator:
                        new_lines.append(line[:split_index])
                        line = line[split_index:].lstrip()
                        line = line_indent + line
                    else:
                        new_lines.append(line[:split_index])
                        line = line[split_index:].lstrip()
                        line = line_indent + line
                        
                new_lines.append(line)
            lines = new_lines

        return '\n'.join(lines)

# ======= Code Navigation and Reporting =======
class PeekPy: # Code Indexer
    class ReferenceTree:
        def __init__(self, index, start_key, max_depth):
            self.index = index
            self.start_key = start_key
            self.max_depth = max_depth
            self.node_index_list = []
            self.visited_keys = set()
            self.root_node = self.build_tree(start_key, 0)

        def build_tree(self, key, depth):
            if depth > self.max_depth:
                return None
            if key in self.visited_keys:
                return None
            self.visited_keys.add(key)
            obj = self.index.get(key)
            if not obj:
                return None

            node = {
                'key': key,
                'depth': depth,
                'references': []
            }
            node['index'] = len(self.node_index_list)
            self.node_index_list.append(node)

            # Collect references
            for ref in obj.get('references', []):
                matched_key = self.match_reference(ref)
                if matched_key:
                    child_node = self.build_tree(matched_key, depth + 1)
                    if child_node:
                        node['references'].append(child_node)
            return node


        def collect_levels(self):
            levels = {}
            queue = [(self.root_node, self.root_node['depth'])]
            while queue:
                node, depth = queue.pop(0)
                if depth not in levels:
                    levels[depth] = []
                levels[depth].append(node)
                for child in node['references']:
                    queue.append((child, child['depth']))
            return levels

        def create_blocks(self):
            levels = self.collect_levels()
            blocks = []
            for depth in range(max(levels.keys()) + 1):
                nodes_at_depth = levels.get(depth, [])
                for node in nodes_at_depth:
                    block = {
                        'node': node,
                        'references': node['references'],
                        'index': node['index']
                    }
                    blocks.append(block)
            return blocks

        def preprocess_blocks(self, blocks):
            visited_keys = set()
            new_blocks = []
            for block in blocks:
                new_refs = []
                for ref_node in block['references']:
                    if ref_node['key'] not in visited_keys:
                        new_refs.append(ref_node)
                        visited_keys.add(ref_node['key'])
                if new_refs:
                    block['references'] = new_refs
                    new_blocks.append(block)
            return new_blocks

        def group_references(self, blocks):
            for block in blocks:
                references = block['references']
                groups = {}
                for ref_node in references:
                    key = ref_node['key']
                    ref_obj = self.index[key]
                    file = ref_obj['location']['file']
                    cls = ref_obj.get('parent', None)
                    group_key = (file, cls)
                    if group_key not in groups:
                        groups[group_key] = []
                    groups[group_key].append(ref_node)
                block['groups'] = groups

        def match_reference(self, ref):
            # Try to match the full reference first
            if ref in self.index:
                return ref
            # If not found, split the reference and try to match method names
            ref_parts = ref.split('.')
            method_name = ref_parts[-1]
            possible_keys = [key for key in self.index if key.endswith('.' + method_name) or key == method_name]
            if possible_keys:
                return possible_keys[0]  # Return the first match
            return None

    class IndexVisitor(ast.NodeVisitor):
        def __init__(self, filename, source, index):
            self.filename: str = filename
            self.source: str = source
            self.index: dict = index
            self.current_class: str = None
            self.current_level: int = 0  # Added to track nesting levels

        def get_source_segment(self, node):
            lines = self.source.splitlines()
            start = node.lineno - 1
            end = node.end_lineno if hasattr(node, 'end_lineno') else node.lineno
            return '\n'.join(lines[start:end])

        def annotation_to_str(self, node):
            if isinstance(node, ast.Name):
                return node.id
            elif isinstance(node, ast.Subscript):
                value = self.annotation_to_str(node.value)
                slice_ = self.annotation_to_str(node.slice)
                return f"{value}[{slice_}]"
            elif isinstance(node, ast.Index):
                return self.annotation_to_str(node.value)
            elif isinstance(node, ast.Tuple):
                elts = [self.annotation_to_str(elt) for elt in node.elts]
                return ', '.join(elts)
            elif isinstance(node, ast.Attribute):
                value = self.annotation_to_str(node.value)
                return f"{value}.{node.attr}"
            elif isinstance(node, ast.Constant):  # For Python 3.8 and above
                return repr(node.value)
            elif isinstance(node, ast.Str):  # For Python 3.7 and below
                return repr(node.s)
            else:
                return ''

        def visit_ClassDef0(self, node):
            class_name = node.name
            key = class_name
            bases = [self.get_base_name(base) for base in node.bases]
            header = f"class {class_name}({', '.join(bases)}):" if bases else f"class {class_name}:"
            obj = {
                'name': class_name,
                'type': 'Class',
                'location': {
                    'file': os.path.basename(self.filename),
                    'line': node.lineno
                },
                'code': self.get_source_segment(node),
                'docstring': ast.get_docstring(node),
                'references': [],
                'methods': [],
                'variables': [],
                'referenced_by': [],
                'header': header
            }
            

            self.index[key] = obj
            self.current_class = class_name
            self.generic_visit(node)
            self.current_class = None
        
        def get_base_name(self, base):
            if isinstance(base, ast.Name):
                return base.id
            elif isinstance(base, ast.Attribute):
                return f"{self.get_base_name(base.value)}.{base.attr}"
            else:
                return ''

        def visit_FunctionDef0(self, node):
            func_name = node.name
            args = [arg.arg for arg in node.args.args]
            args_str = ', '.join(args)
            if self.current_class:
                key = f"{self.current_class}.{func_name}"
                type_ = 'Method'
                parent = self.current_class
            else:
                key = func_name
                type_ = 'Function'
                parent = False
            
            header = f"def {func_name}({args_str}):"
            obj = {
                'name': func_name,
                'type': type_,
                'location': {
                    'file': os.path.basename(self.filename),
                    'line': node.lineno
                },
                'header': header,
                'code': self.get_source_segment(node),
                'docstring': ast.get_docstring(node),
                'references': [],
                'methods': [],
                'variables': [],
                'referenced_by': [],
            }
            
            
            self.index[key] = obj
            collector = self.ReferenceCollector()
            collector.visit(node)
            obj['references'] = collector.references
            obj['variables'] = collector.variables
            if self.current_class:
                self.index[self.current_class]['methods'].append(key)
            self.generic_visit(node)
        
        def visit_ClassDef(self, node):
            class_name = node.name
            key = class_name
            bases = [self.get_base_name(base) for base in node.bases]
            header = f"class {class_name}({', '.join(bases)}):" if bases else f"class {class_name}:"
            obj = {
                'name': class_name,
                'type': 'Class',
                'location': {
                    'file': os.path.basename(self.filename),
                    'line': node.lineno
                },
                'code': self.get_source_segment(node),
                'docstring': ast.get_docstring(node),
                'references': [],
                'methods': [],
                'variables': [],
                'referenced_by': [],
                'header': header,
                'level': self.current_level  # Set the level
            }
            self.index[key] = obj
            self.current_class = class_name
            self.current_level += 1  # Increment level when entering a class
            self.generic_visit(node)
            self.current_level -= 1  # Decrement level when exiting a class
            self.current_class = None

        def visit_FunctionDef(self, node):
            func_name = node.name
            args = [arg.arg for arg in node.args.args]
            args_str = ', '.join(args)
            if self.current_class:
                key = f"{self.current_class}.{func_name}"
                type_ = 'Method'
                parent = self.current_class
            else:
                key = func_name
                type_ = 'Function'
                parent = False

            header = f"def {func_name}({args_str}):"
            obj = {
                'name': func_name,
                'type': type_,
                'location': {
                    'file': os.path.basename(self.filename),
                    'line': node.lineno
                },
                'header': header,
                'code': self.get_source_segment(node),
                'docstring': ast.get_docstring(node),
                'references': [],
                'methods': [],
                'variables': [],
                'referenced_by': [],
                'level': self.current_level  # Set the level
            }

            self.index[key] = obj
            collector = self.ReferenceCollector()
            collector.visit(node)
            obj['references'] = collector.references
            obj['variables'] = collector.variables
            if self.current_class:
                self.index[self.current_class]['methods'].append(key)
            self.current_level += 1  # Increment level when entering a function
            self.generic_visit(node)
            self.current_level -= 1  # Decrement level when exiting a function
        class ReferenceCollector(ast.NodeVisitor):
            def __init__(self):
                self.references = []
                self.variables = []

            def visit_Call(self, node):
                if isinstance(node.func, ast.Name):
                    self.references.append(node.func.id)
                    
                elif isinstance(node.func, ast.Attribute):
                    attr_names = []
                    current = node.func
                    while isinstance(current, ast.Attribute):
                        attr_names.insert(0, current.attr)
                        current = current.value
                    if isinstance(current, ast.Name):
                        attr_names.insert(0, current.id)
                    full_name = '.'.join(attr_names)
                    # full_name = attr_names[-1]
                    self.references.append(full_name)
                    
                self.generic_visit(node)

            def visit_Name(self, node):
                if isinstance(node.ctx, ast.Store):
                    self.variables.append(node.id)
                self.generic_visit(node)

    # ======= Initialization =======
    def __init__(self, path, exclude=[]):
        """Initializes the CodeIndexer with the specified path.
        If the path is a file, it will index that file. If it is a folder, it will index all Python files in that folder.
        """
        self.logger = Logger()
        self.path = path
        self.exclude = exclude
        self.index = {}
        self.set_filters()
        self.build_index()

    def build_index(self):
        self.logger.up("Building Code Index")
        files = []
        name = os.path.basename(self.path)
        if os.path.isfile(self.path):            
            self.logger.log(f"Found file: {name}")
            files.append(self.path)
        else:
            self.logger.log(f"Searching for Python files in '{name}'")
            for root, _, filenames in os.walk(self.path):
                files.extend(
                    os.path.join(root, filename)
                    for filename in filenames if filename.endswith('.py'))
                for filename in filenames:
                    if filename.endswith('.py'):
                        self.logger.log(f"Found file: {filename}")
        for file in files:
            # Get file name and check if its in self.exclude list of str
            if os.path.basename(file) in self.exclude: continue
            with open(file, 'r', encoding='utf-8') as f:
                source = f.read()
            tree = ast.parse(source, filename=file)
            visitor = self.IndexVisitor(file, source, self.index)
            visitor.visit(tree)
        self.logger.log("Finished initial indexing.").down()
  
    # ======= Public Methods =======
    def peek(self, name: str, print_code: bool = False, return_output: bool = False, print_location = True):
        """Peeks at a given object in the index and displays its information."""
        if not return_output: self.logger.clear()
        
        matches = [key for key in self.index if key.lower() == name.lower()]
        matches = [key for key in matches if key == name] if len(matches) > 1 else matches
        if not matches:
            self.logger.log("No matches found.")
            return self._finalize_output(return_output)
        key = matches[0]
        obj = self.index[key]

        location = obj['location']
        parent = obj.get('parent', '')
        # Construct the header
        header = obj['header']
            
        if print_location:
            self.logger.log(f"In file '{location['file']}', line {location['line']}:{' '*30}", 'underline').up()

        # Get class information if available
        if obj['type'] == 'Method':
            class_key = parent
            parent = self.index[class_key]['name'] if class_key in self.index else ''
            # Incorporate 'class.' if class info is present
            if parent:
                def_index = header.find('def ')
                if def_index != -1:
                    header = header[def_index + 4:]
                    header = f"def {parent}.{header}"
                
        self.logger.log(header, 'italic').up()
        if obj['docstring']: self.logger.up().log(obj['docstring'],'dim').down()
        else: self.logger.log('No description available.')
        
        if print_code:
            self.logger.sep().log(" Code:" + ' '*30, 'underline')
            if obj['type'] == 'Class':
                init_code = obj.get('init_code')
                if init_code:
                    self.logger.log("Constructor (__init__) code:")
                    self.logger.log(init_code)
                else: self.logger.log("No __init__ method found.")
            else:
                code_lines = obj['code'].splitlines()
                skip_lines = 1  # Header line
                if obj['docstring']:
                    docstring_lines = len(obj['docstring'].splitlines()) + 2  # Including triple quotes
                    skip_lines += docstring_lines
                code_body = '\n'.join(code_lines[skip_lines:])
                if code_body.strip():
                    self.logger.log(code_body, 'white')
                else:
                    self.logger.log('No additional code.')
        
        if print_location: self.logger.down()
        self.logger.down().sep()
        
        return self._finalize_output(return_output)

    def search(self, keyword: str, return_output: bool = False):
        """Searches for a keyword in the index and displays the results."""
        if not return_output: self.logger.clear()

        self.logger.up().log(f"Searching for keyword '{keyword}'...")

        matches = {key: obj for key, obj in self.index.items() if keyword.lower() in key.lower()}
        matches.update({
            key: obj for key, obj in self.index.items()
            if any(keyword.lower() in var.lower() for var in obj.get('variables', []))
        })
        if not matches:
            self.logger.log("No matches found.")
            return self._finalize_output(return_output)
        match_str = ', '.join(matches.keys())
        self.logger.log(f"Found {len(matches)} match{'es' if len(matches) !=1 else ''}: {match_str}")
        for key in matches:
            _ = self.peek(key, False, True)
        self.logger.sep()

        return self._finalize_output(return_output)

    def report(self, start_keyword: str = None, max_depth: int = 2, output_format='console', return_output: bool = False, output_file=None):
        """Produces a report starting from a given keyword with a specified maximum depth."""
        if output_format == 'console':
            stream = ConsoleStream(self.logger, self.index)
            self.logger.clear().log(f"Producing report starting from '{start_keyword}':").sep(2)
        elif output_format == 'html':
            stream = HTMLStream(self.index)
        else:
            raise ValueError(f"Unsupported output format: {output_format}")

        # Find the starting object
        if start_keyword:
            matches = [key for key in self.index if key.lower() == start_keyword.lower()]
            matches = [key for key in matches if key == start_keyword] if len(matches) > 1 else matches
            if not matches:
                if output_format == 'console':
                    self.logger.log("No matches found.")
                    return self._finalize_output(return_output)
                elif output_format == 'html':
                    return ""  # or some default html output
        else:
            if output_format == 'console':
                self.logger.log("No starting keyword provided.")
                return self._finalize_output(return_output)
            elif output_format == 'html':
                return ""

        starting_key = matches[0]

        # Build the reference tree
        ref_tree = self.ReferenceTree(self.index, starting_key, max_depth)
        blocks = ref_tree.create_blocks()
        blocks = ref_tree.preprocess_blocks(blocks)
        ref_tree.group_references(blocks)

        # Print the starting object
        stream.print_object(starting_key, print_code=True, print_location=True)

        # Now, go through the blocks
        for block in blocks:
            stream.print_block(block)

        # Finalize output
        if output_format == 'console':
            return self._finalize_output(return_output)
        elif output_format == 'html':
            if output_file:
                stream.export_to_file(output_file)
            html_output = stream.get_output()
            if return_output:
                return html_output
            else:
                self.logger.up(html_output)

    # ======= Quick Reference Method =======
    def quick_reference(self, level=1, include_descriptions=False, return_output=False):
        """Prints a quick reference of all methods and classes in order of appearance."""
        if not return_output:
            self.logger.clear()
        self.logger.up().log("Quick Reference").sep()

        # Collect items to print, grouped by file
        files_dict = {}
        for key, obj in self.index.items():
            obj_level = obj.get('level', 0)
            if obj_level <= level:
                file = obj['location']['file']
                if file not in files_dict:
                    files_dict[file] = []
                files_dict[file].append((obj['location']['line'], key, obj))

        # Now, for each file, sort items by line number
        for file in sorted(files_dict.keys()):
            self.logger.log(f"File: {file}", 'underline')
            items = files_dict[file]
            # Sort items by line number
            items.sort(key=lambda x: x[0])
            for line_no, key, obj in items:
                indent = '  ' * obj.get('level', 0)
                header = obj['header']
                self.logger.log(f"{indent}{header}")
                if include_descriptions and obj.get('docstring'):
                    docstring = obj['docstring']
                    doc_lines = docstring.strip().split('\n')
                    for doc_line in doc_lines:
                        self.logger.log(f"{indent}  {doc_line.strip()}", 'dim')
        self.logger.down()
        return self._finalize_output(return_output)
    
    # ======= Getters and Setters =======
    def print_index(self, return_output: bool = False):
        """Prints the entire code outline. Simply a list of objects with their properties. No code or descriptions."""
        self.logger.clear()
        self.logger.up().log("Printing Code Index")
        self.logger.sep(big=True)
        for key, obj in self.index.items():
            # Print Key, Type, Name and number of references
            references = len(obj.get('references', []))
            self.logger.log(f"{obj['type']}{key} ({references} references)")
        return self._finalize_output(return_output)

    def get_output(self): return self.logger.get_output()
 
    # ======= Post-Processing =======
    def _finalize_output(self, return_output):
        self.logger.down()
        output = self.logger.get_output()
        if return_output:
            return output
        else:
            print(output)

    # ======= Post-Processing=======
    def _finalize_output(self, return_output):
            self.logger.down()
            output = self.logger.get_output()
            if return_output:
                return output
            else:
                print(output)

    def set_filters(self, filters = None):
        if filters is None:
            filters = self.logger.filters
            return
        for filter_name, value in filters.items():
            self.logger.set_filter(filter_name, value)
            
    # ======= Preprocessing and Utility Methods =======
    def process_line(self, line):
        """Processes a single line to fix indentation and remove unwanted characters."""
        # Define the number of spaces per indent level
        indent_size = 4

        # Remove unwanted special characters from the beginning of the line
        unwanted_chars = '\u200b\u200c\u200d\ufeff'  # Zero-width spaces and other invisible chars
        line = line.lstrip(unwanted_chars)

        # Replace tabs with spaces
        line = line.replace('\t', ' ' * indent_size)

        # Normalize indentation
        stripped_line = line.lstrip()
        leading_spaces = len(line) - len(stripped_line)
        indent_level = leading_spaces // indent_size
        extra_spaces = leading_spaces % indent_size

        # Remove extra spaces
        if extra_spaces > 0:
            leading_spaces = indent_level * indent_size
        else:
            leading_spaces = leading_spaces

        fixed_line = (' ' * leading_spaces) + stripped_line

        # Remove any unwanted special characters at the end of the line
        fixed_line = fixed_line.rstrip(unwanted_chars + ' \t\r\n') + '\n'

        return fixed_line
    
    def fix_indentation0(self):
        """Fixes the indentation of code files in the specified path."""
        self.logger.log("Fixing indentation of code files...")
        files_to_fix = []

        # Collect all .py files in the path
        if os.path.isfile(self.path):
            if self.path.endswith('.py'):
                files_to_fix.append(self.path)
            base_dir = os.path.dirname(self.path)
        else:
            base_dir = self.path
            for root, _, filenames in os.walk(self.path):
                files_to_fix.extend(
                    os.path.join(root, filename)
                    for filename in filenames if filename.endswith('.py')
                )

        # Create the backup folder
        parent_folder_name = os.path.basename(os.path.abspath(base_dir))
        backup_folder_name = f"{parent_folder_name}_old"
        backup_folder_path = os.path.join(os.path.dirname(base_dir), backup_folder_name)
        os.makedirs(backup_folder_path, exist_ok=True)
        self.logger.log(f"Backup folder created at '{backup_folder_path}'")

        for file_path in files_to_fix:
            # Determine relative path for maintaining folder structure
            rel_path = os.path.relpath(file_path, base_dir)
            backup_file_path = os.path.join(backup_folder_path, rel_path)

            # Create necessary directories in backup folder
            os.makedirs(os.path.dirname(backup_file_path), exist_ok=True)

            # Move the original file to the backup folder
            if not os.path.exists(backup_file_path):
                shutil.move(file_path, backup_file_path)
                self.logger.log(f"Moved '{file_path}' to backup folder.")
            else:
                self.logger.log(f"Backup file '{backup_file_path}' already exists. Skipping backup.")

            # Read the content from the backup file
            with open(backup_file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            # Process lines to fix indentation
            fixed_lines = []
            for line in lines:
                fixed_line = self.process_line(line)
                fixed_lines.append(fixed_line)

            # Write the fixed content back to the original file path
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(fixed_lines)
            self.logger.log(f"Fixed indentation in '{file_path}'")

        self.logger.log("Finished fixing indentation.")
    def _compute_indent_levels(self, raw_lines, indent_size=4):
        """
        Return a list with the logical indent *level* of every line.
        Blank lines get ``None`` so we can reproduce them verbatim.
        Tabs are **already** expanded when this is called.
        """
        stack = []              # holds the distinct “column numbers” we meet
        levels = []

        for line in raw_lines:
            stripped = line.lstrip()
            if not stripped:        # empty / whitespace-only
                levels.append(None)
                continue

            col = len(line) - len(stripped)

            # climb back if current indent shrank
            while stack and col < stack[-1]:
                stack.pop()

            # new deeper block → push
            if not stack or col > stack[-1]:
                stack.append(col)

            levels.append(len(stack) - 1)   # depth = stack length – root(0)

        return levels
    def _scan_indent_meta(self, lines):
        """
        Returns three parallel lists, one entry per *physical* line:

            levels[i]   – logical block depth (0 = top level)
            paren[i]    – open-bracket depth *after* the line
            col[i]      – original leading-space column

        Blank / whitespace-only lines get (None, None, None).
        """
        stack, levels, paren_depth, cols = [], [], [], []
        open_count = 0

        for ln in lines:
            stripped = ln.lstrip()
            if not stripped:
                levels.append(None); paren_depth.append(None); cols.append(None)
                continue

            col = len(ln) - len(stripped)

            # block logic only if we’re *not* already inside ( … )
            if open_count == 0:
                while stack and col < stack[-1]:
                    stack.pop()
                if not stack or col > stack[-1]:
                    stack.append(col)

            # record & update
            levels.append(len(stack) - 1)
            cols.append(col)
            paren_depth.append(open_count)

            # naive but fast bracket balance (ignores strings / comments)
            open_count += stripped.count('(') + stripped.count('[') + stripped.count('{')
            open_count -= stripped.count(')') + stripped.count(']') + stripped.count('}')

        return levels, paren_depth, cols

    # ─────────────────────────────────────────────────────────────
    #  public ░  Re-indent, preserving wrapped-line offsets
    # ─────────────────────────────────────────────────────────────
    def fix_indentation(self, indent_size: int = 4):
        """
        Normalises indentation of every *.py* file found under *self.path*.

        • Tabs → spaces, invisible Unicode garbage stripped.  
        • Pure block lines: exactly `level × indent_size` spaces.  
        • Continuation lines (inside open brackets) keep at least the
          *same* visual offset they had in the original code, rounded **up**
          to the nearest multiple of *indent_size*.  
        • Lines that start with a closing bracket `) ] }` are *not* given
          the extra continuation indent – they align with the block again.
        """
        self.logger.log("Fixing indentation of code files…")
        files = []

        # — locate Python files —
        if os.path.isfile(self.path):
            if self.path.endswith(".py"):
                files.append(self.path)
            base_dir = os.path.dirname(self.path)
        else:
            base_dir = self.path
            for root, _, names in os.walk(self.path):
                files += [os.path.join(root, n) for n in names if n.endswith(".py")]

        # — backup folder —
        backup_root = os.path.join(os.path.dirname(base_dir),
                                   f"{os.path.basename(base_dir)}_old")
        os.makedirs(backup_root, exist_ok=True)
        self.logger.log(f"Backup → {backup_root}")

        invis = '\u200b\u200c\u200d\ufeff'

        for fp in files:
            rel = os.path.relpath(fp, base_dir)
            backup_fp = os.path.join(backup_root, rel)
            os.makedirs(os.path.dirname(backup_fp), exist_ok=True)

            if not os.path.exists(backup_fp):
                shutil.move(fp, backup_fp)
                self.logger.log(f"→ backup {rel}")
            else:
                self.logger.log(f"Backup exists for {rel}")

            # — read original —
            with open(backup_fp, encoding="utf-8") as f:
                raw = [ln.replace('\t', ' '*indent_size)
                         .lstrip(invis)           # leading junk
                         .rstrip(invis + " \r\n") # trailing junk
                       for ln in f.readlines()]

            levels, paren, cols = self._scan_indent_meta(raw)

            rebuilt = []
            for lvl, pd, col, ln in zip(levels, paren, cols, raw):
                if lvl is None:           # blank
                    rebuilt.append('\n')
                    continue

                base = lvl * indent_size
                extra = 0

                # inside (…) and not a closing-bracket line?
                if pd > 0 and not ln.lstrip().startswith((')', ']', '}')):
                    offset_needed = max(0, col - base)
                    extra_units = math.ceil(offset_needed / indent_size)
                    extra = extra_units * indent_size

                indent = ' ' * (base + extra)
                rebuilt.append(f"{indent}{ln.lstrip()}\n")

            with open(fp, 'w', encoding="utf-8") as f:
                f.writelines(rebuilt)
            self.logger.log(f"✓ fixed {rel}")

        self.logger.log("Indentation pass complete.")

def detect_get_patterns(text: str) -> List[Tuple[str, str, str, str]]:
    """
    Detect .get() method patterns in the given text.
    
    Args:
        text: The input text to search
        
    Returns:
        List of tuples containing (full_match, object, key, default_value)
    """
    # Regex pattern to match .get() calls
    # Explanation:
    # (\w+(?:\.\w+)*) - captures object name (can include dots like self.config)
    # \.get\(          - matches .get(
    # (["\'])          - captures opening quote (single or double)
    # ([^"']+)         - captures the key inside quotes
    # \2               - matches the same quote type as opening
    # ,\s*             - matches comma and optional whitespace
    # ([^)]+)          - captures the default value
    # \)               - matches closing parenthesis
    
    pattern = r'(\w+(?:\.\w+)*)\.get\((["\'])([^"\']+)\2,\s*([^)]+)\)'
    
    matches = []
    for match in re.finditer(pattern, text):
        full_match = match.group(0)
        object_name = match.group(1)
        quote_type = match.group(2)
        key = match.group(3)
        default_value = match.group(4)
        
        matches.append((full_match, object_name, key, default_value))
    
    return matches

def replace_get_with_bracket_access(text: str, remove_defaults: bool = True) -> str:
    """
    Replace .get() calls with bracket access syntax.
    
    Args:
        text: The input text to process
        remove_defaults: If True, removes default values and uses bracket access.
                        If False, keeps the logic but shows the transformation.
    
    Returns:
        Modified text with replacements
    """
    pattern = r'(\w+(?:\.\w+)*)\.get\((["\'])([^"\']+)\2,\s*([^)]+)\)'
    
    def replacement(match):
        object_name = match.group(1)
        quote_type = match.group(2)
        key = match.group(3)
        default_value = match.group(4)
        
        if remove_defaults:
            # Simple bracket access (assumes key exists)
            return f'{object_name}[{quote_type}{key}{quote_type}]'
        else:
            # Keep the default logic but show the pattern
            return f'{object_name}["{key}"]  # was: .get("{key}", {default_value})'
    
    return re.sub(pattern, replacement, text)

def analyze_file(file_path: str):
    """
    Analyze a file for .get() patterns and show statistics.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        matches = detect_get_patterns(content)
        
        print(f"Analysis of {file_path}")
        print("=" * 50)
        print(f"Total .get() patterns found: {len(matches)}")
        print()
        
        if matches:
            print("Found patterns:")
            print("-" * 30)
            for i, (full_match, obj, key, default) in enumerate(matches, 1):
                print(f"{i:2d}. {full_match}")
                print(f"    Object: {obj}")
                print(f"    Key: '{key}'")
                print(f"    Default: {default}")
                print(f"    Would become: {obj}[\"{key}\"]")
                print()
        
        # Show unique objects and keys
        objects = set(match[1] for match in matches)
        keys = set(match[2] for match in matches)
        
        print(f"Unique objects using .get(): {len(objects)}")
        for obj in sorted(objects):
            print(f"  - {obj}")
        print()
        
        print(f"Unique keys accessed: {len(keys)}")
        for key in sorted(keys):
            print(f"  - '{key}'")
        
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
    except Exception as e:
        print(f"Error reading file: {e}")

def demo_patterns():
    """
    Demonstrate the regex pattern with example strings.
    """
    test_strings = [
        'config.get("latent_period", 5.0)',
        'self.config.get("noise_std", 0.2)',
        'train_config.get("max_latent_period", 30.0)',
        'df.attrs.get("label", f"sensor_{s_id}")',
        'meta_data.get("sensors", [])',
        'cfg.get("min_period", 0.1)',
        'self.config.get("diffusion_steps", 100)',
    ]
    
    print("REGEX PATTERN DEMONSTRATION")
    print("=" * 50)
    print("Pattern: r'(\\w+(?:\\.\\w+)*)\\.get\\(([\"\\'])([^\"\\']*)\\2,\\s*([^)]+)\\)'")
    print()
    print("Test strings and their detection:")
    print("-" * 40)
    
    for test_str in test_strings:
        matches = detect_get_patterns(test_str)
        if matches:
            print(f"✓ FOUND: {test_str}")
            for full_match, obj, key, default in matches:
                print(f"  → Object: '{obj}', Key: '{key}', Default: {default}")
                print(f"  → Replacement: {obj}[\"{key}\"]")
        else:
            print(f"✗ NOT FOUND: {test_str}")
        print()
    
    print("\nAUTOMATIC REPLACEMENT DEMO:")
    print("-" * 30)
    sample_code = '''
    def example_function(self, config):
        self.lr = config.get("lr", 1e-3)
        self.noise_std = self.config.get("noise_std", 0.2)
        period = train_config.get("latent_period", 5.0)
        return period
    '''
    
    print("Original code:")
    print(sample_code)
    
    print("After replacement (bracket access):")
    replaced = replace_get_with_bracket_access(sample_code, remove_defaults=True)
    print(replaced)
    
    print("After replacement (with comments):")
    replaced_commented = replace_get_with_bracket_access(sample_code, remove_defaults=False)
    print(replaced_commented)

def replace_file_get_patterns(file_path: str, backup: bool = True, mode: str = "bracket") -> bool:
    """
    Replace all .get() patterns in a file with bracket access.
    
    Args:
        file_path: Path to the file to modify
        backup: If True, creates a backup file with .backup extension
        mode: "bracket" for simple bracket access, "commented" for bracket with comments
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Read the original file
        with open(file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        # Create backup if requested
        if backup:
            backup_path = file_path + '.backup'
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(original_content)
            print(f"Backup created: {backup_path}")
        
        # Detect patterns before replacement
        matches_before = detect_get_patterns(original_content)
        print(f"Found {len(matches_before)} .get() patterns to replace")
        
        # Perform replacement
        if mode == "commented":
            new_content = replace_get_with_bracket_access(original_content, remove_defaults=False)
        else:
            new_content = replace_get_with_bracket_access(original_content, remove_defaults=True)
        
        # Verify replacement worked
        matches_after = detect_get_patterns(new_content)
        
        # Write the modified content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"✓ Successfully replaced {len(matches_before) - len(matches_after)} patterns")
        if matches_after:
            print(f"⚠ Warning: {len(matches_after)} patterns still remain (might be complex cases)")
        
        return True
        
    except Exception as e:
        print(f"Error processing file: {e}")
        return False

if __name__ == "__main__":
    print("GET() Pattern Detector and Replacer")
    print("=" * 40)
    
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        
        # Check for replacement mode
        if len(sys.argv) > 2 and sys.argv[2] in ["--replace", "--replace-commented"]:
            mode = "commented" if sys.argv[2] == "--replace-commented" else "bracket"
            print(f"REPLACEMENT MODE: {mode}")
            print("=" * 40)
            
            # Show what will be replaced
            print("Preview of changes:")
            analyze_file(file_path)
            
            # Ask for confirmation (or proceed automatically)
            print("\n" + "="*50)
            print("🔄 PROCEEDING WITH REPLACEMENT...")
            
            success = replace_file_get_patterns(file_path, backup=True, mode=mode)
            
            if success:
                print("✅ File replacement completed successfully!")
                print("📁 Original file backed up with .backup extension")
            else:
                print("❌ File replacement failed!")
        else:
            # Analyze the provided file
            analyze_file(file_path)
    else:
        # Run demonstration
        demo_patterns()
        
        print("\n" + "="*50)
        print("USAGE:")
        print("  python get_pattern_detector.py [file_path] [--replace|--replace-commented]")
        print("  - Without file_path: Shows pattern demonstration")
        print("  - With file_path only: Analyzes the specified file")
        print("  - With --replace: Replaces .get() with bracket access")
        print("  - With --replace-commented: Replaces with comments showing original")
