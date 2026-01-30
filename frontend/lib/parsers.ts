/**
 * Client-Side ETL (Extract, Transform, Load) Library
 * Maps standard data exports to internal attribution format
 */

export interface JourneyData {
  journeys: Array<{
    journey_id: string;
    path: Array<{
      channel: string;
      timestamp: string;
    }>;
    conversion: boolean;
    conversion_value?: number;
    num_touchpoints: number;
    duration_hours: number;
  }>;
}

export interface ParseResult {
  success: boolean;
  data?: JourneyData;
  error?: string;
  metadata: {
    source: string;
    rowsProcessed: number;
    columnsDetected: string[];
  };
}

/**
 * Google Takeout MyActivity parser
 */
export function parseGoogleTakeout(csvText: string): ParseResult {
  try {
    const lines = csvText.split('\n').filter(line => line.trim());
    const header = lines[0].split(',').map(h => h.trim().toLowerCase());
    
    const journeys: JourneyData['journeys'] = [];
    let rowsProcessed = 0;

    for (let i = 1; i < lines.length; i++) {
      const values = lines[i].split(',').map(v => v.trim());
      const row: any = {};
      
      header.forEach((col, idx) => {
        row[col] = values[idx];
      });

      // Map Google MyActivity format to internal format
      if (row.title && row.titlekeywords) {
        const timestamp = new Date(row.time).toISOString();
        const channel = extractChannelFromGoogleActivity(row.title, row.titlekeywords);
        
        if (channel) {
          const journeyId = extractOrCreateJourneyId(journeys, timestamp);
          
          if (!journeys.find(j => j.journey_id === journeyId)) {
            journeys.push({
              journey_id: journeyId,
              path: [],
              conversion: false,
              conversion_value: 0,
              num_touchpoints: 0,
              duration_hours: 0
            });
          }
          
          const journey = journeys.find(j => j.journey_id === journeyId)!;
          journey.path.push({ channel, timestamp });
          journey.num_touchpoints = journey.path.length;
          
          // Detect conversion based on activity type
          if (row.titlekeywords?.includes('visited') || row.titlekeywords?.includes('purchased')) {
            journey.conversion = true;
            journey.conversion_value = estimateConversionValue(row.title);
          }
        }
      }
      rowsProcessed++;
    }

    // Calculate duration and clean up
    journeys.forEach(journey => {
      if (journey.path.length >= 2) {
        const start = new Date(journey.path[0].timestamp);
        const end = new Date(journey.path[journey.path.length - 1].timestamp);
        journey.duration_hours = (end.getTime() - start.getTime()) / (1000 * 60 * 60);
      }
    });

    return {
      success: true,
      data: { journeys },
      metadata: {
        source: 'Google Takeout',
        rowsProcessed,
        columnsDetected: header
      }
    };
  } catch (error) {
    return {
      success: false,
      error: `Google Takeout parsing failed: ${error}`,
      metadata: {
        source: 'Google Takeout',
        rowsProcessed: 0,
        columnsDetected: []
      }
    };
  }
}

/**
 * Facebook Ads Manager parser
 */
export function parseFacebookAds(csvText: string): ParseResult {
  try {
    const lines = csvText.split('\n').filter(line => line.trim());
    const header = lines[0].split(',').map(h => h.trim().toLowerCase());
    
    const journeys: JourneyData['journeys'] = [];
    let rowsProcessed = 0;

    for (let i = 1; i < lines.length; i++) {
      const values = lines[i].split(',').map(v => v.trim());
      const row: any = {};
      
      header.forEach((col, idx) => {
        row[col] = values[idx];
      });

      // Facebook Ads typically has campaign, action, conversion event
      if (row.campaign_name && row.action_type) {
        const timestamp = new Date(row.action_time || row.date).toISOString();
        const channel = `Facebook: ${row.campaign_name}`;
        const journeyId = extractOrCreateJourneyId(journeys, timestamp);
        
        if (!journeys.find(j => j.journey_id === journeyId)) {
          journeys.push({
            journey_id: journeyId,
            path: [],
            conversion: false,
            conversion_value: 0,
            num_touchpoints: 0,
            duration_hours: 0
          });
        }
        
        const journey = journeys.find(j => j.journey_id === journeyId)!;
        journey.path.push({ channel, timestamp });
        journey.num_touchpoints = journey.path.length;
        
        // Facebook conversions
        if (row.action_type?.toLowerCase().includes('conversion') || row.conversion_value > 0) {
          journey.conversion = true;
          journey.conversion_value = parseFloat(row.conversion_value) || 0;
        }
      }
      rowsProcessed++;
    }

    // Calculate duration
    journeys.forEach(journey => {
      if (journey.path.length >= 2) {
        const start = new Date(journey.path[0].timestamp);
        const end = new Date(journey.path[journey.path.length - 1].timestamp);
        journey.duration_hours = (end.getTime() - start.getTime()) / (1000 * 60 * 60);
      }
    });

    return {
      success: true,
      data: { journeys },
      metadata: {
        source: 'Facebook Ads',
        rowsProcessed,
        columnsDetected: header
      }
    };
  } catch (error) {
    return {
      success: false,
      error: `Facebook Ads parsing failed: ${error}`,
      metadata: {
        source: 'Facebook Ads',
        rowsProcessed: 0,
        columnsDetected: []
      }
    };
  }
}

