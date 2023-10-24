import hashlib
import ast


class PythonFingerprinter(ast.NodeVisitor):
    def __init__(self):
        # A list to store the normalized version of the script
        self.normalized_script = []

    def visit_Str(self, node):
        # Replace all string literals (eg; "hello", 'world', etc) with a single token
        self.normalized_script.append("STRING_LITERAL")
        self.generic_visit(node)

    def visit_Num(self, node):
        # Replace all number literals (eg; 1, 500, 5.5, etc) with a single token
        self.normalized_script.append("NUMBER_LITERAL")
        self.generic_visit(node)

    # To handle complex use cases, define additional visit_ methods for other types of AST nodes. Ex - visit_ListComp(self, node), visit_Assign(self, node), visit_If(self, node), etc

    def generic_visit(self, node):
        self.normalized_script.append(node.__class__.__name__)
        super().generic_visit(node)


def normalize_python_script(script):
    """Parse the script and produce a normalized version using AST."""
    tree = ast.parse(script)
    visitor = PythonFingerprinter()
    visitor.visit(tree)
    return "".join(visitor.normalized_script)


def compute_fingerprint(script):
    """Compute a fingerprint for the python script."""
    normalized_script = normalize_python_script(script)
    print(normalized_script)
    return hashlib.md5(normalized_script.encode()).hexdigest()


def detect_duplicate_script(script, stored_fingerprints):
    """Detect whether the script is a duplicate."""
    fingerprint = compute_fingerprint(script)
    if fingerprint in stored_fingerprints:
        return True
    stored_fingerprints.add(fingerprint)
    return False


# Testing
stored_fingerprints = set()

script1 = """
def xyz(a, b):
    return a + b - c
"""

script2 = """
def xyz(x, y):
    return x + y - z
"""

script3 = """
def xyz(a, b):
    return a - b + c
"""


script4 = """
def xyz(a, b):
    return 1 - 2 + 3
"""


print(compute_fingerprint(script1), end="\n\n")
print(compute_fingerprint(script2), end="\n\n")
print(compute_fingerprint(script3), end="\n\n")
print(compute_fingerprint(script4), end="\n\n")
