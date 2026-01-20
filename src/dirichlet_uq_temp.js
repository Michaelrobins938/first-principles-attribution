// Temporary file to hold the Dirichlet UQ implementation
// This will be inserted into attribution.js after runBootstrapUQ

/**
 * Dirichlet UQ: Sample uncertainty in transition matrix T itself
 * Uses Dirichlet posterior over transition rows given observed counts
 */
const runDirichletUQ = (rawEvents, alpha = 0.5, B = 200, dirichletPrior = 0.1, psychWeights = PSYCHOGRAPHIC_WEIGHTS) => {
    const paths = generateSimulatedPaths(rawEvents);
    const totalConversionValue = rawEvents.reduce((sum, e) => sum + e.conversion_value, 0);

    // Build baseline transition matrix to extract transition counts
    const { T: baselineT, stateToIndex } = calculateTransitionMatrix(paths, psychWeights);
    const channels = Object.keys(stateToIndex).filter(c => !['START', 'CONVERSION', 'NULL'].includes(c));

    if (channels.length === 0) {
        throw new Error('No channels found for Dirichlet UQ');
    }

    // Extract weighted transition counts per source state
    const transitionCounts = {};
    for (const state of Object.keys(stateToIndex)) {
        transitionCounts[state] = {};
        for (const nextState of Object.keys(stateToIndex)) {
            transitionCounts[state][nextState] = 0;
        }
    }

    // Count transitions with psychographic weighting
    for (const path of paths) {
        for (let i = 0; i < path.length - 1; i++) {
            const from = path[i].channel;
            const to = path[i + 1].channel;
            const weight = psychWeights[path[i].context_key] || 1.0;
            transitionCounts[from][to] += weight;
        }
    }

    // Helper: Sample from Dirichlet distribution
    // Uses Gamma variates: if X_i ~ Gamma(α_i, 1), then (X_1/S, ..., X_k/S) ~ Dirichlet(α_1,...,α_k)
    const sampleDirichlet = (alphas) => {
        const gammaVariates = alphas.map(a => {
            if (a <= 0) return 0;
            // Simple gamma sampler (Marsaglia-Tsang for shape >= 1)
            if (a < 1) {
                // For small alpha, use rejection
                let x, u;
                do {
                    x = Math.pow(Math.random(), 1 / a);
                    u = Math.random();
                } while (u > Math.exp(-x));
                return x;
            } else {
                // Marsaglia-Tsang for a >= 1
                const d = a - 1 / 3;
                const c = 1 / Math.sqrt(9 * d);
                let x, v;
                do {
                    do {
                        x = gaussianRandom();
                        v = 1 + c * x;
                    } while (v <= 0);
                    v = v * v * v;
                    const u = Math.random();
                    if (u < 1 - 0.0331 * x * x * x * x) break;
                    if (Math.log(u) < 0.5 * x * x + d * (1 - v + Math.log(v))) break;
                } while (true);
                return d * v;
            }
        });

        const sum = gammaVariates.reduce((a, b) => a + b, 0);
        return gammaVariates.map(g => sum > 0 ? g / sum : 0);
    };

    // Helper: Box-Muller for Gaussian random
    const gaussianRandom = () => {
        const u1 = Math.random();
        const u2 = Math.random();
        return Math.sqrt(-2 * Math.log(u1)) * Math.cos(2 * Math.PI * u2);
    };

    // Bootstrap iterations
    const bootstrapResults = [];
    let maxRowStochasticError = 0;
    let minEntry = Infinity;
    let maxEntry = -Infinity;

    for (let b = 0; b < B; b++) {
        // Sample T row-wise from Dirichlet posterior
        const sampledT = [];
        for (const sourceState of Object.keys(stateToIndex)) {
            const row = [];
            const counts = transitionCounts[sourceState];
            const alphas = Object.keys(stateToIndex).map(s => dirichletPrior + (counts[s] || 0));
            const probs = sampleDirichlet(alphas);

            // INVARIANT: Row-stochastic check
            const rowSum = probs.reduce((a, b) => a + b, 0);
            maxRowStochasticError = Math.max(maxRowStochasticError, Math.abs(rowSum - 1));

            // Track min/max for diagnostics
            for (const p of probs) {
                minEntry = Math.min(minEntry, p);
                maxEntry = Math.max(maxEntry, p);
            }

            sampledT.push(probs);
        }

        // Compute attribution with sampled T
        const markovEffects = {};
        const fullChannelsSet = new Set(channels);
        const pFull = calculateConversionValueV(sampledT, stateToIndex, fullChannelsSet);

        for (const channel of channels) {
            const withoutChannel = new Set(channels.filter(c => c !== channel));
            const pWithout = calculateConversionValueV(sampledT, stateToIndex, withoutChannel);
            markovEffects[channel] = pFull - pWithout;
        }

        // Normalize Markov
        const markovSum = Object.values(markovEffects).reduce((a, b) => a + b, 0);
        const markovShare = markovSum > 0 ?
            Object.fromEntries(Object.entries(markovEffects).map(([k, v]) => [k, v / markovSum])) :
            Object.fromEntries(channels.map(k => [k, 0.0]));

        // Compute Shapley (using sampled T)
        const shapleyValue = calculateShapleyValue(sampledT, stateToIndex, rawEvents);
        const shapleySum = Object.values(shapleyValue).reduce((a, b) => a + b, 0);
        const shapleyShare = shapleySum > 0 ?
            Object.fromEntries(Object.entries(shapleyValue).map(([k, v]) => [k, v / shapleySum])) :
            Object.fromEntries(channels.map(k => [k, 0.0]));

        // Hybrid
        const hybridShare = {};
        const hybridValue = {};
        for (const ch of channels) {
            const hShare = alpha * markovShare[ch] + (1.0 - alpha) * shapleyShare[ch];
            hybridShare[ch] = hShare;
            hybridValue[ch] = hShare * totalConversionValue;
        }

        // INVARIANT: Bootstrap replicate sum check
        const repSum = Object.values(hybridValue).reduce((a, b) => a + b, 0);
        assertAlmostEqual(repSum, totalConversionValue, 1e-3, `Dirichlet UQ replicate ${b} total value check violated`);

        bootstrapResults.push({ hybridShare, hybridValue });
    }

    if (bootstrapResults.length === 0) {
        throw new Error('Dirichlet UQ produced no valid results');
    }

    // Compute percentiles
    const confidenceIntervals = {};
    for (const ch of channels) {
        const values = bootstrapResults.map(r => r.hybridValue[ch] || 0);
        values.sort((a, b) => a - b);

        const getPercentile = (p) => {
            const index = Math.floor(p / 100 * values.length);
            return values[Math.min(index, values.length - 1)];
        };

        const p05 = getPercentile(5);
        const p25 = getPercentile(25);
        const p50 = getPercentile(50);
        const p75 = getPercentile(75);
        const p95 = getPercentile(95);

        // INVARIANT: Quantile ordering
        if (!(p05 <= p25 && p25 <= p50 && p50 <= p75 && p75 <= p95)) {
            throw new Error(`Quantile invariant check failed for channel ${ch}`);
        }

        const mean = values.reduce((a, b) => a + b, 0) / values.length;
        const std = Math.sqrt(values.map(v => Math.pow(v - mean, 2)).reduce((a, b) => a + b, 0) / values.length);

        confidenceIntervals[ch] = { p05, p25, p50, p75, p95, mean, std };
    }

    // Rank stability
    const rankCounts = {};
    for (const ch of channels) {
        rankCounts[ch] = Array(channels.length).fill(0);
    }

    for (const r of bootstrapResults) {
        const ranked = Object.entries(r.hybridValue)
            .sort(([, a], [, b]) => b - a)
            .map(([ch]) => ch);
        ranked.forEach((ch, rank) => rankCounts[ch][rank]++);
    }

    const rankStability = {};
    for (const ch of channels) {
        rankStability[ch] = {
            top1: rankCounts[ch][0] / bootstrapResults.length,
            top2: (rankCounts[ch][0] + rankCounts[ch][1]) / bootstrapResults.length
        };
    }

    return {
        type: 'uq_transition_dirichlet',
        version: '1.0.0',
        B: B,
        alpha: alpha,
        dirichlet_prior: dirichletPrior,
        uq_target: 'transition_matrix',
        posterior: 'dirichlet_rowwise',
        counts_semantics: 'weighted_pseudocounts',
        confidence_intervals: confidenceIntervals,
        rank_stability: rankStability,
        total_conversion_value: totalConversionValue,
        generated_at: new Date().toISOString(),
        seed: Date.now(),
        method: 'transition_dirichlet',
        row_stochastic_max_abs_error: maxRowStochasticError,
        min_entry: minEntry === Infinity ? 0 : minEntry,
        max_entry: maxEntry === -Infinity ? 0 : maxEntry
    };
};
