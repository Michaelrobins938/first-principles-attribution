#!/usr/bin/env node
/**
 * Behavioral Profiling Analyzer for ChatGPT Data
 * 
 * Applies psychographic profiling framework to ChatGPT conversation data
 * to extract behavioral patterns, motivations, fears, desires, and triggers.
 * 
 * Generates Portfolio-Ready Deliverables:
 * - Search Behavior Map
 * - Content Resonance Profile
 * - Behavioral Rhythm Chart
 * - Behavior Loop Diagram
 * - Interest Constellation Map
 * - Motivation Drivers Sheet
 * - Fear Barriers Map
 * - Desire Archetype Summary
 * - Trigger Activation Chart
 * - Buying Psychology Blueprint
 * 
 * Usage: node behavioral-profiling-analyzer.js
 */

const fs = require('fs');
const path = require('path');

// ============================================================================
// CONFIGURATION
// ============================================================================

const CONFIG = {
    INPUT_FILES: {
        conversations: path.join(__dirname, 'Data', 'conversations.json'),
        enrichedEvents: path.join(__dirname, 'Data', 'enriched-events.json'),
    },
    OUTPUT_DIR: path.join(__dirname, 'Behavioral-Profile'),
    DELIVERABLES: {
        searchBehaviorMap: 'Search-Behavior-Map.json',
        contentResonance: 'Content-Resonance-Profile.json',
        behavioralRhythm: 'Behavioral-Rhythm-Chart.json',
        behaviorLoops: 'Behavior-Loop-Diagram.json',
        interestConstellation: 'Interest-Constellation-Map.json',
        motivationDrivers: 'Motivation-Drivers-Sheet.json',
        fearBarriers: 'Fear-Barriers-Map.json',
        desireArchetypes: 'Desire-Archetype-Summary.json',
        triggerActivation: 'Trigger-Activation-Chart.json',
        buyingPsychology: 'Buying-Psychology-Blueprint.json',
        fullProfile: 'Full-Behavioral-Profile.json',
        visualSummary: 'Visual-Summary-Report.md',
    }
};

// Create output directory
if (!fs.existsSync(CONFIG.OUTPUT_DIR)) {
    fs.mkdirSync(CONFIG.OUTPUT_DIR, { recursive: true });
}

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

/**
 * Extract topic keywords from title
 */
function extractTopicKeywords(title) {
    const titleLower = (title || '').toLowerCase();

    // Remove common words
    const stopWords = new Set(['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'should', 'could', 'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'what', 'which', 'who', 'when', 'where', 'why', 'how']);

    const words = titleLower
        .replace(/[^\w\s]/g, ' ')
        .split(/\s+/)
        .filter(w => w.length > 2 && !stopWords.has(w));

    return words;
}

/**
 * Detect problem-solving queries
 */
function isProblemSolving(title) {
    const problemPatterns = /fix|error|issue|problem|help|debug|troubleshoot|solve|broken|not working|failed|wrong|incorrect/i;
    return problemPatterns.test(title || '');
}

/**
 * Detect learning/research queries  
 */
function isLearning(title) {
    const learningPatterns = /how to|explain|understand|learn|what is|why|tutorial|guide|example|teach me|introduction/i;
    return learningPatterns.test(title || '');
}

/**
 * Detect creative/generative queries
 */
function isCreative(title) {
    const creativePatterns = /create|generate|make|design|build|write|compose|draft|idea|brainstorm|suggest/i;
    return creativePatterns.test(title || '');
}

/**
 * Detect aspirational content
 */
function isAspirational(title) {
    const aspirationalPatterns = /best|top|advanced|professional|expert|master|ultimate|complete|comprehensive|perfect/i;
    return aspirationalPatterns.test(title || '');
}

/**
 * Detect anxiety/stress signals
 */
function isAnxietySignal(title) {
    const anxietyPatterns = /urgent|asap|quick|fast|help|critical|emergency|important|deadline|stuck|lost|confused/i;
    return anxietyPatterns.test(title || '');
}

/**
 * Categorize topic into interest cluster
 */
