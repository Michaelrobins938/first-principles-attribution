#!/usr/bin/env node
/**
 * Enhanced Data Parser for Attribution Analytics
 * 
 * This script extracts DEEP insights and determinant UIDs from raw ChatGPT data:
 * - Session clustering & user journey UID generation
 * - Behavioral pattern extraction (message velocity, topic shifts)
 * - Sentiment & feedback integration
 * - Multi-dimensional context modeling
 * - Temporal & sequential features
 * - Model transition analysis
 * 
 * Usage: node enhanced-data-parser.js
 */

const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

// ============================================================================
// CONFIGURATION
// ============================================================================

const CONFIG = {
    INPUT_FILES: {
        conversations: path.join(__dirname, 'Data', 'conversations.json'),
        feedback: path.join(__dirname, 'Data', 'message_feedback.json'),
        user: path.join(__dirname, 'Data', 'user.json'),
        modelRecs: path.join(__dirname, 'Data', '/model-recommendations.json')
    },
    OUTPUT_FILES: {
        enrichedEvents: path.join(__dirname, 'Data', 'enriched-events.json'),
        sessionClusters: path.join(__dirname, 'Data', 'session-clusters.json'),
        behavioralFeatures: path.join(__dirname, 'Data', 'behavioral-features.json'),
        uidMapping: path.join(__dirname, 'Data', 'uid-mappings.json'),
        enhancedStats: path.join(__dirname, 'Data', 'enhanced-stats.json')
    },
    SESSION_TIMEOUT_MS: 30 * 60 * 1000, // 30 minutes between conversations = new session
    MIN_ENGAGEMENT_TURNS: 5, // Conversations with 5+ turns are "high engagement"
    TOPIC_SHIFT_THRESHOLD: 0.3, // Cosine similarity threshold for topic change detection
};

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

/**
 * Generate deterministic UID from multiple factors
 */
function generateUID(...factors) {
    const hash = crypto.createHash('sha256');
    factors.forEach(f => hash.update(String(f)));
    return hash.digest('hex').substring(0, 16);
}

/**
 * Extract advanced intent from title and conversation metadata
 */
function extractAdvancedIntent(title, mapping, messages = []) {
    const titleLower = (title || '').toLowerCase();

    // Multi-dimensional intent classification
    const dimensions = {
        cognitive_load: 'unknown',
        task_complexity: 'simple',
        domain_specificity: 'general',
        urgency: 'low'
    };

    // Cognitive load indicators
    if (titleLower.match(/how|why|explain|understand|learn/)) {
        dimensions.cognitive_load = 'learning';
    } else if (titleLower.match(/fix|error|bug|issue|problem|help/)) {
        dimensions.cognitive_load = 'problem_solving';
    } else if (titleLower.match(/create|build|design|generate|make/)) {
        dimensions.cognitive_load = 'creative';
    } else if (titleLower.match(/analyze|compare|evaluate|assess/)) {
        dimensions.cognitive_load = 'analytical';
    } else {
        dimensions.cognitive_load = 'exploratory';
    }

    // Task complexity (based on title length and technical terms)
    const techTerms = titleLower.match(/api|code|function|algorithm|database|server|neural|model|regex|async/g);
    const titleWords = titleLower.split(/\s+/).length;

    if (techTerms && techTerms.length > 2 || titleWords > 10) {
        dimensions.task_complexity = 'complex';
    } else if (techTerms && techTerms.length > 0 || titleWords > 5) {
        dimensions.task_complexity = 'moderate';
    }

    // Domain specificity
    if (titleLower.match(/code|programming|function|api|git|docker|python|javascript|react|node/)) {
        dimensions.domain_specificity = 'coding';
    } else if (titleLower.match(/business|market|strategy|revenue|customer|sales/)) {
        dimensions.domain_specificity = 'business';
    } else if (titleLower.match(/design|art|creative|image|photo|visual/)) {
        dimensions.domain_specificity = 'creative';
    } else if (titleLower.match(/learn|study|research|paper|academic/)) {
        dimensions.domain_specificity = 'learning';
    }

    // Urgency (based on sentiment words  and punctuation)
    if (titleLower.match(/urgent|asap|immediately|quick|fast|help|critical|broken/)) {
        dimensions.urgency = 'high';
    } else if (titleLower.match(/soon|today|need|important/)) {
        dimensions.urgency = 'medium';
    }

    return dimensions;
}