/**
 * Shopify Orders parser
 */
export function parseShopifyOrders(csvText: string): ParseResult {
  try {
    const lines = csvText.split('\n').filter(line => line.trim());
    const header = lines[0].split(',').map(h => h.trim().toLowerCase());
    
    const journeys: JourneyData['journeys'] = [];
    let rowsProcessed = 0;

    for (let i = 1; i < lines.length; i++) {
      const values = lines[i].split(',').map(v => v.trim());
      const row: any = {};
      
      header.forEach((col, idx) => {
        row[col] = values[idx];
      });

      // Shopify orders have customer, source, created_at
      if (row.order_id && row.customer_id) {
        const timestamp = new Date(row.created_at || row.processed_at).toISOString();
        const journeyId = `shopify_${row.customer_id}`;
        const channel = row.utm_source || row.source || 'Direct';
        
        let journey = journeys.find(j => j.journey_id === journeyId);
        if (!journey) {
          journey = {
            journey_id: journeyId,
            path: [],
            conversion: false,
            conversion_value: 0,
            num_touchpoints: 0,
            duration_hours: 0
          };
          journeys.push(journey);
        }
        
        // Add touchpoint (each order is a touchpoint)
        journey.path.push({ channel, timestamp });
        journey.num_touchpoints = journey.path.length;
        journey.conversion = true; // Orders are conversions
        journey.conversion_value = parseFloat(row.total_price) || 0;
      }
      rowsProcessed++;
    }

    // Calculate duration per customer journey
    journeys.forEach(journey => {
      if (journey.path.length >= 2) {
        const start = new Date(journey.path[0].timestamp);
        const end = new Date(journey.path[journey.path.length - 1].timestamp);
        journey.duration_hours = (end.getTime() - start.getTime()) / (1000 * 60 * 60);
      }
    });

    return {
      success: true,
      data: { journeys },
      metadata: {
        source: 'Shopify Orders',
        rowsProcessed,
        columnsDetected: header
      }
    };
  } catch (error) {
    return {
      success: false,
      error: `Shopify parsing failed: ${error}`,
      metadata: {
        source: 'Shopify Orders',
        rowsProcessed: 0,
        columnsDetected: []
      }
    };
  }
}

/**
 * GA4 Data Export parser
 */