function categorizeTopic(title) {
    const titleLower = (title || '').toLowerCase();

    const clusters = {
        'Technology & AI': /ai|artificial intelligence|machine learning|neural|gpt|model|algorithm|tech|code|programming|software|api|data|automation/i,
        'Business & Entrepreneurship': /business|startup|entrepreneur|marketing|sales|revenue|customer|strategy|growth|product|market/i,
        'Creative & Design': /design|art|creative|image|photo|video|visual|ui|ux|brand|aesthetic|style/i,
        'Personal Development': /learn|improve|productivity|habit|goal|motivation|mindset|self|personal|growth|development/i,
        'Health & Wellness': /health|fitness|wellness|exercise|sleep|nutrition|mental|stress|anxiety|meditation/i,
        'Finance & Investment': /finance|money|invest|trading|stock|crypto|wealth|passive income|financial/i,
        'Writing & Content': /write|writing|content|blog|article|copy|storytelling|narrative|essay|book/i,
        'Problem Solving & Analysis': /analyze|problem|solve|debug|fix|issue|troubleshoot|optimize|improve|evaluate/i,
        'Research & Learning': /research|study|understand|explain|learn|education|academic|theory|concept|science/i,
        'General & Exploratory': /general|chat|conversation|question|curious|explore|wonder|think/i,
    };

    for (const [cluster, pattern] of Object.entries(clusters)) {
        if (pattern.test(titleLower)) {
            return cluster;
        }
    }

    return 'Other';
}

/**
 * Detect "rabbit hole" sequences (successive deep dives)
 */
function findRabbitHoles(conversations, windowHours = 3) {
    const sequences = [];
    const windowMs = windowHours * 60 * 60 * 1000;

    for (let i = 0; i < conversations.length - 2; i++) {
        const conv1 = conversations[i];
        const conv2 = conversations[i + 1];
        const conv3 = conversations[i + 2];

        const time1 = conv1.create_time * 1000;
        const time2 = conv2.create_time * 1000;
        const time3 = conv3.create_time * 1000;

        // Check if all 3 are within window
        if (time3 - time1 <= windowMs) {
            // Check if they're on similar topics
            const topic1 = categorizeTopic(conv1.title);
            const topic2 = categorizeTopic(conv2.title);
            const topic3 = categorizeTopic(conv3.title);

            if (topic1 === topic2 && topic2 === topic3) {
                sequences.push({
                    topic: topic1,
                    start_time: time1,
                    conversations: [conv1.title, conv2.title, conv3.title],
                    duration_minutes: Math.round((time3 - time1) / (60 * 1000)),
                });
            }
        }
    }

    return sequences;
}

// ============================================================================
// PHASE 1: BEHAVIORAL DATA EXTRACTION
// ============================================================================

/**
 * 1. Search Behavior Map
 * Equivalent to "Google Search History" analysis
 */
function buildSearchBehaviorMap(conversations) {
    console.log('📊 Building Search Behavior Map...');

    const topicFrequency = {};
    const recurringThemes = {};
    const problemSolvingQueries = [];
    const learningQueries = [];
    const creativeQueries = [];
    const rabbitHoles = findRabbitHoles(conversations);

    conversations.forEach(conv => {
        const title = conv.title || '';
        const topic = categorizeTopic(title);
        const keywords = extractTopicKeywords(title);

        // Topic frequency
        topicFrequency[topic] = (topicFrequency[topic] || 0) + 1;

        // Keyword frequency
        keywords.forEach(kw => {
            recurringThemes[kw] = (recurringThemes[kw] || 0) + 1;
        });

        // Query types
        if (isProblemSolving(title)) {
            problemSolvingQueries.push({ title, timestamp: conv.create_time });
        }
        if (isLearning(title)) {
            learningQueries.push({ title, timestamp: conv.create_time });
        }
        if (isCreative(title)) {
            creativeQueries.push({ title, timestamp: conv.create_time });
        }
    });

    // Sort and get top themes
    const topThemes = Object.entries(recurringThemes)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 50)
        .map(([keyword, count]) => ({ keyword, count }));

    const topTopics = Object.entries(topicFrequency)
        .sort((a, b) => b[1] - a[1])
        .map(([topic, count]) => ({ topic, count, percentage: ((count / conversations.length) * 100).toFixed(1) }));

    return {
        total_queries: conversations.length,
        top_topics: topTopics,
        top_themes: topThemes,
        query_types: {
            problem_solving: {
                count: problemSolvingQueries.length,
                percentage: ((problemSolvingQueries.length / conversations.length) * 100).toFixed(1),
                examples: problemSolvingQueries.slice(0, 10).map(q => q.title),
            },
            learning: {
                count: learningQueries.length,
                percentage: ((learningQueries.length / conversations.length) * 100).toFixed(1),
                examples: learningQueries.slice(0, 10).map(q => q.title),
            },
            creative: {
                count: creativeQueries.length,
                percentage: ((creativeQueries.length / conversations.length) * 100).toFixed(1),
                examples: creativeQueries.slice(0, 10).map(q => q.title),
            },
        },
        rabbit_holes: rabbitHoles,
        insights: {
            curiosity_pattern: topTopics[0]?.topic || 'Unknown',
            learning_style: learningQueries.length > problemSolvingQueries.length ? 'Exploratory Learner' : 'Problem-Driven Learner',
            primary_use_case: topTopics[0]?.topic || 'Unknown',
        }
    };
}

