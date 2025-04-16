import argparse
import sys
import graphviz


class OrgNode:
    def __init__(self, name):
        self.name = name.strip()
        self.children = []
        self.parent = None

    def add_child(self, child):
        self.children.append(child)
        child.parent = self


def count_leading_spaces(line):
    return len(line) - len(line.lstrip())


def parse_org_file(filename):
    root = OrgNode("Root")
    stack = [(root, -1)]  # (node, indent_level)

    with open(filename, "r") as f:
        for line in f:
            if not line.strip():  # Skip empty lines
                continue

            indent = count_leading_spaces(line)
            node = OrgNode(line.strip())

            # Find the parent by looking for the last node with less indentation
            while stack and stack[-1][1] >= indent:
                stack.pop()

            parent, _ = stack[-1]
            parent.add_child(node)
            stack.append((node, indent))

    return root


def print_org_chart(node, level=0):
    print("  " * level + "- " + node.name)
    for child in node.children:
        print_org_chart(child, level + 1)


def print_reporting_relationships(node):
    """
    Prints all reporting relationships starting at the given node.

    For each node, prints a line of the form "X reports to Y", where X is the
    node's name and Y is the name of its parent node. Does not print anything for
    the root node.

    Recursively calls itself on the node's children.

    Parameters
    ----------
    node : OrgNode
        The node at which to start printing reporting relationships.
    """
    if node.parent and node.parent.name != "Root":
        print(f"{node.name} reports to {node.parent.name}")
    for child in node.children:
        print_reporting_relationships(child)


def print_mermaid_flowchart(node):
    """
    Prints a Mermaid flowchart representing the organization chart rooted at `node`.

    The flowchart is printed in Markdown format, surrounded by triple backticks.
    The graph is specified in the Mermaid "flowchart" syntax, with the root node
    at the top and children listed below.

    Parameters
    ----------
    node : OrgNode
        The root of the organization chart to print.
    node_id : str, optional
        The node ID to use for the root node. Defaults to "0".
    """
    if node.name == "Root" and node.children:
        print("```mermaid")
        print("flowchart TB")
        _print_mermaid_nodes(node.children[0])
        print("```")


def _print_mermaid_nodes(node, parent_id=None, counter=None):
    """
    Prints the Mermaid syntax for a single node and its children.

    Parameters
    ----------
    node : OrgNode
        The node to print.
    parent_id : str, optional
        The node ID of the parent node. Defaults to None.
    counter : list[int], optional
        The node ID counter. Defaults to None.

    Notes
    -----
    This function uses a counter to generate unique node IDs. The counter is
    passed by reference, so the function modifies it in place.

    """
    if counter is None:
        counter = [0]
    current_id = f"n{counter[0]}"
    counter[0] += 1

    # Print the node
    print(f'\t{current_id}["{node.name}"]')

    # Print connection to parent
    if parent_id is not None:
        print(f"\t{parent_id} --> {current_id}")

    # Process children
    for child in node.children:
        _print_mermaid_nodes(child, current_id, counter)


def generate_svg_chart(node, output_file="org_chart"):
    """
    Generates an SVG representation of the organization chart.
    
    Parameters
    ----------
    node : OrgNode
        The root node of the organization chart.
    output_file : str, optional
        The name of the output file (without extension). Defaults to "org_chart".
    
    Returns
    -------
    str
        Path to the generated SVG file.
    """
    dot = graphviz.Digraph(comment='Organization Chart')
    dot.attr(rankdir='TB')  # Top to bottom layout
    dot.attr('node', shape='box', style='rounded,filled', fillcolor='lightblue')
    
    def add_nodes(node, node_ids=None):
        if node_ids is None:
            node_ids = {}
        
        if node.name == "Root":
            for child in node.children:
                add_nodes(child, node_ids)
            return
            
        # Create unique ID for this node if not already created
        if node.name not in node_ids:
            node_ids[node.name] = f"node_{len(node_ids)}"
        
        current_id = node_ids[node.name]
        dot.node(current_id, node.name)
        
        # Add edges to children
        for child in node.children:
            if child.name not in node_ids:
                node_ids[child.name] = f"node_{len(node_ids)}"
            child_id = node_ids[child.name]
            dot.edge(current_id, child_id)
            add_nodes(child, node_ids)
    
    add_nodes(node)
    dot.render(output_file, format='svg', cleanup=True)
    return f"{output_file}.svg"


def main():
    """
    Entry point for the program.

    Reads an organization structure from a file specified by command line argument
    and prints the requested representation of the structure.

    Command line arguments:
    ----------------------
    filename : str
        Path to the input text file containing the organization structure.
        If not provided, defaults to "org.txt".
    --format, -f : str
        Output format. One of: 'tree' (indented organization chart),
        'visio' (reporting relationships in a format suitable for Visio), or 'mermaid' (Mermaid flowchart).
        If not provided, defaults to showing all formats.
    """
    parser = argparse.ArgumentParser(
        description="Generate organization charts from an indented text file"
    )
    parser.add_argument(
        "filename",
        nargs="?",
        default="org.txt",
        help="path to the input text file (default: org.txt)",
    )
    parser.add_argument(
        "-f",
        "--format",
        choices=["tree", "visio", "mermaid", "svg"],
        help="output format (default: show all formats)",
    )
    args = parser.parse_args()

    try:
        root = parse_org_file(args.filename)
        
        # If no format specified, show all formats
        if args.format is None:
            print("Organization Chart", file=sys.stderr)
            print_org_chart(root.children[0])  # Skip the artificial root node
            print("\nReporting Relationships (for Visio import)", file=sys.stderr)
            print_reporting_relationships(root.children[0])
            print("\nMermaid Flowchart", file=sys.stderr)
            print_mermaid_flowchart(root)
            print("\nGenerating SVG...", file=sys.stderr)
            svg_file = generate_svg_chart(root.children[0])
            print(f"SVG file generated: {svg_file}", file=sys.stderr)
        else:
            # Show only the requested format
            if args.format == "tree":
                print_org_chart(root.children[0])
            elif args.format == "visio":
                print_reporting_relationships(root.children[0])
            elif args.format == "mermaid":
                print_mermaid_flowchart(root)
            elif args.format == "svg":
                svg_file = generate_svg_chart(root.children[0])
                print(f"SVG file generated: {svg_file}")
    except FileNotFoundError:
        print(
            f"Error: {args.filename} not found. Please create a text file with your organization structure."
        )
        print(
            "Each line should represent a resource, with indentation showing reporting relationships."
        )


if __name__ == "__main__":
    main()
