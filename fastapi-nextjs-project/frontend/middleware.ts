import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

// This function can be marked `async` if using `await` inside
export function middleware(request: NextRequest) {
  // Check if the route is AI-related
  const isAIRoute = request.nextUrl.pathname.startsWith('/ai-tools');
  
  // If it's an AI route, we need to check if AI is enabled
  if (isAIRoute) {
    // In a real implementation, we would check a cookie or environment variable
    // For now, we'll redirect to a special endpoint that will check server-side
    return NextResponse.rewrite(new URL('/api/check-ai-access?redirect=' + request.nextUrl.pathname, request.url));
  }
  
  // For non-AI routes, continue normally
  return NextResponse.next();
}

// See "Matching Paths" below to learn more
export const config = {
  matcher: ['/ai-tools/:path*'],
};