/**
 * 2. Content Resonance Profile
 * What topics you engage with most deeply
 */
function buildContentResonanceProfile(conversations) {
    console.log('📊 Building Content Resonance Profile...');

    const topicEngagement = {};
    const modelPreferences = {};

    conversations.forEach(conv => {
        const topic = categorizeTopic(conv.title);
        const model = conv.current_model || 'UNKNOWN';
        const mapping = conv.mapping ? Object.values(conv.mapping) : [];
        const turnCount = mapping.filter(m => m.message?.author?.role === 'user').length;

        // Track engagement by topic
        if (!topicEngagement[topic]) {
            topicEngagement[topic] = {
                conversation_count: 0,
                total_turns: 0,
                avg_turns: 0,
                high_engagement_count: 0,
            };
        }

        topicEngagement[topic].conversation_count++;
        topicEngagement[topic].total_turns += turnCount;
        topicEngagement[topic].avg_turns = topicEngagement[topic].total_turns / topicEngagement[topic].conversation_count;

        if (turnCount >= 5) {
            topicEngagement[topic].high_engagement_count++;
        }

        // Model preferences
        modelPreferences[model] = (modelPreferences[model] || 0) + 1;
    });

    const topicRanking = Object.entries(topicEngagement)
        .map(([topic, data]) => ({
            topic,
            ...data,
            engagement_rate: ((data.high_engagement_count / data.conversation_count) * 100).toFixed(1) + '%',
        }))
        .sort((a, b) => b.avg_turns - a.avg_turns);

    return {
        topic_engagement: topicRanking,
        model_preferences: Object.entries(modelPreferences)
            .sort((a, b) => b[1] - a[1])
            .map(([model, count]) => ({ model, count })),
        insights: {
            preferred_learning_medium: 'Conversational AI (ChatGPT)',
            most_engaging_topic: topicRanking[0]?.topic || 'Unknown',
            emotional_driver: topicRanking[0]?.topic.includes('Problem') ? 'Problem-solving' : 'Learning & Growth',
        }
    };
}

/**
 * 3. Behavioral Rhythm Chart
 * Time-based activity patterns
 */
function buildBehavioralRhythmChart(conversations) {
    console.log('📊 Building Behavioral Rhythm Chart...');

    const hourOfDay = Array(24).fill(0);
    const dayOfWeek = Array(7).fill(0);
    const monthOfYear = Array(12).fill(0);

    const dayNames = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
    const monthNames = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];

    conversations.forEach(conv => {
        const date = new Date(conv.create_time * 1000);
        hourOfDay[date.getHours()]++;
        dayOfWeek[date.getDay()]++;
        monthOfYear[date.getMonth()]++;
    });

    // Find peak hours
    const peakHour = hourOfDay.indexOf(Math.max(...hourOfDay));
    const peakDay = dayOfWeek.indexOf(Math.max(...dayOfWeek));

    // Classify user type
    const nightActivity = hourOfDay.slice(22, 24).concat(hourOfDay.slice(0, 6)).reduce((a, b) => a + b, 0);
    const morningActivity = hourOfDay.slice(6, 12).reduce((a, b) => a + b, 0);
    const afternoonActivity = hourOfDay.slice(12, 18).reduce((a, b) => a + b, 0);
    const eveningActivity = hourOfDay.slice(18, 22).reduce((a, b) => a + b, 0);

    const totalActivity = nightActivity + morningActivity + afternoonActivity + eveningActivity;

    let userType = 'Balanced';
    if (nightActivity / totalActivity > 0.35) userType = 'Night Owl';
    else if (morningActivity / totalActivity > 0.35) userType = 'Morning Person';
    else if (afternoonActivity / totalActivity > 0.35) userType = 'Afternoon Worker';

    // Weekend vs weekday
    const weekendActivity = dayOfWeek[0] + dayOfWeek[6];
    const weekdayActivity = dayOfWeek.slice(1, 6).reduce((a, b) => a + b, 0);

    return {
        hour_of_day: hourOfDay.map((count, hour) => ({
            hour: `${hour}:00`,
            count,
            percentage: ((count / conversations.length) * 100).toFixed(1),
        })),
        day_of_week: dayOfWeek.map((count, day) => ({
            day: dayNames[day],
            count,
            percentage: ((count / conversations.length) * 100).toFixed(1),
        })),
        month_of_year: monthOfYear.map((count, month) => ({
            month: monthNames[month],
            count,
        })),
        insights: {
            user_type: userType,
            peak_hour: `${peakHour}:00 - ${peakHour + 1}:00`,
            peak_day: dayNames[peakDay],
            weekend_vs_weekday: weekendActivity > weekdayActivity ? 'More active on weekends' : 'More active on weekdays',
            activity_distribution: {
                night: `${((nightActivity / totalActivity) * 100).toFixed(1)}%`,
                morning: `${((morningActivity / totalActivity) * 100).toFixed(1)}%`,
                afternoon: `${((afternoonActivity / totalActivity) * 100).toFixed(1)}%`,
                evening: `${((eveningActivity / totalActivity) * 100).toFixed(1)}%`,
            }
        }
    };
}

