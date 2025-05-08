/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
    NEXT_PUBLIC_AI_ENABLED: process.env.NEXT_PUBLIC_AI_ENABLED === 'true',
    NEXT_PUBLIC_QUERYBOOK_ENABLED: process.env.NEXT_PUBLIC_QUERYBOOK_ENABLED === 'true',
    NEXT_PUBLIC_QUERYBOOK_URL: process.env.NEXT_PUBLIC_QUERYBOOK_URL,
    NEXT_PUBLIC_QUERYBOOK_API_URL: process.env.NEXT_PUBLIC_QUERYBOOK_API_URL,
    NEXT_PUBLIC_DOCETL_ENABLED: process.env.NEXT_PUBLIC_DOCETL_ENABLED === 'true',
    NEXT_PUBLIC_DOCETL_API_URL: process.env.NEXT_PUBLIC_DOCETL_API_URL,
  },
  async rewrites() {
    const rewrites = [];

    // Only add Querybook rewrites if enabled
    if (process.env.NEXT_PUBLIC_QUERYBOOK_ENABLED === 'true') {
      rewrites.push({
        source: '/querybook/:path*',
        destination: `${process.env.NEXT_PUBLIC_QUERYBOOK_URL}/:path*`,
      });

      rewrites.push({
        source: '/querybook-api/:path*',
        destination: `${process.env.NEXT_PUBLIC_QUERYBOOK_API_URL}/:path*`,
      });
    }

    // Only add DocETL rewrites if enabled
    if (process.env.NEXT_PUBLIC_DOCETL_ENABLED === 'true') {
      rewrites.push({
        source: '/docetl-api/:path*',
        destination: `${process.env.NEXT_PUBLIC_DOCETL_API_URL}/:path*`,
      });
    }

    return rewrites;
  },
}

module.exports = nextConfig
