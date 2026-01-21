"""
Knowledge Graph Builder

Constructs semantic knowledge graphs from file system metadata,
creating mindmaps that show relationships between interests, projects, and skills.
"""

from typing import Dict, List, Set, Tuple, Optional
from pathlib import Path
from collections import defaultdict
import json
from datetime import datetime


class KnowledgeGraphBuilder:
    """
    Build hierarchical knowledge graphs from file metadata.

    Creates nodes for:
    - Interests (from inferred topics)
    - Projects (from directory structure)
    - Skills (from file types and topics)
    - Tools (from file types)

    Creates edges for:
    - related_to: Files with common topics
    - supports: Project support file relationships
    - derived_from: Generated/compiled files
    - part_of: Hierarchical relationships
    """

    def __init__(self, files: List[Dict]):
        """
        Initialize builder with file metadata.

        Args:
            files: List of file metadata dictionaries from SafeFilesystemScanner
        """
        self.files = files
        self.graph = {
            "nodes": {},
            "edges": [],
            "metadata": {}
        }

    def build_graph(self) -> Dict:
        """
        Build complete knowledge graph structure.

        Returns:
            Graph dictionary with nodes and edges
        """
        # Add nodes
        self._add_interest_nodes()
        self._add_project_nodes()
        self._add_skill_nodes()
        self._add_tool_nodes()

        # Add edges
        self._add_topic_edges()
        self._add_project_edges()
        self._add_skill_edges()

        # Add metadata
        self.graph["metadata"] = {
            "total_nodes": len(self.graph["nodes"]),
            "total_edges": len(self.graph["edges"]),
            "node_types": self._count_node_types(),
            "generated_at": datetime.now().isoformat(),
            "file_count": len(self.files)
        }

        return self.graph

    def _add_interest_nodes(self) -> None:
        """Extract and add interest nodes from file topics."""
        topics_count = defaultdict(int)

        # Count topic occurrences
        for file in self.files:
            for topic in file.get("topics", []):
                topics_count[topic] += 1

        # Create nodes for significant topics
        for topic, count in topics_count.items():
            if count >= 2:  # Only topics in 2+ files
                self._add_node(
                    node_id=f"interest_{topic}",
                    node_type="interest",
                    label=topic.title(),
                    properties={
                        "topic": topic,
                        "file_count": count,
                        "importance": min(1.0, count / 10.0),  # Normalize importance
                        "topic_type": "primary" if count > 5 else "secondary"
                    }
                )

    def _add_project_nodes(self) -> None:
        """Extract and add project nodes from directory structure."""
        projects = defaultdict(list)

        # Group files by top-level project directory
        for file in self.files:
            path = Path(file["path"])
            # Use the first significant directory as project
            if len(path.parts) >= 3:
                project_name = path.parts[-3]
                projects[project_name].append(file)

        # Create nodes for significant projects
        for project_name, project_files in projects.items():
            if len(project_files) >= 2:
                last_modified = max(f.get("modified_timestamp", 0) for f in project_files)

                self._add_node(
                    node_id=f"project_{project_name}",
                    node_type="project",
                    label=project_name.replace("_", " ").title(),
                    properties={
                        "project_name": project_name,
                        "file_count": len(project_files),
                        "last_modified": last_modified,
                        "status": "active" if self._is_recent(last_modified) else "archived",
                        "total_size": sum(f["size_bytes"] for f in project_files)
                    }
                )

    def _add_skill_nodes(self) -> None:
        """Extract and add skill nodes from file types and content."""
        skills_count = defaultdict(int)

        # Map file types to skills
        type_to_skill = {
            "code": ["Programming", "Software Development"],
            "documentation": ["Technical Writing", "Documentation"],
            "data": ["Data Analysis", "Data Management"],
            "database": ["Database Design", "SQL"],
            "web": ["Web Development", "Frontend Development"]
        }

        # Count file types to infer skills
        for file in self.files:
            file_type = file.get("file_type", "other")
            if file_type in type_to_skill:
                for skill in type_to_skill[file_type]:
                    skills_count[skill] += 1

        # Create skill nodes
        for skill, count in skills_count.items():
            self._add_node(
                node_id=f"skill_{skill.lower().replace(' ', '_')}",
                node_type="skill",
                label=skill,
                properties={
                    "skill": skill,
                    "proficiency": min("expert", "advanced" if count > 10 else "intermediate" if count > 5 else "beginner"),
                    "evidence_count": count
                }
            )

    def _add_tool_nodes(self) -> None:
        """Extract and add tool nodes from file types."""
        tools_count = defaultdict(int)

        # Map extensions to tools
        extension_to_tool = {
            ".py": "Python",
            ".js": "JavaScript",
            ".ts": "TypeScript",
            ".json": "JSON",
            ".sql": "SQL",
            ".md": "Markdown",
            ".html": "HTML",
            ".css": "CSS"
        }

        # Count tool usage
        for file in self.files:
            ext = file.get("extension", "")
            if ext in extension_to_tool:
                tool = extension_to_tool[ext]
                tools_count[tool] += 1

        # Create tool nodes
        for tool, count in tools_count.items():
            self._add_node(
                node_id=f"tool_{tool.lower()}",
                node_type="tool",
                label=tool,
                properties={
                    "tool": tool,
                    "usage_count": count,
                    "proficiency": "Expert" if count > 20 else "Intermediate" if count > 5 else "Basic"
                }
            )

    def _add_node(
        self,
        node_id: str,
        node_type: str,
        label: str,
        properties: Dict = None
    ) -> None:
        """Add a node to the graph."""
        self.graph["nodes"][node_id] = {
            "id": node_id,
            "type": node_type,
            "label": label,
            "properties": properties or {}
        }

    def _add_edge(
        self,
        source_id: str,
        target_id: str,
        relationship: str,
        weight: float = 1.0
    ) -> None:
        """Add an edge to the graph."""
        edge = {
            "source": source_id,
            "target": target_id,
            "relationship": relationship,
            "weight": weight
        }
        self.graph["edges"].append(edge)

    def _add_topic_edges(self) -> None:
        """Add edges between interests that share topics."""
        interest_nodes = [
            node_id for node_id, node in self.graph["nodes"].items()
            if node.get("type") == "interest"
        ]

        # Connect interests with shared file topics
        for i, interest1_id in enumerate(interest_nodes):
            for interest2_id in interest_nodes[i+1:]:
                # Check if they appear together in files
                shared_files = sum(
                    1 for file in self.files
                    if (interest1_id.replace("interest_", "") in [t.lower() for t in file.get("topics", [])]) and
                    (interest2_id.replace("interest_", "") in [t.lower() for t in file.get("topics", [])])
                )

                if shared_files > 0:
                    self._add_edge(
                        source_id=interest1_id,
                        target_id=interest2_id,
                        relationship="related_to",
                        weight=min(1.0, shared_files / 5.0)
                    )

    def _add_project_edges(self) -> None:
        """Add edges between projects and their skills/tools."""
        for file in self.files:
            # Map project to skills
            path = Path(file["path"])
            if len(path.parts) >= 3:
                project_name = path.parts[-3]
                project_id = f"project_{project_name}"

                # Connect to file type skills
                file_type = file.get("file_type", "")
                if file_type == "code":
                    skill_id = "skill_programming"
                    if skill_id in self.graph["nodes"]:
                        self._add_edge(
                            source_id=project_id,
                            target_id=skill_id,
                            relationship="uses"
                        )

    def _add_skill_edges(self) -> None:
        """Add edges between skills and tools."""
        # Connect programming skills to language tools
        skill_tool_map = {
            "skill_programming": ["tool_python", "tool_javascript", "tool_typescript"],
            "skill_web_development": ["tool_html", "tool_css", "tool_javascript"],
            "skill_database_design": ["tool_sql"]
        }

        for skill_id, tool_ids in skill_tool_map.items():
            if skill_id in self.graph["nodes"]:
                for tool_id in tool_ids:
                    if tool_id in self.graph["nodes"]:
                        self._add_edge(
                            source_id=skill_id,
                            target_id=tool_id,
                            relationship="uses"
                        )

    def _is_recent(self, timestamp: float, days: int = 90) -> bool:
        """Check if a timestamp is recent (within N days)."""
        import time
        return timestamp > (time.time() - days * 86400)

    def _count_node_types(self) -> Dict[str, int]:
        """Count nodes by type."""
        counts = defaultdict(int)
        for node in self.graph["nodes"].values():
            counts[node.get("type", "unknown")] += 1
        return dict(counts)

    def export_to_mindmap(self) -> str:
        """
        Export graph as Obsidian-style markdown mindmap.

        Format is compatible with Obsidian and other markdown mindmap tools.
        """
        lines = ["# Knowledge Map\n"]

        # Get primary interests
        interests = sorted(
            [n for n in self.graph["nodes"].values() if n.get("type") == "interest"],
            key=lambda x: x.get("properties", {}).get("file_count", 0),
            reverse=True
        )

        for interest in interests[:10]:  # Top 10 interests
            lines.append(f"\n## {interest['label']}")
            lines.append(f"Topics: {interest['properties'].get('file_count', 0)} files\n")

            # Find related nodes
            related_edges = [
                e for e in self.graph["edges"]
                if e["source"] == interest["id"] and e["relationship"] == "related_to"
            ]

            for edge in related_edges[:5]:
                target_node = self.graph["nodes"].get(edge["target"], {})
                lines.append(f"- Related: [[{target_node.get('label', 'Unknown')}]]")

        return "\n".join(lines)

    def export_to_json(self) -> str:
        """Export graph as JSON."""
        return json.dumps(self.graph, indent=2, default=str)

    def get_summary(self) -> Dict:
        """Get graph summary statistics."""
        return {
            "total_nodes": len(self.graph["nodes"]),
            "total_edges": len(self.graph["edges"]),
            "top_interests": self._get_top_nodes("interest", 5),
            "top_projects": self._get_top_nodes("project", 5),
            "top_skills": self._get_top_nodes("skill", 5),
            "top_tools": self._get_top_nodes("tool", 5),
            "connectivity": self._calculate_connectivity()
        }

    def _get_top_nodes(self, node_type: str, limit: int = 5) -> List[Dict]:
        """Get top nodes by importance."""
        nodes_of_type = [
            n for n in self.graph["nodes"].values()
            if n.get("type") == node_type
        ]

        # Sort by importance/count
        sorted_nodes = sorted(
            nodes_of_type,
            key=lambda x: x.get("properties", {}).get("file_count", 0) or
                         x.get("properties", {}).get("evidence_count", 0),
            reverse=True
        )

        return sorted_nodes[:limit]

    def _calculate_connectivity(self) -> float:
        """Calculate graph connectivity (0-1, higher = more connected)."""
        if not self.graph["nodes"] or not self.graph["edges"]:
            return 0.0

        max_edges = len(self.graph["nodes"]) * (len(self.graph["nodes"]) - 1) / 2
        actual_edges = len(self.graph["edges"])

        return min(1.0, actual_edges / (max_edges or 1))

