"""
DAGVIZ provides a simple visualization of Directed Acyclic Graphs.
"""
try:
    import importlib.metadata as importlib_metadata  # type: ignore
except ModuleNotFoundError:
    import importlib_metadata

__version__ = importlib_metadata.version(__name__)

from typing import Any, Callable, Optional, Sequence, Union

import networkx as nx
from networkx.algorithms import dag

from .abstract import AbstractPlot
from .render import render
from .istyle import iStyle
from .style import metro
from .dagre import Dagre  # noqa


def make_abstract_plot(
    G: nx.Graph,
    *,
    target_node: Optional[Any] = None,
    include_ancestors: bool = False,
    order: Union[Sequence[Any], Callable[..., Sequence[Any]]] = dag.topological_sort
) -> AbstractPlot:
    """Generate an abstract plot for a DAG, optionally including ancestors of a target node.

    Args:
        G: The DAG to be visualized.
        target_node: The node for which ancestors may be included in the plot.
        include_ancestors: Flag to include ancestors of the target_node in the plot.
        order: Optional; The order of the nodes, or a function that creates an order
               from the graph. The default is to use a topological sort of the nodes.

    Returns:
        An abstract plot of the graph that can be used to render an image from.
    """
    plot = AbstractPlot()

    # If including ancestors, adjust the node sequence to include them
    if target_node and include_ancestors:
        ancestors = set(nx.ancestors(G, target_node)) if include_ancestors else set()
        sequence = [node for node in order(G) if node in ancestors or node == target_node]
        # Optionally, add descendants of target_node here, depending on how you want them visualized
    else:
        sequence = order(G) if callable(order) else order

    for nd in sequence:
        row = plot.add_row(G.nodes[nd].get("label", str(nd)))
        # Add inputs (predecessors)
        for pred in G.pred[nd]:
            row.add_input(pred)
        # Add the node itself
        row.add_node(nd, len(G.succ[nd]))

    return plot


def render_svg(
    G: nx.Graph, *, include_ancestors: bool = False, style: Callable[..., iStyle] = metro.svg_renderer()
) -> str:
    """
    Generate a DAG visualization as an SVG string.

    Args:
        G:     The DAG to visualize
        style: Optional; The visualization style to apply
    Returns:
        A string containing the SVG of the plot
    """
    return render(make_abstract_plot(G,include_ancestors=include_ancestors), style)


class Metro:
    """
    Render a topological ordering of a DAG using the "metro" style in
    jupyter notebooks.

    Args:
        G: directed acyclic graph to render
    """

    def __init__(self, G: nx.DiGraph):
        self.graph = G

    def _repr_html_(self) -> str:
        return render_svg(self.graph)
