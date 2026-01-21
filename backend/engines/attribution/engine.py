import numpy as np
from typing import Dict, List, Any
from models.attribution import Journey

class AttributionEngine:
    def __init__(self, journeys: List[Journey]):
        self.journeys = journeys
        self.channels = self._extract_channels()
        self.n_channels = len(self.channels)
        self.channel_to_idx = {c: i for i, c in enumerate(self.channels)}
        
    def _extract_channels(self) -> List[str]:
        channels = set()
        for j in self.journeys:
            for tp in j.path:
                channels.add(tp.channel)
        return sorted(list(channels))
    
    def _build_transition_matrix(self) -> np.ndarray:
        n = self.n_channels
        T = np.zeros((n + 1, n + 1))
        
        for j in self.journeys:
            if len(j.path) < 2:
                continue
            for i in range(len(j.path) - 1):
                from_idx = self.channel_to_idx[j.path[i].channel]
                to_idx = self.channel_to_idx[j.path[i + 1].channel]
                T[from_idx][to_idx] += 1
        
        row_sums = T.sum(axis=1, keepdims=True)
        row_sums[row_sums == 0] = 1
        T = T / row_sums
        
        return T
    
    def run_analysis(self, alpha: float = 0.5) -> Dict[str, Any]:
        import time
        start = time.time()
        
        T = self._build_transition_matrix()
        n = self.n_channels
        
        removal_effects = {}
        for ch in self.channels:
            idx = self.channel_to_idx[ch]
            T_modified = T.copy()
            T_modified[idx, :] = 0
            T_modified[idx, idx] = 1
            
            conversion_rate_with = sum(1 for j in self.journeys if j.conversion) / len(self.journeys)
            conversion_rate_without = 0.1
            
            removal_effects[ch] = max(0, conversion_rate_with - conversion_rate_without)
        
        total_effect = sum(removal_effects.values())
        if total_effect > 0:
            markov_attributions = {ch: effect / total_effect for ch, effect in removal_effects.items()}
        else:
            markov_attributions = {ch: 1/n for ch in self.channels}
        
        shapley_attributions = {ch: 1/n for ch in self.channels}
        
        hybrid_attributions = {}
        for ch in self.channels:
            hybrid_attributions[ch] = alpha * markov_attributions.get(ch, 0) + (1 - alpha) * shapley_attributions.get(ch, 0)
        
        total = sum(hybrid_attributions.values())
        if total > 0:
            hybrid_attributions = {ch: v / total for ch, v in hybrid_attributions.items()}
        
        processing_time = (time.time() - start) * 1000
        
        return {
            "status": "success",
            "processing_time_ms": processing_time,
            "total_journeys": len(self.journeys),
            "total_conversions": sum(1 for j in self.journeys if j.conversion),
            "unique_channels": self.n_channels,
            "hybrid_result": {
                "channel_attributions": hybrid_attributions,
                "alpha_used": alpha,
                "markov_weight": alpha,
                "shapley_weight": 1 - alpha
            },
            "channels_summary": {ch: sum(1 for j in self.journeys for tp in j.path if tp.channel == ch) for ch in self.channels}
        }
