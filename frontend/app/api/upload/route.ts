import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    console.log('=== API Route: Upload started ===');

    const formData = await request.formData();
    console.log('FormData received');

    const file = formData.get('file') as File;
    console.log('File:', file?.name, 'Size:', file?.size);

    if (!file) {
      console.log('No file provided');
      return NextResponse.json(
        { error: 'No file provided' },
        { status: 400 }
      );
    }

    // Forward the request to the backend
    const backendUrl = process.env.BACKEND_API_URL || 'http://localhost:8000';
    console.log(`Forwarding to backend at ${backendUrl}/api/upload`);

    const backendFormData = new FormData();
    backendFormData.append('file', file);

    const response = await fetch(`${backendUrl}/api/upload`, {
      method: 'POST',
      body: backendFormData,
    });

    console.log('Backend response status:', response.status);
    const text = await response.text();
    console.log('Backend response text:', text);

    if (!response.ok) {
      console.log('Backend error:', text);
      return NextResponse.json(
        { error: `Backend error: ${text}` },
        { status: response.status }
      );
    }

    const data = JSON.parse(text);
    console.log('Upload successful:', data);
    return NextResponse.json(data);

  } catch (error) {
    console.error('=== API Route Error ===');
    console.error('Error:', error);
    console.error('Error message:', error instanceof Error ? error.message : 'Unknown error');

    return NextResponse.json(
      {
        error: 'Upload failed',
        details: error instanceof Error ? error.message : 'Unknown error'
      },
      { status: 500 }
    );
  }
}
