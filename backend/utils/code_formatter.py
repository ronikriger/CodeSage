import re
from typing import Dict, List

class CodeFormatter:
    @staticmethod
    def format_python(code: str) -> str:
        # Remove extra whitespace
        code = re.sub(r'\s+', ' ', code)
        # Add proper indentation
        lines = code.split(';')
        formatted_lines = []
        indent_level = 0
        
        for line in lines:
            line = line.strip()
            if line.endswith(':'):
                formatted_lines.append('    ' * indent_level + line)
                indent_level += 1
            elif line.startswith(('return', 'break', 'continue')):
                indent_level = max(0, indent_level - 1)
                formatted_lines.append('    ' * indent_level + line)
            else:
                formatted_lines.append('    ' * indent_level + line)
        
        return '\n'.join(formatted_lines)

    @staticmethod
    def format_javascript(code: str) -> str:
        # Basic JavaScript formatting
        code = re.sub(r';\s*', ';\n', code)
        code = re.sub(r'{\s*', '{\n', code)
        code = re.sub(r'}\s*', '}\n', code)
        return code

    @staticmethod
    def detect_language(code: str) -> str:
        # Simple language detection based on syntax
        if 'def ' in code or 'import ' in code:
            return 'python'
        elif 'function ' in code or 'const ' in code:
            return 'javascript'
        return 'unknown'

    @staticmethod
    def format_code(code: str, language: str = None) -> str:
        if not language:
            language = CodeFormatter.detect_language(code)
        
        formatters = {
            'python': CodeFormatter.format_python,
            'javascript': CodeFormatter.format_javascript
        }
        
        formatter = formatters.get(language.lower())
        if formatter:
            return formatter(code)
        return code 