export function parseGA4(csvText: string): ParseResult {
  try {
    const lines = csvText.split('\n').filter(line => line.trim());
    const header = lines[0].split(',').map(h => h.trim().toLowerCase());
    
    const journeys: JourneyData['journeys'] = [];
    let rowsProcessed = 0;

    for (let i = 1; i < lines.length; i++) {
      const values = lines[i].split(',').map(v => v.trim());
      const row: any = {};
      
      header.forEach((col, idx) => {
        row[col] = values[idx];
      });

      // GA4 format: event_name, source, medium, campaign, user_id, timestamp
      if (row.event_name && row.user_pseudo_id) {
        const timestamp = new Date(row.event_date || row.event_timestamp).toISOString();
        const journeyId = `ga4_${row.user_pseudo_id}`;
        
        // Build channel from source/medium/campaign
        const channel = buildGA4Channel(row.source, row.medium, row.campaign);
        
        let journey = journeys.find(j => j.journey_id === journeyId);
        if (!journey) {
          journey = {
            journey_id: journeyId,
            path: [],
            conversion: false,
            conversion_value: 0,
            num_touchpoints: 0,
            duration_hours: 0
          };
          journeys.push(journey);
        }
        
        journey.path.push({ channel, timestamp });
        journey.num_touchpoints = journey.path.length;
        
        // GA4 conversion events
        if (row.event_name === 'purchase' || row.event_name === 'conversion') {
          journey.conversion = true;
          journey.conversion_value = parseFloat(row.event_value) || 0;
        }
      }
      rowsProcessed++;
    }

    // Calculate duration
    journeys.forEach(journey => {
      if (journey.path.length >= 2) {
        const start = new Date(journey.path[0].timestamp);
        const end = new Date(journey.path[journey.path.length - 1].timestamp);
        journey.duration_hours = (end.getTime() - start.getTime()) / (1000 * 60 * 60);
      }
    });

    return {
      success: true,
      data: { journeys },
      metadata: {
        source: 'GA4 Export',
        rowsProcessed,
        columnsDetected: header
      }
    };
  } catch (error) {
    return {
      success: false,
      error: `GA4 parsing failed: ${error}`,
      metadata: {
        source: 'GA4 Export',
        rowsProcessed: 0,
        columnsDetected: []
      }
    };
  }
}

// Helper functions
function extractChannelFromGoogleActivity(title: string, keywords: string): string | null {
  const keywordMap: { [key: string]: string } = {
    'google': 'Search',
    'youtube': 'Video',
    'chrome': 'Direct',
    'play': 'Mobile',
    'maps': 'Location',
    'gmail': 'Email',
    'drive': 'Cloud',
    'photos': 'Media',
    'news': 'Content',
    'shopping': 'Ecommerce'
  };

  const text = (title + ' ' + keywords).toLowerCase();
  for (const [keyword, channel] of Object.entries(keywordMap)) {
    if (text.includes(keyword)) {
      return channel;
    }
  }
  return 'Other';
}

function extractOrCreateJourneyId(journeys: JourneyData['journeys'], timestamp: string): string {
  const now = new Date(timestamp);
  const dateKey = now.toISOString().split('T')[0]; // YYYY-MM-DD
  
  // Group by hour sessions (simplified)
  const hourKey = dateKey + '_' + now.getHours();
  const existingJourney = journeys.find(j => j.journey_id.startsWith(hourKey));
  
  if (existingJourney) {
    return existingJourney.journey_id;
  }
  
  return `session_${hourKey}_${Math.random().toString(36).substr(2, 9)}`;
}

function estimateConversionValue(title: string): number {
  const valueMap: { [key: string]: number } = {
    'purchase': 100,
    'subscribe': 50,
    'checkout': 75,
    'signup': 25
  };
  
  const text = title.toLowerCase();
  for (const [keyword, value] of Object.entries(valueMap)) {
    if (text.includes(keyword)) {
      return value;
    }
  }
  return 0;
}

function buildGA4Channel(source?: string, medium?: string, campaign?: string): string {
  const parts = [];
  if (source && source !== '(not set)' && source !== '(none)') parts.push(source);
  if (medium && medium !== '(not set)' && medium !== '(none)') parts.push(medium);
  if (campaign && campaign !== '(not set)' && campaign !== '(none)') parts.push(campaign);
  
  return parts.length > 0 ? parts.join(' / ') : 'Direct';
}

/**
 * Auto-detect data source and parse
 */
export function parseAutoDetect(csvText: string): ParseResult {
  const lines = csvText.split('\n').filter(line => line.trim());
  const header = lines[0].toLowerCase();
  
  // Auto-detect based on column headers
  if (header.includes('titlekeywords') && header.includes('time')) {
    return parseGoogleTakeout(csvText);
  } else if (header.includes('campaign_name') && header.includes('action_type')) {
    return parseFacebookAds(csvText);
  } else if (header.includes('order_id') && header.includes('customer_id')) {
    return parseShopifyOrders(csvText);
  } else if (header.includes('event_name') && header.includes('user_pseudo_id')) {
    return parseGA4(csvText);
  } else {
    // Fallback to basic CSV parsing
    return {
      success: false,
      error: 'Unable to auto-detect data source. Please specify the format manually.',
      metadata: {
        source: 'Unknown',
        rowsProcessed: 0,
        columnsDetected: header.split(',').map(h => h.trim())
      }
    };
  }
}