/**
 * Calculate message velocity (messages per hour)
 */
function calculateMessageVelocity(mapping) {
    if (!mapping || mapping.length < 2) return 0;

    const timestamps = mapping.map(m => m.create_time ? new Date(m.create_time).getTime() : 0).filter(t => t > 0);
    if (timestamps.length < 2) return 0;

    const durationHours = (Math.max(...timestamps) - Math.min(...timestamps)) / (1000 * 60 * 60);
    return durationHours > 0 ? timestamps.length / durationHours : 0;
}

/**
 * Detect topic shift in conversation
 * Simple heuristic: look for significant semantic changes based on message author patterns
 */
function detectTopicShifts(mapping) {
    if (!mapping || mapping.length < 3) return 0;

    let shifts = 0;
    let prevAuthor = null;
    let consecutiveSameAuthor = 0;

    mapping.forEach(msg => {
        const author = msg.author?.role || 'unknown';
        if (author === prevAuthor) {
            consecutiveSameAuthor++;
        } else {
            // A shift might have occurred if same author speaks 3+ times in a row (clarification loop)
            if (consecutiveSameAuthor >= 3) shifts++;
            consecutiveSameAuthor = 1;
        }
        prevAuthor = author;
    });

    return shifts;
}

/**
 * Extract conversation metadata
 */
function extractConversationMetadata(conv) {
    const mapping = conv.mapping ? Object.values(conv.mapping) : [];
    const userMessages = mapping.filter(m => m.message && m.message.author?.role === 'user');
    const assistantMessages = mapping.filter(m => m.message && m.message.author?.role === 'assistant');

    return {
        turnCount: Math.min(userMessages.length, assistantMessages.length),
        userMessageCount: userMessages.length,
        assistantMessageCount: assistantMessages.length,
        totalMessages: mapping.length,
        messageVelocity: calculateMessageVelocity(mapping),
        topicShifts: detectTopicShifts(mapping),
        avgUserMessageLength: userMessages.length > 0
            ? userMessages.reduce((sum, m) => sum + ((m.message?.content?.parts?.[0] || '').length || 0), 0) / userMessages.length
            : 0,
        avgAssistantMessageLength: assistantMessages.length > 0
            ? assistantMessages.reduce((sum, m) => sum + ((m.message?.content?.parts?.[0] || '').length || 0), 0) / assistantMessages.length
            : 0,
    };
}

/**
 * Calculate engagement score (0-100)
 */
function calculateEngagementScore(metadata, conversationDurationMs) {
    const {
        turnCount,
        userMessageCount,
        assistantMessageCount,
        messageVelocity,
        topicShifts,
        avgUserMessageLength,
        avgAssistantMessageLength
    } = metadata;

    // Weighted scoring
    let score = 0;

    // Turn count (0-30 points)
    score += Math.min(turnCount * 3, 30);

    // Message velocity (0-20 points) - higher velocity = more engagement
    score += Math.min(messageVelocity * 2, 20);

    // Topic shifts (0-15 points) - some shifts indicate deep exploration
    score += Math.min(topicShifts * 5, 15);

    // Message length (0-20 points) - longer messages = more thought
    const avgLength = (avgUserMessageLength + avgAssistantMessageLength) / 2;
    score += Math.min(avgLength / 50, 20);

    // Balance (0-15 points) - balanced conversation is good
    const balance = 1 - Math.abs(userMessageCount - assistantMessageCount) / Math.max(userMessageCount, assistantMessageCount, 1);
    score += balance * 15;

    return Math.min(Math.round(score), 100);
}

// ============================================================================
// MAIN PARSER
// ============================================================================