/**
 * 4. Behavior Loop Diagram
 * What pulls you in, keeps you engaged, and ends cycles
 */
function buildBehaviorLoopDiagram(conversations) {
    console.log('📊 Building Behavior Loop Diagram...');

    // Identify sessions (conversations within 30 min)
    const sessions = [];
    let currentSession = [];

    const sortedConvs = [...conversations].sort((a, b) => a.create_time - b.create_time);

    sortedConvs.forEach((conv, i) => {
        if (i === 0) {
            currentSession = [conv];
        } else {
            const prevTime = sortedConvs[i - 1].create_time * 1000;
            const currTime = conv.create_time * 1000;

            if (currTime - prevTime <= 30 * 60 * 1000) {
                currentSession.push(conv);
            } else {
                if (currentSession.length > 0) {
                    sessions.push(currentSession);
                }
                currentSession = [conv];
            }
        }
    });

    if (currentSession.length > 0) {
        sessions.push(currentSession);
    }

    // Analyze loops
    const loopStarts = {};
    const loopEnds = {};
    const avgSessionLength = sessions.reduce((sum, s) => sum + s.length, 0) / sessions.length;

    sessions.forEach(session => {
        if (session.length > 0) {
            const startTopic = categorizeTopic(session[0].title);
            const endTopic = categorizeTopic(session[session.length - 1].title);

            loopStarts[startTopic] = (loopStarts[startTopic] || 0) + 1;
            loopEnds[endTopic] = (loopEnds[endTopic] || 0) + 1;
        }
    });

    return {
        total_sessions: sessions.length,
        avg_conversations_per_session: avgSessionLength.toFixed(2),
        loop_triggers: Object.entries(loopStarts)
            .sort((a, b) => b[1] - a[1])
            .map(([topic, count]) => ({ topic, count })),
        loop_endings: Object.entries(loopEnds)
            .sort((a, b) => b[1] - a[1])
            .map(([topic, count]) => ({ topic, count })),
        insights: {
            primary_trigger: Object.entries(loopStarts).sort((a, b) => b[1] - a[1])[0]?.[0] || 'Unknown',
            typical_session_length: `${Math.round(avgSessionLength)} conversations`,
            engagement_pattern: avgSessionLength > 3 ? 'Deep Engagement Sessions' : 'Quick Query Sessions',
        }
    };
}

/**
 * 5. Interest Constellation Map
 * Major interest clusters
 */
function buildInterestConstellationMap(conversations) {
    console.log('📊 Building Interest Constellation Map...');

    const topicFrequency = {};
    const topicConnections = {};

    conversations.forEach(conv => {
        const topic = categorizeTopic(conv.title);
        topicFrequency[topic] = (topicFrequency[topic] || 0) + 1;
    });

    // Find connections (topics that appear in same sessions)
    const sortedConvs = [...conversations].sort((a, b) => a.create_time - b.create_time);

    for (let i = 0; i < sortedConvs.length - 1; i++) {
        const conv1 = sortedConvs[i];
        const conv2 = sortedConvs[i + 1];

        const time1 = conv1.create_time * 1000;
        const time2 = conv2.create_time * 1000;

        if (time2 - time1 <= 30 * 60 * 1000) {
            const topic1 = categorizeTopic(conv1.title);
            const topic2 = categorizeTopic(conv2.title);

            if (topic1 !== topic2) {
                const connection = `${topic1} → ${topic2}`;
                topicConnections[connection] = (topicConnections[connection] || 0) + 1;
            }
        }
    }

    const clusters = Object.entries(topicFrequency)
        .sort((a, b) => b[1] - a[1])
        .map(([topic, count]) => ({
            topic,
            count,
            percentage: ((count / conversations.length) * 100).toFixed(1) + '%',
            size: count > 500 ? 'Core' : count > 100 ? 'Major' : 'Minor',
        }));

    const topConnections = Object.entries(topicConnections)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 15)
        .map(([connection, count]) => ({ connection, count }));

    return {
        clusters,
        connections: topConnections,
        insights: {
            core_interests: clusters.filter(c => c.size === 'Core').map(c => c.topic),
            interest_diversity: `${clusters.length} distinct interest areas`,
            strongest_connection: topConnections[0]?.connection || 'None',
        }
    };
}

