/** @type {import('next').NextConfig} */
const nextConfig = {
  output: "export",
  basePath: "/web",
  trailingSlash: true,
  images: { unoptimized: true },
  eslint: { ignoreDuringBuilds: true },
};

export default nextConfig;
