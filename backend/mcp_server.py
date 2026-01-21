"""
MCP Server for Attribution Engine

This module exposes the attribution and covariation analysis functions
via the Model Context Protocol (MCP) for integration with WeKnora.

Usage:
    python backend/mcp_server.py

The server will run on stdin/stdout for MCP protocol communication.
"""

import json
import sys
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

sys.path.insert(0, '.')

from backend.engines.attribution.engine import AttributionEngine, MarkovAttribution, ShapleyAttribution
from backend.engines.attribution.covariation import (
    CovariationEngine,
    CovariationResult,
    AttributionType,
    create_covariation_insight
)


@dataclass
class MCPRequest:
    method: str
    params: Dict[str, Any]
    id: Optional[str] = None


@dataclass
class MCPResponse:
    result: Dict[str, Any]
    id: Optional[str] = None


class AttributionMCPServer:
    """MCP Server exposing attribution analysis tools."""
    
    def __init__(self):
        self.attribution_engine = None
        self.covariation_engine = CovariationEngine()
    
    def handle_request(self, request: MCPRequest) -> MCPResponse:
        """Handle incoming MCP request."""
        method_name = request.method
        
        handlers = {
            "analyze_attribution": self.analyze_attribution,
            "analyze_markov": self.analyze_markov,
            "analyze_shapley": self.analyze_shapley,
            "analyze_covariation": self.analyze_covariation,
            "enrich_attribution": self.enrich_attribution,
            "get_internal_behaviors": self.get_internal_behaviors,
            "get_external_behaviors": self.get_external_behaviors,
            "load_journeys": self.load_journeys,
            "analyze_all": self.analyze_all,
            "ping": self.ping,
        }
        
        handler = handlers.get(method_name)
        if handler:
            try:
                result = handler(request.params)
                return MCPResponse(result=result, id=request.id)
            except Exception as e:
                return MCPResponse(
                    result={"error": str(e), "type": type(e).__name__},
                    id=request.id
                )
        else:
            return MCPResponse(
                result={"error": f"Unknown method: {method_name}"},
                id=request.id
            )
    
    def ping(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Health check endpoint."""
        return {
            "status": "ok",
            "service": "attribution-mcp-server",
            "timestamp": datetime.now().isoformat(),
            "version": "2.0.0"
        }
    
    def load_journeys(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Load journey data for analysis."""
        journeys = params.get("journeys", [])
        
        if not journeys and "file_path" in params:
            import os
            file_path = params["file_path"]
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    journeys = json.load(f)
        
        if journeys:
            self.attribution_engine = AttributionEngine(journeys)
            return {
                "status": "loaded",
                "journey_count": len(journeys),
                "unique_channels": len(set(
                    tp.get("channel") 
                    for j in journeys 
                    for tp in j.get("path", [])
                )) if journeys else 0
            }
        
        return {"status": "no_data", "message": "No journeys provided"}
    
    def analyze_attribution(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Run hybrid Markov-Shapley attribution analysis."""
        alpha = params.get("alpha", 0.5)
        journeys = params.get("journeys", [])
        filter_channels = params.get("filter_channels")
        
        if not journeys and self.attribution_engine:
            pass
        elif journeys:
            self.attribution_engine = AttributionEngine(journeys)
        
        if not self.attribution_engine:
            return {"error": "No data loaded. Call load_journeys first."}
        
        result = self.attribution_engine.run_analysis(
            alpha=alpha,
            include_uncertainty=params.get("include_uncertainty", True),
            filter_channels=filter_channels
        )
        
        return result
    
    def analyze_markov(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Run Markov Chain attribution only."""
        journeys = params.get("journeys", [])
        
        if journeys:
            markov = MarkovAttribution(journeys)
            result = markov.get_full_result()
            return result.model_dump()
        
        if self.attribution_engine:
            markov = MarkovAttribution(self.attribution_engine.journeys)
            return markov.get_full_result().model_dump()
        
        return {"error": "No data available"}
    
    def analyze_shapley(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Run Shapley Value attribution only."""
        journeys = params.get("journeys", [])
        max_iterations = params.get("max_iterations", 1000)
        
        if journeys:
            shapley = ShapleyAttribution(journeys, max_iterations=max_iterations)
            result = shapley.get_full_result()
            return result.model_dump()
        
        if self.attribution_engine:
            shapley = ShapleyAttribution(self.attribution_engine.journeys)
            return shapley.get_full_result().model_dump()
        
        return {"error": "No data available"}
    
    def analyze_covariation(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze behaviors using Kelley Covariation Model."""
        behavior = params.get("behavior")
        observations = params.get("observations", [])
        
        if behavior:
            if observations:
                from backend.engines.attribution.covariation import Observation
                for obs_data in observations:
                    obs = Observation(**obs_data)
                    self.covariation_engine.add_observation(behavior, obs)
            
            result = self.covariation_engine.analyze_behavior(behavior)
            return result.to_dict()
        
        if observations:
            from backend.engines.attribution.covariation import Observation
            for obs_data in observations:
                obs = Observation(**obs_data)
                self.covariation_engine.add_observation(
                    obs_data.get("action", "unknown"), obs
                )
        
        all_results = self.covariation_engine.analyze_all()
        return {
            behavior: result.to_dict() 
            for behavior, result in all_results.items()
        }
    
    def enrich_attribution(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Combine Markov-Shapley attribution with Covariation analysis."""
        journeys = params.get("journeys", [])
        alpha = params.get("alpha", 0.5)
        
        if journeys:
            self.attribution_engine = AttributionEngine(journeys)
        
        if not self.attribution_engine:
            return {"error": "No data loaded"}
        
        result = self.attribution_engine.run_analysis(alpha=alpha)
        
        markov = result.get("markov_result", {}).get("channel_attributions", {})
        shapley = result.get("shapley_result", {}).get("channel_values", {})
        
        self.covariation_engine.add_observations_from_journey_data(journeys)
        
        from backend.engines.attribution.covariation import analyze_attribution_with_covariation
        
        enriched = analyze_attribution_with_covariation(
            markov_attribution=markov,
            shapley_attribution=shapley,
            journey_data=journeys,
            alpha=alpha
        )
        
        return {
            "attribution_result": result,
            "covariation_enrichment": enriched
        }
    
    def get_internal_behaviors(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get list of internally-attributed behaviors."""
        behaviors = self.covariation_engine.get_internal_behaviors()
        return {"behaviors": behaviors, "type": "internal"}
    
    def get_external_behaviors(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get list of externally-attributed behaviors."""
        behaviors = self.covariation_engine.get_external_behaviors()
        return {"behaviors": behaviors, "type": "external"}
    
    def analyze_all(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Run complete analysis (attribution + covariation)."""
        journeys = params.get("journeys", [])
        alpha = params.get("alpha", 0.5)
        
        if journeys:
            self.attribution_engine = AttributionEngine(journeys)
            self.covariation_engine.add_observations_from_journey_data(journeys)
        
        if not self.attribution_engine:
            return {"error": "No data loaded"}
        
        attribution_result = self.attribution_engine.run_analysis(alpha=alpha)
        covariation_results = self.covariation_engine.analyze_all()
        
        return {
            "status": "success",
            "attribution": attribution_result,
            "covariation": {
                behavior: result.to_dict()
                for behavior, result in covariation_results.items()
            },
            "internal_behaviors": self.covariation_engine.get_internal_behaviors(),
            "external_behaviors": self.covariation_engine.get_external_behaviors()
        }


def main():
    """Main entry point for MCP server."""
    server = AttributionMCPServer()
    
    print("Attribution MCP Server started", file=sys.stderr)
    
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        
        try:
            request_data = json.loads(line)
            request = MCPRequest(
                method=request_data.get("method", ""),
                params=request_data.get("params", {}),
                id=request_data.get("id")
            )
            
            response = server.handle_request(request)
            
            response_data = {"result": response.result}
            if response.id:
                response_data["id"] = response.id
            
            print(json.dumps(response_data))
            sys.stdout.flush()
            
        except json.JSONDecodeError as e:
            print(json.dumps({"error": f"Invalid JSON: {str(e)}"}))
            sys.stdout.flush()
        except Exception as e:
            print(json.dumps({"error": str(e)}))
            sys.stdout.flush()


if __name__ == "__main__":
    main()
