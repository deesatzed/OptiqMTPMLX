"""
Example Nex plugin.

This adds a safe calculator tool that the agent can use.

Place this (or your own .py files) in ~/.nex/plugins/ or ./plugins/
The plugin system will auto-discover functions registered here.
"""

from nex.tools import TOOLS

def calculator(expression: str) -> str:
    """Safely evaluate a simple math expression."""
    import ast
    import operator as op

    # Supported operators
    operators = {
        ast.Add: op.add,
        ast.Sub: op.sub,
        ast.Mult: op.mul,
        ast.Div: op.truediv,
        ast.Pow: op.pow,
        ast.Mod: op.mod,
    }

    def eval_node(node):
        if isinstance(node, ast.Num):  # <number>
            return node.n
        elif isinstance(node, ast.BinOp):  # <left> <operator> <right>
            return operators[type(node.op)](eval_node(node.left), eval_node(node.right))
        elif isinstance(node, ast.UnaryOp):  # <operator> <operand>
            return operators[type(node.op)](eval_node(node.operand))
        else:
            raise TypeError(f"Unsupported expression: {node}")

    try:
        tree = ast.parse(expression, mode='eval')
        result = eval_node(tree.body)
        return str(result)
    except Exception as e:
        return f"Error: {e}"

# Register the tool
TOOLS["calculator"] = lambda args: calculator(args.get("expression", "")) 

def register_tools(tools_dict):
    """Plugin entry point called by the loader."""
    tools_dict["calculator"] = lambda args: calculator(args.get("expression", ""))
    print("[plugin] example_calculator registered 'calculator' tool")