// ============================================================================
// PHASE 2: PSYCHOGRAPHIC FRAMEWORK
// ============================================================================

/**
 * 6. Motivation Drivers Sheet
 */
function buildMotivationDriversSheet(conversations, searchBehaviorMap) {
    console.log('📊 Building Motivation Drivers Sheet...');

    const motivations = {
        Growth: 0,
        Problem_Solving: 0,
        Creativity: 0,
        Optimization: 0,
        Learning: 0,
        Achievement: 0,
    };

    conversations.forEach(conv => {
        const title = conv.title || '';

        if (isLearning(title)) motivations.Learning++;
        if (isProblemSolving(title)) motivations.Problem_Solving++;
        if (isCreative(title)) motivations.Creativity++;
        if (isAspirational(title)) motivations.Achievement++;
        if (/optimize|improve|better|enhance|upgrade/i.test(title)) motivations.Optimization++;
        if (/grow|scale|expand|develop|build/i.test(title)) motivations.Growth++;
    });

    const total = Object.values(motivations).reduce((a, b) => a + b, 0);
    const motivationRanking = Object.entries(motivations)
        .map(([motivation, count]) => ({
            motivation,
            count,
            percentage: ((count / total) * 100).toFixed(1) + '%',
        }))
        .sort((a, b) => b.count - a.count);

    return {
        primary_motivation: motivationRanking[0]?.motivation || 'Unknown',
        motivation_breakdown: motivationRanking,
        insights: {
            dominant_driver: motivationRanking[0]?.motivation || 'Unknown',
            secondary_driver: motivationRanking[1]?.motivation || 'Unknown',
            motivation_style: motivationRanking[0]?.motivation === 'Problem_Solving' ?
                'Reactive (Problem-driven)' : 'Proactive (Goal-driven)',
        }
    };
}

/**
 * 7. Fear Barriers Map
 * Inferred from anxiety signals and over-researching patterns
 */
function buildFearBarriersMap(conversations) {
    console.log('📊 Building Fear Barriers Map...');

    const anxietySignals = [];
    const repeatedTopics = {};

    conversations.forEach(conv => {
        const title = conv.title || '';
        const topic = categorizeTopic(title);

        if (isAnxietySignal(title)) {
            anxietySignals.push({
                title,
                timestamp: conv.create_time,
                topic,
            });
        }

        repeatedTopics[topic] = (repeatedTopics[topic] || 0) + 1;
    });

    // Over-researched topics (potential fear areas)
    const overResearchedTopics = Object.entries(repeatedTopics)
        .filter(([topic, count]) => count > 50)
        .sort((a, b) => b[1] - a[1])
        .map(([topic, count]) => ({ topic, count }));

    const inferredFears = {
        'Technical Failure': anxietySignals.filter(s => s.topic.includes('Technology')).length,
        'Time Pressure': anxietySignals.filter(s => /urgent|deadline|quick/i.test(s.title)).length,
        'Competence Gap': anxietySignals.filter(s => s.topic.includes('Learning')).length,
        'Decision Paralysis': overResearchedTopics.length > 3 ? overResearchedTopics.length : 0,
    };

    return {
        anxiety_signals: {
            total_count: anxietySignals.length,
            percentage: ((anxietySignals.length / conversations.length) * 100).toFixed(1) + '%',
            examples: anxietySignals.slice(0, 10).map(s => s.title),
        },
        over_researched_topics: overResearchedTopics,
        inferred_fears: Object.entries(inferredFears)
            .filter(([_, count]) => count > 0)
            .sort((a, b) => b[1] - a[1])
            .map(([fear, intensity]) => ({ fear, intensity })),
        insights: {
            primary_fear: Object.entries(inferredFears).sort((a, b) => b[1] - a[1])[0]?.[0] || 'None detected',
            research_depth: overResearchedTopics.length > 3 ? 'Deep researcher (potential analysis paralysis)' : 'Decisive',
        }
    };
}

/**
 * 8. Desire Archetype Summary
 * What you keep revisiting and aspire to
 */
