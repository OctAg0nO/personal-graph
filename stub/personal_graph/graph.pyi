import types
from _typeshed import Incomplete
from contextlib import AbstractContextManager
from graphviz import Digraph  # type: ignore
from personal_graph.graph_generator import (
    OpenAITextToGraphParser as OpenAITextToGraphParser,
)
from personal_graph.models import (
    Edge as Edge,
    EdgeInput as EdgeInput,
    KnowledgeGraph as KnowledgeGraph,
    Node as Node,
)
from personal_graph.database import (
    SQLite as SQLite,
    TursoDB as TursoDB,
)
from personal_graph.vector_store import (
    SQLiteVSS as SQLiteVSS,
    VliteVSS as VliteVSS,
)
from typing import Any, Dict, List, Tuple

class GraphDB(AbstractContextManager):
    vector_store: Incomplete
    db: Incomplete
    graph_generator: Incomplete
    def __init__(
        self,
        *,
        vector_store: SQLiteVSS | VliteVSS = ...,
        database: TursoDB | SQLite = ...,
        graph_generator: OpenAITextToGraphParser = ...,
    ) -> None: ...
    def __eq__(self, other): ...
    def __enter__(self) -> GraphDB: ...
    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: types.TracebackType | None,
    ) -> None: ...
    def add_node(self, node: Node) -> None: ...
    def add_nodes(self, nodes: List[Node]) -> None: ...
    def add_edge(self, edge: EdgeInput) -> None: ...
    def add_edges(self, edges: List[EdgeInput]) -> None: ...
    def update_node(self, node: Node) -> None: ...
    def update_nodes(self, nodes: List[Node]) -> None: ...
    def remove_node(self, id: str | int) -> None: ...
    def remove_nodes(self, ids: List[Any]) -> None: ...
    def search_node(self, node_id: str | int) -> Any: ...
    def search_node_label(self, node_id: str | int) -> Any: ...
    def traverse(
        self, source: str, target: str | None = None, with_bodies: bool = False
    ) -> List: ...
    def insert_graph(self, kg: KnowledgeGraph) -> KnowledgeGraph: ...
    def search_from_graph(
        self,
        text: str,
        *,
        threshold: float = 0.9,
        limit: int = 1,
        descending: bool = False,
        sort_by: str = "",
    ) -> KnowledgeGraph: ...
    def merge_by_similarity(self, *, threshold: float = 0.9) -> None: ...
    def find_nodes_like(self, label: str, *, threshold: float = 0.9) -> List[Node]: ...
    def visualize(self, file: str, id: List[str]) -> Digraph: ...
    def fetch_ids_from_db(self) -> List[str]: ...
    def search_indegree_edges(self, target: str) -> List[Any]: ...
    def search_outdegree_edges(self, source: str) -> List[Any]: ...
    def is_unique_prompt(self, text: str, *, threshold: float = 0.9) -> bool: ...
    def insert(self, text: str, attributes: Dict) -> None: ...
    def search(
        self,
        text: str,
        *,
        threshold: float = 0.9,
        descending: bool = False,
        limit: int = 1,
        sort_by: str = "",
    ) -> None | List[Tuple[Any, str, dict, Any]]: ...