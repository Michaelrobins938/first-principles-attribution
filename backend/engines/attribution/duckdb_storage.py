"""
DuckDB Attribution Storage Engine

This module provides high-performance analytics storage for attribution results
using DuckDB MCP. Enables fast SQL queries over attribution data.
"""

import duckdb
import json
from typing import List, Dict, Optional, Tuple
from datetime import datetime
from pathlib import Path


class DuckDBAttributionStorage:
    """Store and query attribution data using DuckDB."""

    def __init__(self, db_path: str = "data/attribution_analytics.duckdb"):
        """
        Initialize DuckDB connection for attribution analytics.

        Args:
            db_path: Path to DuckDB database file
        """
        self.db_path = db_path
        self.conn = None
        self._initialize_connection()
        self._create_schema()

    def _initialize_connection(self) -> None:
        """Initialize and connect to DuckDB."""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self.conn = duckdb.connect(self.db_path)
        # Enable JSON support
        self.conn.execute("INSTALL json")
        self.conn.execute("LOAD json")

    def _create_schema(self) -> None:
        """Create attribution analysis schema."""

        # Journeys table
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS journeys (
                journey_id VARCHAR PRIMARY KEY,
                user_id VARCHAR,
                start_date TIMESTAMP,
                end_date TIMESTAMP,
                conversion BOOLEAN,
                conversion_value FLOAT,
                num_touchpoints INTEGER,
                duration_hours FLOAT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Touchpoints table
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS touchpoints (
                touchpoint_id VARCHAR PRIMARY KEY,
                journey_id VARCHAR,
                channel VARCHAR,
                timestamp TIMESTAMP,
                context VARCHAR,
                position INTEGER,
                FOREIGN KEY (journey_id) REFERENCES journeys(journey_id)
            )
        """)

        # Attribution results table
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS attribution_results (
                result_id VARCHAR PRIMARY KEY,
                run_id VARCHAR,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                channel VARCHAR,
                markov_value FLOAT,
                shapley_value FLOAT,
                hybrid_value FLOAT,
                alpha FLOAT,
                methodology VARCHAR,
                total_journeys INTEGER,
                processing_time_ms FLOAT
            )
        """)

        # Channel statistics table
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS channel_stats (
                channel_id VARCHAR PRIMARY KEY,
                channel_name VARCHAR,
                total_touchpoints INTEGER,
                total_conversions INTEGER,
                conversion_rate FLOAT,
                avg_position FLOAT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Analysis runs table (for tracking experiments)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS analysis_runs (
                run_id VARCHAR PRIMARY KEY,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                description VARCHAR,
                num_journeys INTEGER,
                num_channels INTEGER,
                alpha_value FLOAT,
                include_uncertainty BOOLEAN,
                processing_time_ms FLOAT,
                status VARCHAR
            )
        """)

    def store_journeys(self, journeys: List[Dict]) -> int:
        """
        Store journeys in DuckDB.

        Args:
            journeys: List of journey dictionaries

        Returns:
            Number of journeys stored
        """
        inserted = 0

        for journey in journeys:
            # Insert journey
            self.conn.execute("""
                INSERT INTO journeys
                (journey_id, user_id, start_date, end_date, conversion, conversion_value, num_touchpoints, duration_hours)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, [
                journey.get("journey_id"),
                journey.get("user_id", "anonymous"),
                journey.get("path", [{}])[0].get("timestamp") if journey.get("path") else None,
                journey.get("path", [{}])[-1].get("timestamp") if journey.get("path") else None,
                journey.get("conversion", False),
                journey.get("conversion_value", 0.0),
                len(journey.get("path", [])),
                journey.get("duration_hours", 0.0)
            ])

            # Insert touchpoints
            for i, touchpoint in enumerate(journey.get("path", [])):
                self.conn.execute("""
                    INSERT INTO touchpoints
                    (touchpoint_id, journey_id, channel, timestamp, context, position)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, [
                    f"{journey.get('journey_id')}_{i}",
                    journey.get("journey_id"),
                    touchpoint.get("channel"),
                    touchpoint.get("timestamp"),
                    touchpoint.get("context"),
                    i
                ])

            inserted += 1

        self.conn.commit()
        return inserted

    def store_attribution_results(self, run_id: str, results: Dict) -> None:
        """
        Store attribution analysis results.

        Args:
            run_id: Unique identifier for this analysis run
            results: Attribution analysis results dictionary
        """
        markov_values = results.get("markov_result", {}).get("channel_attributions", {})
        shapley_values = results.get("shapley_result", {}).get("channel_values", {})
        hybrid_values = results.get("hybrid_result", {}).get("channel_attributions", {})

        all_channels = set(markov_values.keys()) | set(shapley_values.keys()) | set(hybrid_values.keys())

        result_id = 1
        for channel in all_channels:
            self.conn.execute("""
                INSERT INTO attribution_results
                (result_id, run_id, channel, markov_value, shapley_value, hybrid_value, alpha, methodology, total_journeys, processing_time_ms)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, [
                f"{run_id}_{result_id}",
                run_id,
                channel,
                markov_values.get(channel, 0.0),
                shapley_values.get(channel, 0.0),
                hybrid_values.get(channel, 0.0),
                results.get("hybrid_result", {}).get("alpha_used", 0.5),
                "hybrid",
                results.get("total_journeys", 0),
                results.get("processing_time_ms", 0)
            ])
            result_id += 1

        self.conn.commit()

    def store_analysis_run(self, run_id: str, metadata: Dict) -> None:
        """Store analysis run metadata."""
        self.conn.execute("""
            INSERT INTO analysis_runs
            (run_id, description, num_journeys, num_channels, alpha_value, include_uncertainty, processing_time_ms, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, [
            run_id,
            metadata.get("description", ""),
            metadata.get("total_journeys", 0),
            metadata.get("unique_channels", 0),
            metadata.get("alpha", 0.5),
            metadata.get("include_uncertainty", False),
            metadata.get("processing_time_ms", 0),
            "completed"
        ])
        self.conn.commit()

    def query_channel_performance(self, channel: str) -> Dict:
        """
        Query performance metrics for a specific channel.

        Args:
            channel: Channel name to query

        Returns:
            Dictionary with channel metrics
        """
        result = self.conn.execute(f"""
            SELECT
                channel,
                COUNT(*) as total_occurrences,
                SUM(CASE WHEN j.conversion THEN 1 ELSE 0 END) as total_conversions,
                CAST(SUM(CASE WHEN j.conversion THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*) as conversion_rate,
                AVG(t.position) as avg_position,
                AVG(j.conversion_value) as avg_conversion_value
            FROM touchpoints t
            JOIN journeys j ON t.journey_id = j.journey_id
            WHERE t.channel = ?
            GROUP BY t.channel
        """, [channel]).fetchall()

        if not result:
            return {}

        row = result[0]
        return {
            "channel": row[0],
            "total_occurrences": row[1],
            "total_conversions": row[2],
            "conversion_rate": row[3],
            "avg_position": row[4],
            "avg_conversion_value": row[5]
        }

    def query_channel_ranking(self) -> List[Dict]:
        """Query ranking of channels by attribution value."""
        result = self.conn.execute("""
            SELECT
                channel,
                SUM(hybrid_value) as total_hybrid_value,
                AVG(hybrid_value) as avg_hybrid_value,
                COUNT(*) as occurrences
            FROM attribution_results
            GROUP BY channel
            ORDER BY total_hybrid_value DESC
        """).fetchall()

        return [
            {
                "channel": row[0],
                "total_hybrid_value": row[1],
                "avg_hybrid_value": row[2],
                "occurrences": row[3]
            }
            for row in result
        ]

    def query_journey_metrics(self) -> Dict:
        """Query overall journey metrics."""
        result = self.conn.execute("""
            SELECT
                COUNT(*) as total_journeys,
                SUM(CASE WHEN conversion THEN 1 ELSE 0 END) as total_conversions,
                AVG(num_touchpoints) as avg_touchpoints,
                AVG(duration_hours) as avg_duration,
                SUM(conversion_value) as total_value
            FROM journeys
        """).fetchall()

        if not result:
            return {}

        row = result[0]
        return {
            "total_journeys": row[0],
            "total_conversions": row[1],
            "conversion_rate": (row[1] or 0) / (row[0] or 1),
            "avg_touchpoints": row[2],
            "avg_duration_hours": row[3],
            "total_conversion_value": row[4]
        }

    def query_sensitivity_analysis(self, run_id: str) -> List[Dict]:
        """Query sensitivity analysis results for alpha parameter."""
        result = self.conn.execute("""
            SELECT
                alpha,
                channel,
                hybrid_value
            FROM attribution_results
            WHERE run_id = ?
            ORDER BY alpha, hybrid_value DESC
        """, [run_id]).fetchall()

        return [
            {"alpha": row[0], "channel": row[1], "hybrid_value": row[2]}
            for row in result
        ]

    def export_to_json(self, table_name: str) -> str:
        """Export table to JSON string."""
        result = self.conn.execute(f"SELECT * FROM {table_name}").fetch_arrow_table()
        return result.to_pandas().to_json(orient="records")

    def get_summary_statistics(self) -> Dict:
        """Get overall summary statistics."""
        stats = {
            "journey_metrics": self.query_journey_metrics(),
            "channel_ranking": self.query_channel_ranking()[:10],  # Top 10 channels
            "database_path": self.db_path,
            "last_updated": datetime.now().isoformat()
        }
        return stats

    def close(self) -> None:
        """Close DuckDB connection."""
        if self.conn:
            self.conn.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