function buildDesireArchetypeSummary(conversations) {
    console.log('📊 Building Desire Archetype Summary...');

    const aspirationalContent = [];
    const recurringInterests = {};

    conversations.forEach(conv => {
        const title = conv.title || '';
        const topic = categorizeTopic(title);

        if (isAspirational(title)) {
            aspirationalContent.push({ title, topic, timestamp: conv.create_time });
        }

        recurringInterests[topic] = (recurringInterests[topic] || 0) + 1;
    });

    const desireArchetypes = {
        'Mastery': aspirationalContent.filter(a => /expert|master|advanced|professional/i.test(a.title)).length,
        'Innovation': aspirationalContent.filter(a => /new|innovative|cutting-edge|latest/i.test(a.title)).length,
        'Efficiency': aspirationalContent.filter(a => /optimize|automate|streamline|efficient/i.test(a.title)).length,
        'Success': aspirationalContent.filter(a => /successful|win|achieve|best/i.test(a.title)).length,
    };

    const topRecurringInterests = Object.entries(recurringInterests)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 5)
        .map(([topic, count]) => ({ topic, count, persistence: count > 50 ? 'High' : 'Medium' }));

    return {
        aspirational_content: {
            total_count: aspirationalContent.length,
            percentage: ((aspirationalContent.length / conversations.length) * 100).toFixed(1) + '%',
            top_examples: aspirationalContent.slice(0, 10).map(a => a.title),
        },
        recurring_interests: topRecurringInterests,
        desire_archetypes: Object.entries(desireArchetypes)
            .filter(([_, count]) => count > 0)
            .sort((a, b) => b[1] - a[1])
            .map(([archetype, intensity]) => ({ archetype, intensity })),
        insights: {
            primary_desire: Object.entries(desireArchetypes).sort((a, b) => b[1] - a[1])[0]?.[0] || 'Growth',
            aspiration_level: aspirationalContent.length > conversations.length * 0.2 ? 'High Achiever' : 'Pragmatic',
        }
    };
}

/**
 * 9. Trigger Activation Chart
 * What causes you to engage
 */
function buildTriggerActivationChart(conversations, behavioralRhythm) {
    console.log('📊 Building Trigger Activation Chart...');

    const triggers = {
        'Time-Based': {
            peak_hours: behavioralRhythm.insights.peak_hour,
            pattern: behavioralRhythm.insights.user_type,
        },
        'Problem-Triggered': {
            count: conversations.filter(c => isProblemSolving(c.title)).length,
            percentage: ((conversations.filter(c => isProblemSolving(c.title)).length / conversations.length) * 100).toFixed(1) + '%',
        },
        'Learning-Triggered': {
            count: conversations.filter(c => isLearning(c.title)).length,
            percentage: ((conversations.filter(c => isLearning(c.title)).length / conversations.length) * 100).toFixed(1) + '%',
        },
        'Creative-Triggered': {
            count: conversations.filter(c => isCreative(c.title)).length,
            percentage: ((conversations.filter(c => isCreative(c.title)).length / conversations.length) * 100).toFixed(1) + '%',
        },
    };

    return {
        triggers,
        insights: {
            primary_trigger: 'Problem-solving needs',
            activation_pattern: behavioralRhythm.insights.user_type,
            engagement_style: triggers['Problem-Triggered'].count > triggers['Learning-Triggered'].count ?
                'Reactive (problem-driven)' : 'Proactive (curiosity-driven)',
        }
    };
}

/**
 * 10. Buying Psychology Blueprint
 * Decision-making patterns and conversion signals
 */
function buildBuyingPsychologyBlueprint(conversations) {
    console.log('📊 Building Buying Psychology Blueprint...');

    // ChatGPT context: "buying" = model upgrades, high-engagement decisions
    const highEngagementConvs = conversations.filter(conv => {
        const mapping = conv.mapping ? Object.values(conv.mapping) : [];
        const turns = mapping.filter(m => m.message?.author?.role === 'user').length;
        return turns >= 5;
    });

    const researchDepth = {
        'Quick Decision': conversations.filter(c => {
            const mapping = c.mapping ? Object.values(c.mapping) : [];
            return mapping.filter(m => m.message?.author?.role === 'user').length <= 2;
        }).length,
        'Moderate Research': conversations.filter(c => {
            const mapping = c.mapping ? Object.values(c.mapping) : [];
            const turns = mapping.filter(m => m.message?.author?.role === 'user').length;
            return turns > 2 && turns < 5;
        }).length,
        'Deep Research': highEngagementConvs.length,
    };

    return {
        decision_style: Object.entries(researchDepth).sort((a, b) => b[1] - a[1])[0]?.[0] || 'Moderate Research',
        research_depth: Object.entries(researchDepth)
            .map(([style, count]) => ({
                style,
                count,
                percentage: ((count / conversations.length) * 100).toFixed(1) + '%',
            })),
        conversion_signals: {
            high_engagement_topics: [...new Set(highEngagementConvs.map(c => categorizeTopic(c.title)))]
                .slice(0, 5),
            engagement_rate: ((highEngagementConvs.length / conversations.length) * 100).toFixed(1) + '%',
        },
        insights: {
            buyer_type: researchDepth['Deep Research'] > researchDepth['Quick Decision'] ?
                'Analytical Buyer (deep research before commitment)' :
                'Decisive Buyer (quick decisions)',
            commitment_level: highEngagementConvs.length > conversations.length * 0.3 ? 'High' : 'Medium',
        }
    };
}

