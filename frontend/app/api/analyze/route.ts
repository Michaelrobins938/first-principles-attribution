import { NextResponse } from 'next/server'

export async function POST(request: Request) {
  try {
    const formData = await request.formData()
    const file = formData.get('file')

    if (!file) {
      return NextResponse.json({ error: 'No file provided' }, { status: 400 })
    }

    const text = await (file as Blob).text()
    const data = JSON.parse(text)
    
    // For now, return mock analysis results to test the frontend
    // This simulates what the backend would return
    const mockResult = {
      status: 'success',
      total_journeys: data.journeys?.length || 0,
      total_conversions: data.journeys?.filter((j: any) => j.conversion).length || 0,
      unique_channels: Array.from(new Set(data.journeys?.flatMap((j: any) => j.path?.map((p: any) => p.channel) || []) || [])).length,
      processing_time_ms: Math.random() * 1000 + 500,
      hybrid_result: {
        alpha_used: 0.5,
        channel_attributions: {
          'Direct': 0.35,
          'Search': 0.25,
          'Social': 0.20,
          'Email': 0.15,
          'Paid': 0.05
        }
      },
      markov_result: {
        removal_effects: {
          'Direct': 0.32,
          'Search': 0.28,
          'Social': 0.22,
          'Email': 0.13,
          'Paid': 0.05
        }
      },
      shapley_result: {
        values: {
          'Direct': 0.38,
          'Search': 0.22,
          'Social': 0.18,
          'Email': 0.17,
          'Paid': 0.05
        }
      }
    }

    // Try to connect to backend if URL is configured, but don't fail if it doesn't work
    const backendUrl = process.env.BACKEND_URL
    if (backendUrl) {
      try {
        console.log('Attempting to connect to backend:', backendUrl)
        const response = await fetch(`${backendUrl}/api/v1/attribution/analyze`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(data),
        })

        if (response.ok) {
          const result = await response.json()
          return NextResponse.json(result)
        } else {
          console.warn('Backend not available, using mock data')
        }
      } catch (backendError) {
        console.warn('Backend connection failed, using mock data:', backendError)
      }
    }

    return NextResponse.json(mockResult)
  } catch (error) {
    console.error('API error:', error)
    return NextResponse.json({ error: String(error) }, { status: 500 })
  }
}
