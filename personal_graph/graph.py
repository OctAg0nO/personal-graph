from __future__ import annotations

import json
import uuid
from typing import Any, List, Optional, Union, Dict, Callable

import libsql_experimental as libsql  # type: ignore
from contextlib import AbstractContextManager

from graphviz import Digraph  # type: ignore
from dotenv import load_dotenv

from personal_graph.clients import LLMClient
from personal_graph.graph_generator import InstructorGraphGenerator
from personal_graph.models import Node, EdgeInput, KnowledgeGraph
from personal_graph.database.sqlitevss import SQLiteVSS
from personal_graph.database.vlitedatabase import VLiteDatabase

load_dotenv()
CursorExecFunction = Callable[[libsql.Cursor, libsql.Connection], Any]


class Graph(AbstractContextManager):
    def __init__(
        self,
        *,
        vector_store: Union[SQLiteVSS, VLiteDatabase],
        graph_generator: InstructorGraphGenerator = InstructorGraphGenerator(llm_client=LLMClient()),
    ):
        self.vector_store = vector_store
        self.graph_generator = graph_generator

    def __eq__(self, other):
        if not isinstance(other, Graph):
            return "Not of Graph Type"
        else:
            return self.vector_store == other.vector_store

    def __enter__(self) -> Graph:
        self.vector_store.initialize()
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.vector_store.save()

    # High level apis
    def add_node(self, node: Node) -> None:
        self.vector_store.add_node(
            node.label,
            json.loads(node.attributes)
            if isinstance(node.attributes, str)
            else node.attributes,
            node.id,
        )

    def add_nodes(self, nodes: List[Node]) -> None:
        labels: List[str] = [node.label for node in nodes]
        attributes: List[Union[Dict[str, str]]] = [
            json.loads(node.attributes)
            if isinstance(node.attributes, str)
            else node.attributes
            for node in nodes
        ]
        ids: List[str | int] = [node.id for node in nodes]

        self.vector_store.add_nodes(
            attributes=attributes,
            labels=labels,
            ids=ids,
        )

    def add_edge(self, edge: EdgeInput) -> None:
        self.vector_store.add_edge(
            edge.source.id,
            edge.target.id,
            edge.label,
            json.loads(edge.attributes)
            if isinstance(edge.attributes, str)
            else edge.attributes,
        )

    def add_edges(self, edges: List[EdgeInput]) -> None:
        sources: List[str | int] = [edge.source.id for edge in edges]
        targets: List[str | int] = [edge.target.id for edge in edges]
        labels: List[str] = [edge.label for edge in edges]
        attributes: List[Union[Dict[str, str]]] = [
            json.loads(edge.attributes)
            if isinstance(edge.attributes, str)
            else edge.attributes
            for edge in edges
        ]

        self.vector_store.add_edges(
            sources=sources, targets=targets, labels=labels, attributes=attributes
        )

    def update_node(self, node: Node) -> None:
        self.vector_store.update_node(node)

    def update_nodes(self, nodes: List[Node]) -> None:
        for node in nodes:
            self.update_node(node)

    def remove_node(self, id: Union[str, int]) -> None:
        self.vector_store.remove_node(id)

    def remove_nodes(self, ids: List[Any]) -> None:
        self.vector_store.remove_nodes(ids)

    def search_node(self, node_id: str | int) -> Any:
        return self.vector_store.search_node(node_id)

    def search_node_label(self, node_id: str | int) -> Any:
        return self.vector_store.search_node_label(node_id)

    def traverse(
        self, source: str, target: Optional[str] = None, with_bodies: bool = False
    ) -> List:
        return self.vector_store.traverse(source, target, with_bodies)

    def insert_into_graph(self, text: str) -> KnowledgeGraph:
        uuid_dict = {}
        kg = self.graph_generator.generate(text)

        try:
            for node in kg.nodes:
                uuid_dict[node.id] = str(uuid.uuid4())
                self.vector_store.add_node(
                    node.label,
                    {"body": node.attributes},
                    uuid_dict[node.id],
                )

            for edge in kg.edges:
                self.vector_store.add_edge(
                    uuid_dict[edge.source],
                    uuid_dict[edge.target],
                    edge.label,
                    {"body": edge.attributes},
                )
        except KeyError:
            return KnowledgeGraph()
        return kg

    def search_from_graph(
        self, text: str, *, limit: int = 5, descending: bool = False, sort_by: str = ""
    ) -> KnowledgeGraph:
        return self.vector_store.search_from_graph(
            text, limit=limit, descending=descending, sort_by=sort_by
        )

    def visualize_graph(self, kg: KnowledgeGraph) -> Digraph:
        dot = Digraph(comment="Knowledge Graph")

        # Add nodes
        for node in kg.nodes:
            dot.node(str(node.id), node.label, color="black")

        # Add edges
        for edge in kg.edges:
            dot.edge(str(edge.source), str(edge.target), edge.label, color="black")

        return dot

    def merge_by_similarity(self, threshold) -> None:
        self.vector_store.merge_by_similarity(threshold)

    def find_nodes_like(self, label: str, threshold: float) -> List[Node]:
        return self.vector_store.find_nodes_like(label, threshold)

    def visualize(self, file: str, path: List[str]) -> Digraph:
        return self.vector_store.graphviz_visualize(file, path)

    def fetch_ids_from_db(self) -> List[str]:
        return self.vector_store.fetch_ids_from_db()

    def search_indegree_edges(self, target: str) -> List[Any]:
        return self.vector_store.search_indegree_edges(target)

    def search_outdegree_edges(self, source: str) -> List[Any]:
        return self.vector_store.search_outdegree_edges(source)

    def is_unique_prompt(self, text: str, threshold: float) -> bool:
        similar_nodes = self.vector_store.vector_search_node(
            {"body": text}, threshold=threshold, descending=False, limit=1, sort_by=""
        )

        if not similar_nodes:
            return True
        return False

    def insert(
        self,
        text: str,
        attributes: Dict,
    ) -> None:
        node = Node(
            id=str(uuid.uuid4()),
            label=text,
            attributes=json.dumps(attributes),
        )
        self.add_node(node)

    def search(
        self,
        text: str,
        *,
        descending: bool = False,
        limit: int = 1,
        sort_by: str = "",
    ):
        return self.vector_store.search(
            text, descending=descending, limit=limit, sort_by=sort_by
        )