// ============================================================================
// MAIN ANALYSIS
// ============================================================================

async function runBehavioralProfiling() {
    console.log('🧠 Behavioral Profiling Analyzer Starting...\n');

    // Load conversations
    console.log('📂 Loading conversation data...');
    const rawConversations = JSON.parse(fs.readFileSync(CONFIG.INPUT_FILES.conversations, 'utf-8'));
    console.log(`✅ Loaded ${rawConversations.length} conversations\n`);

    // Filter valid conversations
    const conversations = rawConversations.filter(c => c.create_time && c.title);

    console.log('🔍 Generating Behavioral Profile Deliverables...\n');

    // PHASE 1: Behavioral Data
    const searchBehaviorMap = buildSearchBehaviorMap(conversations);
    const contentResonance = buildContentResonanceProfile(conversations);
    const behavioralRhythm = buildBehavioralRhythmChart(conversations);
    const behaviorLoops = buildBehaviorLoopDiagram(conversations);
    const interestConstellation = buildInterestConstellationMap(conversations);

    // PHASE 2: Psychographic Framework
    const motivationDrivers = buildMotivationDriversSheet(conversations, searchBehaviorMap);
    const fearBarriers = buildFearBarriersMap(conversations);
    const desireArchetypes = buildDesireArchetypeSummary(conversations);
    const triggerActivation = buildTriggerActivationChart(conversations, behavioralRhythm);
    const buyingPsychology = buildBuyingPsychologyBlueprint(conversations);

    // Build Full Profile
    const fullProfile = {
        generated_at: new Date().toISOString(),
        profile_summary: {
            total_conversations: conversations.length,
            date_range: {
                first: new Date(Math.min(...conversations.map(c => c.create_time)) * 1000).toISOString(),
                last: new Date(Math.max(...conversations.map(c => c.create_time)) * 1000).toISOString(),
            },
            primary_interest: searchBehaviorMap.insights.curiosity_pattern,
            user_type: behavioralRhythm.insights.user_type,
            motivation_style: motivationDrivers.insights.dominant_driver,
            decision_style: buyingPsychology.insights.buyer_type,
        },
        behavioral_data: {
            search_behavior_map: searchBehaviorMap,
            content_resonance: contentResonance,
            behavioral_rhythm: behavioralRhythm,
            behavior_loops: behaviorLoops,
            interest_constellation: interestConstellation,
        },
        psychographic_framework: {
            motivation_drivers: motivationDrivers,
            fear_barriers: fearBarriers,
            desire_archetypes: desireArchetypes,
            trigger_activation: triggerActivation,
            buying_psychology: buyingPsychology,
        },
    };

    // Save all deliverables
    console.log('\n💾 Saving deliverables...\n');

    const deliverables = [
        [CONFIG.DELIVERABLES.searchBehaviorMap, searchBehaviorMap],
        [CONFIG.DELIVERABLES.contentResonance, contentResonance],
        [CONFIG.DELIVERABLES.behavioralRhythm, behavioralRhythm],
        [CONFIG.DELIVERABLES.behaviorLoops, behaviorLoops],
        [CONFIG.DELIVERABLES.interestConstellation, interestConstellation],
        [CONFIG.DELIVERABLES.motivationDrivers, motivationDrivers],
        [CONFIG.DELIVERABLES.fearBarriers, fearBarriers],
        [CONFIG.DELIVERABLES.desireArchetypes, desireArchetypes],
        [CONFIG.DELIVERABLES.triggerActivation, triggerActivation],
        [CONFIG.DELIVERABLES.buyingPsychology, buyingPsychology],
        [CONFIG.DELIVERABLES.fullProfile, fullProfile],
    ];

    deliverables.forEach(([filename, data]) => {
        const filepath = path.join(CONFIG.OUTPUT_DIR, filename);
        fs.writeFileSync(filepath, JSON.stringify(data, null, 2));
        console.log(`✅ Saved ${filename}`);
    });

    // Generate visual summary report
    const visualSummary = generateVisualSummary(fullProfile);
    fs.writeFileSync(path.join(CONFIG.OUTPUT_DIR, CONFIG.DELIVERABLES.visualSummary), visualSummary);
    console.log(`✅ Saved ${CONFIG.DELIVERABLES.visualSummary}`);

    console.log('\n🎉 Behavioral Profiling Complete!\n');
    console.log('📊 Generated Deliverables:');
    console.log('   ✓ Search Behavior Map');
    console.log('   ✓ Content Resonance Profile');
    console.log('   ✓ Behavioral Rhythm Chart');
    console.log('   ✓ Behavior Loop Diagram');
    console.log('   ✓ Interest Constellation Map');
    console.log('   ✓ Motivation Drivers Sheet');
    console.log('   ✓ Fear Barriers Map');
    console.log('   ✓ Desire Archetype Summary');
    console.log('   ✓ Trigger Activation Chart');
    console.log('   ✓ Buying Psychology Blueprint');
    console.log('   ✓ Full Behavioral Profile');
    console.log('   ✓ Visual Summary Report');

    console.log(`\n📁 All files saved to: ${CONFIG.OUTPUT_DIR}\n`);
    console.log('💼 These deliverables are portfolio-ready!');
    console.log('🎯 Use them to demonstrate your psychographic profiling skills.\n');
}

