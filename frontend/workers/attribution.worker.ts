// Web Worker for attribution calculations
import { JourneyData } from '../lib/parsers';

interface AttributionResult {
  status: string;
  total_journeys: number;
  total_conversions: number;
  unique_channels: number;
  processing_time_ms: number;
  hybrid_result: {
    alpha_used: number;
    channel_attributions: { [channel: string]: number };
  };
  markov_result: {
    removal_effects: { [channel: string]: number };
  };
  shapley_result: {
    values: { [channel: string]: number };
  };
}

// Attribution Engine implementation in Web Worker
class AttributionEngine {
  private journeys: any[];
  private channels: Set<string>;
  
  constructor(journeys: JourneyData['journeys']) {
    this.journeys = journeys;
    this.channels = new Set(
      journeys.flatMap(j => j.path.map(p => p.channel))
    );
  }

  runAnalysis(alpha: number = 0.5): AttributionResult {
    const startTime = Date.now();
    
    // Run both algorithms
    const markovResults = this.calculateMarkovRemovalEffects();
    const shapleyResults = this.calculateShapleyValues();
    
    // Combine results
    const hybridResults: { [channel: string]: number } = {};
    this.channels.forEach(channel => {
      const markovValue = markovResults[channel] || 0;
      const shapleyValue = shapleyResults[channel] || 0;
      hybridResults[channel] = alpha * markovValue + (1 - alpha) * shapleyValue;
    });
    
    // Normalize to sum to 1
    const total = Object.values(hybridResults).reduce((sum, val) => sum + val, 0);
    Object.keys(hybridResults).forEach(channel => {
      hybridResults[channel] = hybridResults[channel] / total;
    });
    
    return {
      status: 'success',
      total_journeys: this.journeys.length,
      total_conversions: this.journeys.filter(j => j.conversion).length,
      unique_channels: this.channels.size,
      processing_time_ms: Date.now() - startTime,
      hybrid_result: {
        alpha_used: alpha,
        channel_attributions: hybridResults
      },
      markov_result: {
        removal_effects: markovResults
      },
      shapley_result: {
        values: shapleyResults
      }
    };
  }

  private calculateMarkovRemovalEffects(): { [channel: string]: number } {
    const transitionMatrix = this.buildTransitionMatrix();
    const removalEffects: { [channel: string]: number } = {};
    
    // Calculate baseline conversion probability
    const baselineConversionProb = this.calculateOverallConversionProbability(transitionMatrix);
    
    // Calculate removal effect for each channel
    this.channels.forEach(channel => {
      const modifiedMatrix = this.removeChannelFromMatrix(transitionMatrix, channel);
      const modifiedConversionProb = this.calculateOverallConversionProbability(modifiedMatrix);
      removalEffects[channel] = baselineConversionProb - modifiedConversionProb;
    });
    
    // Normalize
    const total = Object.values(removalEffects).reduce((sum, val) => sum + val, 0);
    Object.keys(removalEffects).forEach(channel => {
      removalEffects[channel] = removalEffects[channel] / total;
    });
    
    return removalEffects;
  }

  private calculateShapleyValues(): { [channel: string]: number } {
    const shapleyValues: { [channel: string]: number } = {};
    const channelList = Array.from(this.channels);
    
    // Simplified Shapley calculation
    channelList.forEach(channel => {
      let marginalContribution = 0;
      const permutations = this.generatePermutations(channelList.filter(c => c !== channel), channel);
      
      permutations.forEach(permutation => {
        const valueWithout = this.calculateCoalitionValue(permutation.filter(p => p !== channel));
        const valueWith = this.calculateCoalitionValue([...permutation, channel]);
        marginalContribution += (valueWith - valueWithout) / permutations.length;
      });
      
      shapleyValues[channel] = marginalContribution;
    });
    
    // Normalize
    const total = Object.values(shapleyValues).reduce((sum, val) => sum + val, 0);
    Object.keys(shapleyValues).forEach(channel => {
      shapleyValues[channel] = shapleyValues[channel] / total;
    });
    
    return shapleyValues;
  }

