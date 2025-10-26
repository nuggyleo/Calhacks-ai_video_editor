import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    console.log('=== API Route: Save Video started ===');

    const body = await request.json();
    const { filename, url, description, user_email } = body;

    console.log('Save video request:', { filename, url, user_email });

    if (!filename || !url || !user_email) {
      console.log('Missing required fields');
      return NextResponse.json(
        { error: 'Missing required fields: filename, url, user_email' },
        { status: 400 }
      );
    }

    // Forward the request to the backend
    const backendUrl = process.env.BACKEND_API_URL || 'http://localhost:8000';
    console.log(`Forwarding to backend at ${backendUrl}/api/saved-videos/`);

    const encodedEmail = encodeURIComponent(user_email);
    const response = await fetch(
      `${backendUrl}/api/saved-videos/?user_email=${encodedEmail}`,
      {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          filename,
          url,
          description,
        }),
      }
    );

    console.log('Backend response status:', response.status);
    const responseText = await response.text();
    console.log('Backend response:', responseText);

    if (!response.ok) {
      console.log('Backend error:', responseText);
      return NextResponse.json(
        { error: `Backend error: ${responseText}` },
        { status: response.status }
      );
    }

    const data = JSON.parse(responseText);
    console.log('Video saved successfully:', data);
    return NextResponse.json(data);

  } catch (error) {
    console.error('=== API Route Error ===');
    console.error('Error:', error);
    console.error('Error message:', error instanceof Error ? error.message : 'Unknown error');

    return NextResponse.json(
      {
        error: 'Save video failed',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    );
  }
}

export async function GET(request: NextRequest) {
  try {
    console.log('=== API Route: Load Saved Videos started ===');

    const searchParams = request.nextUrl.searchParams;
    const user_email = searchParams.get('user_email');

    console.log('Load saved videos request:', { user_email });

    if (!user_email) {
      console.log('Missing user_email');
      return NextResponse.json(
        { error: 'Missing required parameter: user_email' },
        { status: 400 }
      );
    }

    // Forward the request to the backend
    const backendUrl = process.env.BACKEND_API_URL || 'http://localhost:8000';
    console.log(`Forwarding to backend at ${backendUrl}/api/saved-videos/`);

    const encodedEmail = encodeURIComponent(user_email);
    const response = await fetch(
      `${backendUrl}/api/saved-videos/?user_email=${encodedEmail}`
    );

    console.log('Backend response status:', response.status);
    const responseText = await response.text();
    console.log('Backend response:', responseText);

    if (!response.ok) {
      console.log('Backend error:', responseText);
      return NextResponse.json(
        { error: `Backend error: ${responseText}` },
        { status: response.status }
      );
    }

    const data = JSON.parse(responseText);
    console.log('Saved videos loaded:', data);
    return NextResponse.json(data);

  } catch (error) {
    console.error('=== API Route Error ===');
    console.error('Error:', error);
    console.error('Error message:', error instanceof Error ? error.message : 'Unknown error');

    return NextResponse.json(
      {
        error: 'Load saved videos failed',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    );
  }
}

export async function DELETE(request: NextRequest) {
  try {
    console.log('=== API Route: Delete Saved Video started ===');

    const searchParams = request.nextUrl.searchParams;
    const user_email = searchParams.get('user_email');
    const video_id = searchParams.get('video_id');

    console.log('Delete saved video request:', { user_email, video_id });

    if (!user_email || !video_id) {
      console.log('Missing required parameters');
      return NextResponse.json(
        { error: 'Missing required parameters: user_email, video_id' },
        { status: 400 }
      );
    }

    // Forward the request to the backend
    const backendUrl = process.env.BACKEND_API_URL || 'http://localhost:8000';
    console.log(`Forwarding to backend at ${backendUrl}/api/saved-videos/${video_id}`);

    const encodedEmail = encodeURIComponent(user_email);
    const response = await fetch(
      `${backendUrl}/api/saved-videos/${video_id}?user_email=${encodedEmail}`,
      { method: 'DELETE' }
    );

    console.log('Backend response status:', response.status);
    const responseText = await response.text();
    console.log('Backend response:', responseText);

    if (!response.ok) {
      console.log('Backend error:', responseText);
      return NextResponse.json(
        { error: `Backend error: ${responseText}` },
        { status: response.status }
      );
    }

    const data = JSON.parse(responseText || '{}');
    console.log('Video deleted successfully:', data);
    return NextResponse.json(data);

  } catch (error) {
    console.error('=== API Route Error ===');
    console.error('Error:', error);
    console.error('Error message:', error instanceof Error ? error.message : 'Unknown error');

    return NextResponse.json(
      {
        error: 'Delete video failed',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    );
  }
}