function generateVisualSummary(profile) {
    return `# Behavioral Profile - Visual Summary

**Generated:** ${profile.generated_at}  
**Analysis Period:** ${profile.profile_summary.date_range.first.split('T')[0]} to ${profile.profile_summary.date_range.last.split('T')[0]}  
**Total Conversations:** ${profile.profile_summary.total_conversations}

---

## 👤 Profile Overview

**Primary Interest:** ${profile.profile_summary.primary_interest}  
**User Type:** ${profile.profile_summary.user_type}  
**Motivation Style:** ${profile.profile_summary.motivation_style}  
**Decision Style:** ${profile.profile_summary.decision_style}

---

## 🎯 Top 5 Interest Areas

${profile.behavioral_data.interest_constellation.clusters.slice(0, 5).map((c, i) =>
        `${i + 1}. **${c.topic}** - ${c.count} conversations (${c.percentage})`
    ).join('\n')}

---

## 🧠 Motivation Breakdown

${profile.psychographic_framework.motivation_drivers.motivation_breakdown.slice(0, 3).map((m, i) =>
        `${i + 1}. **${m.motivation}** - ${m.percentage}`
    ).join('\n')}

---

## ⏰ Activity Patterns

**Peak Activity:** ${profile.behavioral_data.behavioral_rhythm.insights.peak_hour}  
**Most Active Day:** ${profile.behavioral_data.behavioral_rhythm.insights.peak_day}  
**Activity Distribution:**
- Morning: ${profile.behavioral_data.behavioral_rhythm.insights.activity_distribution.morning}
- Afternoon: ${profile.behavioral_data.behavioral_rhythm.insights.activity_distribution.afternoon}
- Evening: ${profile.behavioral_data.behavioral_rhythm.insights.activity_distribution.evening}
- Night: ${profile.behavioral_data.behavioral_rhythm.insights.activity_distribution.night}

---

## 🔄 Engagement Patterns

**Primary Trigger:** ${profile.psychographic_framework.trigger_activation.insights.primary_trigger}  
**Engagement Style:** ${profile.psychographic_framework.trigger_activation.insights.engagement_style}  
**Average Session:** ${profile.behavioral_data.behavior_loops.insights.typical_session_length}

---

## 💡 Key Insights

**Learning Style:** ${profile.behavioral_data.search_behavior_map.insights.learning_style}  
**Primary Use Case:** ${profile.behavioral_data.search_behavior_map.insights.primary_use_case}  
**Aspiration Level:** ${profile.psychographic_framework.desire_archetypes.insights.aspiration_level}  
**Research Depth:** ${profile.psychographic_framework.fear_barriers.insights.research_depth}

---

## 📈 Portfolio Use Cases

This behavioral profile demonstrates expertise in:

1. **Data-Driven Persona Development**
2. **Psychographic Segmentation**
3. **Behavioral Pattern Recognition**
4. **Predictive User Modeling**
5. **Strategic Marketing Insights**

Perfect for:
- UX Research positions
- Marketing Strategy roles
- Data Analysis projects
- Behavioral Psychology applications
- Product Management portfolios
`;
}

// Run the analysis
runBehavioralProfiling().catch(err => {
    console.error(' Error during profiling:', err);
    process.exit(1);
});