  private buildTransitionMatrix(): Map<string, Map<string, number>> {
    const matrix = new Map();
    
    // Initialize matrix
    this.channels.forEach(fromChannel => {
      matrix.set(fromChannel, new Map());
      this.channels.forEach(toChannel => {
        matrix.get(fromChannel)!.set(toChannel, 0);
      });
    });
    
    // Count transitions
    this.journeys.forEach(journey => {
      for (let i = 0; i < journey.path.length - 1; i++) {
        const fromChannel = journey.path[i].channel;
        const toChannel = journey.path[i + 1].channel;
        const count = matrix.get(fromChannel)?.get(toChannel) || 0;
        matrix.get(fromChannel)!.set(toChannel, count + 1);
      }
    });
    
    return matrix;
  }

  private removeChannelFromMatrix(matrix: Map<string, Map<string, number>>, channelToRemove: string): Map<string, Map<string, number>> {
    const newMatrix = new Map();
    
    this.channels.forEach(channel => {
      if (channel === channelToRemove) return;
      
      newMatrix.set(channel, new Map());
      this.channels.forEach(otherChannel => {
        if (otherChannel === channelToRemove) return;
        
        // Reroute transitions through the removed channel
        let value = 0;
        if (matrix.has(channel)) {
          // Direct transition
          value += matrix.get(channel)?.get(otherChannel) || 0;
          // Indirect transition through removed channel
          value += (matrix.get(channel)?.get(channelToRemove) || 0) * 
                   ((matrix.get(channelToRemove)?.get(otherChannel) || 0) / 
                    this.calculateTotalOutgoing(channelToRemove));
        }
        
        newMatrix.get(channel)!.set(otherChannel, value);
      });
    });
    
    return newMatrix;
  }

  private calculateOverallConversionProbability(matrix: Map<string, Map<string, number>>): number {
    // Simplified calculation - average conversion rate
    const conversionJourneys = this.journeys.filter(j => j.conversion);
    return conversionJourneys.length / this.journeys.length;
  }

  private calculateCoalitionValue(coalition: string[]): number {
    // Simplified coalition value calculation
    const coalitionSet = new Set(coalition);
    let conversionsWithCoalition = 0;
    
    this.journeys.forEach(journey => {
      const hasCoalitionChannel = journey.path.some(p => coalitionSet.has(p.channel));
      if (hasCoalitionChannel && journey.conversion) {
        conversionsWithCoalition++;
      }
    });
    
    return conversionsWithCoalition;
  }

  private generatePermutations(channels: string[], fixedChannel?: string): string[][] {
    if (channels.length <= 1) return [channels];
    
    const permutations: string[][] = [];
    for (let i = 0; i < channels.length; i++) {
      const current = channels[i];
      const remaining = channels.slice(0, i).concat(channels.slice(i + 1));
      const subPermutations = this.generatePermutations(remaining, fixedChannel);
      
      subPermutations.forEach(perm => {
        permutations.push([current, ...perm]);
      });
    }
    
    return permutations;
  }

  private calculateTotalOutgoing(channel: string): number {
    let total = 0;
    const matrix = this.buildTransitionMatrix();
    
    this.channels.forEach(otherChannel => {
      total += matrix.get(channel)?.get(otherChannel) || 0;
    });
    
    return total || 1; // Avoid division by zero
  }
}

// Handle messages from main thread
self.onmessage = function(event) {
  const { type, data } = event.data;
  
  switch (type) {
    case 'ANALYZE':
      try {
        const engine = new AttributionEngine(data.journeys);
        const result = engine.runAnalysis(data.alpha || 0.5);
        
        self.postMessage({
          type: 'SUCCESS',
          result
        });
      } catch (error) {
        self.postMessage({
          type: 'ERROR',
          error: String(error)
        });
      }
      break;
      
    default:
      console.warn('Unknown message type:', type);
  }
};

export {};