async function parseEnhancedData() {
    console.log('🚀 Enhanced Data Parser Starting...\n');

    // Load all data sources
    console.log('📂 Loading data files...');
    const rawConversations = JSON.parse(fs.readFileSync(CONFIG.INPUT_FILES.conversations, 'utf-8'));
    const feedbackData = JSON.parse(fs.readFileSync(CONFIG.INPUT_FILES.feedback, 'utf-8'));

    let userData = {};
    let modelRecs = {};

    try {
        userData = JSON.parse(fs.readFileSync(CONFIG.INPUT_FILES.user, 'utf-8'));
    } catch (e) {
        console.log('⚠️  User data not found, continuing without it');
    }

    try {
        modelRecs = JSON.parse(fs.readFileSync(CONFIG.INPUT_FILES.modelRecs, 'utf-8'));
    } catch (e) {
        console.log('⚠️  Model recommendations not found, continuing without it');
    }

    console.log(`✅ Loaded ${rawConversations.length} conversations`);
    console.log(`✅ Loaded ${feedbackData.length} feedback entries\n`);

    // Build feedback lookup
    const feedbackMap = {};
    feedbackData.forEach(fb => {
        feedbackMap[fb.conversation_id] = fb;
    });

    // Process conversations
    console.log('🔍 Processing conversations...\n');
    const enrichedEvents = [];
    const sessionClusters = [];
    const behavioralFeatures = {};
    const uidMappings = {};

    let currentSessionId = null;
    let currentSessionStartTime = null;
    let currentSessionConversations = [];

    // Sort by create_time
    const sortedConversations = rawConversations
        .filter(c => c.create_time)
        .sort((a, b) => a.create_time - b.create_time);

    sortedConversations.forEach((conv, idx) => {
        const convId = conv.id || conv.conversation_id || `conv_${idx}`;
        const createTime = conv.create_time * 1000; // Convert to milliseconds
        const title = conv.title || 'Untitled';
        const model = (conv.current_model || conv.default_model_slug || 'UNKNOWN').toUpperCase().replace(/-/g, '_').replace('TEXT_DAVINCI_002_RENDER_SHA', 'TEXT-DAVINCI-002-RENDER-SHA');

        // Session clustering: group conversations within 30 min window
        if (!currentSessionId || (createTime - currentSessionStartTime) > CONFIG.SESSION_TIMEOUT_MS) {
            // Start new session
            if (currentSessionConversations.length > 0) {
                sessionClusters.push({
                    session_id: currentSessionId,
                    start_time: currentSessionStartTime,
                    end_time: currentSessionStartTime + (CONFIG.SESSION_TIMEOUT_MS),
                    conversation_ids: currentSessionConversations.map(c => c.id),
                    conversation_count: currentSessionConversations.length,
                    total_engagement_score: currentSessionConversations.reduce((sum, c) => sum + (c.engagement_score || 0), 0),
                });
            }

            currentSessionId = generateUID('session', createTime, convId);
            currentSessionStartTime = createTime;
            currentSessionConversations = [];
        }

        // Extract conversation metadata
        const metadata = extractConversationMetadata(conv);
        const feedback = feedbackMap[convId];
        const advancedIntent = extractAdvancedIntent(title, conv.mapping ? Object.values(conv.mapping) : []);
        const engagementScore = calculateEngagementScore(metadata, (conv.update_time - conv.create_time) * 1000);

        // Determine conversion
        const isConversion = engagementScore >= 50 || metadata.turnCount >= CONFIG.MIN_ENGAGEMENT_TURNS;
        const conversionValue = isConversion ? (engagementScore >= 80 ? 50 : 30) : 0;

        // Build context key (multi-dimensional)
        const intentLevel = engagementScore >= 60 ? 'high_intent' : (engagementScore >= 30 ? 'medium_intent' : 'low_intent');
        const contextKey = `${intentLevel}_${advancedIntent.domain_specificity}`;

        // Generate UIDs
        const conversationUID = generateUID('conv', convId, createTime);
        const sessionUID = currentSessionId;
        const userJourneyUID = generateUID('journey', conv.create_time, model, advancedIntent.cognitive_load);
        const behavioralUID = generateUID('behavior', metadata.turnCount, metadata.messageVelocity, metadata.topicShifts);

        // Create enriched event
        const enrichedEvent = {
            // Core Attribution Fields
            timestamp: conv.create_time,
            channel: model,
            context_key: contextKey,
            conversion_value: conversionValue,
            conversation_id: convId,
            title: title,
            os_version: 'Web',
            timezone_offset: '0',

            // Enhanced UIDs
            uids: {
                conversation_uid: conversationUID,
                session_uid: sessionUID,
                user_journey_uid: userJourneyUID,
                behavioral_uid: behavioralUID,
            },

            // Metadata (IR-compliant extension)
            metadata: {
                category: advancedIntent.domain_specificity,
                intent: intentLevel.replace('_intent', ''),
                conversion_type: isConversion ? (engagementScore >= 80 ? 'high_engagement' : 'medium_engagement') : 'none',
                model: model.toLowerCase(),

                // Advanced Intent Dimensions
                cognitive_load: advancedIntent.cognitive_load,
                task_complexity: advancedIntent.task_complexity,
                urgency: advancedIntent.urgency,

                // Conversation Metrics
                turn_count: metadata.turnCount,
                message_velocity: metadata.messageVelocity.toFixed(2),
                topic_shifts: metadata.topicShifts,
                engagement_score: engagementScore,
                avg_user_msg_length: Math.round(metadata.avgUserMessageLength),
                avg_assistant_msg_length: Math.round(metadata.avgAssistantMessageLength),

                // Feedback Integration
                has_feedback: !!feedback,
                feedback_rating: feedback?.rating || null,
                feedback_tags: feedback?.content ? JSON.parse(feedback.content).tags || [] : [],

                // Temporal Features
                hour_of_day: new Date(createTime).getHours(),
                day_of_week: new Date(createTime).getDay(),
                is_weekend: [0, 6].includes(new Date(createTime).getDay()),
            }
        };

        enrichedEvents.push(enrichedEvent);
        currentSessionConversations.push({
            id: convId,
            engagement_score: engagementScore,
            conversation_uid: conversationUID
        });

        // Store UID mappings
        uidMappings[convId] = {
            conversation_uid: conversationUID,
            session_uid: sessionUID,
            user_journey_uid: userJourneyUID,
            behavioral_uid: behavioralUID,
        };

        // Store behavioral features
        behavioralFeatures[behavioralUID] = {
            turn_count: metadata.turnCount,
            message_velocity: metadata.messageVelocity,
            topic_shifts: metadata.topicShifts,
            engagement_score: engagementScore,
            cognitive_load: advancedIntent.cognitive_load,
            task_complexity: advancedIntent.task_complexity,
        };

        // Progress logging
        if ((idx + 1) % 500 === 0) {
            console.log(`   Processed ${idx + 1}/${sortedConversations.length} conversations...`);
        }
    });

    // Add final session
    if (currentSessionConversations.length > 0) {
        sessionClusters.push({
            session_id: currentSessionId,
            start_time: currentSessionStartTime,
            conversation_ids: currentSessionConversations.map(c => c.id),
            conversation_count: currentSessionConversations.length,
            total_engagement_score: currentSessionConversations.reduce((sum, c) => sum + (c.engagement_score || 0), 0),
        });
    }

    console.log(`\n✅ Processed ${enrichedEvents.length} conversations`);
    console.log(`✅ Created ${sessionClusters.length} session clusters`);
    console.log(`✅ Generated ${Object.keys(behavioralFeatures).length} unique behavioral profiles\n`);

    // Generate enhanced stats
    const enhancedStats = {
        generated_at: new Date().toISOString(),
        total_conversations: enrichedEvents.length,
        total_conversions: enrichedEvents.filter(e => e.conversion_value > 0).length,
        total_conversion_value: enrichedEvents.reduce((sum, e) => sum + e.conversion_value, 0),
        total_sessions: sessionClusters.length,
        avg_conversations_per_session: (enrichedEvents.length / sessionClusters.length).toFixed(2),
        unique_behavioral_profiles: Object.keys(behavioralFeatures).length,

        by_cognitive_load: {},
        by_task_complexity: {},
        by_urgency: {},
        by_hour_of_day: {},
        by_engagement_tier: {
            high: enrichedEvents.filter(e => e.metadata.engagement_score >= 70).length,
            medium: enrichedEvents.filter(e => e.metadata.engagement_score >= 40 && e.metadata.engagement_score < 70).length,
            low: enrichedEvents.filter(e => e.metadata.engagement_score < 40).length,
        },
    };

    // Aggregate stats
    enrichedEvents.forEach(e => {
        const cl = e.metadata.cognitive_load;
        const tc = e.metadata.task_complexity;
        const urg = e.metadata.urgency;
        const hour = e.metadata.hour_of_day;

        enhancedStats.by_cognitive_load[cl] = (enhancedStats.by_cognitive_load[cl] || 0) + 1;
        enhancedStats.by_task_complexity[tc] = (enhancedStats.by_task_complexity[tc] || 0) + 1;
        enhancedStats.by_urgency[urg] = (enhancedStats.by_urgency[urg] || 0) + 1;
        enhancedStats.by_hour_of_day[hour] = (enhancedStats.by_hour_of_day[hour] || 0) + 1;
    });

    // Save outputs
    console.log('💾 Saving enhanced data...\n');

    fs.writeFileSync(CONFIG.OUTPUT_FILES.enrichedEvents, JSON.stringify(enrichedEvents, null, 2));
    console.log(`✅ Saved ${CONFIG.OUTPUT_FILES.enrichedEvents}`);

    fs.writeFileSync(CONFIG.OUTPUT_FILES.sessionClusters, JSON.stringify(sessionClusters, null, 2));
    console.log(`✅ Saved ${CONFIG.OUTPUT_FILES.sessionClusters}`);

    fs.writeFileSync(CONFIG.OUTPUT_FILES.behavioralFeatures, JSON.stringify(behavioralFeatures, null, 2));
    console.log(`✅ Saved ${CONFIG.OUTPUT_FILES.behavioralFeatures}`);

    fs.writeFileSync(CONFIG.OUTPUT_FILES.uidMapping, JSON.stringify(uidMappings, null, 2));
    console.log(`✅ Saved ${CONFIG.OUTPUT_FILES.uidMapping}`);

    fs.writeFileSync(CONFIG.OUTPUT_FILES.enhancedStats, JSON.stringify(enhancedStats, null, 2));
    console.log(`✅ Saved ${CONFIG.OUTPUT_FILES.enhancedStats}`);

    console.log('\n🎉 Enhanced Data Parsing Complete!\n');
    console.log('📊 Summary:');
    console.log(`   - ${enhancedStats.total_conversations} conversations processed`);
    console.log(`   - ${enhancedStats.total_conversions} conversions detected (${((enhancedStats.total_conversions / enhancedStats.total_conversations) * 100).toFixed(1)}%)`);
    console.log(`   - ${enhancedStats.total_sessions} user sessions identified`);
    console.log(`   - ${enhancedStats.unique_behavioral_profiles} unique behavioral patterns`);
    console.log(`   - ${enrichedStats.by_engagement_tier.high} high-engagement conversations`);
    console.log(`\n🔍 Next Steps:`);
    console.log(`   1. Review enriched-events.json for full attribution data`);
    console.log(`   2. Explore session-clusters.json for user journey insights`);
    console.log(`   3. Analyze behavioral-features.json for pattern mining`);
    console.log(`   4. Load enriched-events.json into attribution dashboard\n`);
}

// Run the parser
parseEnhancedData().catch(err => {
    console.error('❌ Error during parsing:', err);
    process.exit(1);
});
