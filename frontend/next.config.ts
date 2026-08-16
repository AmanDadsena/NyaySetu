import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  experimental: {
    // React's <ViewTransition> integration. Route changes become real
    // transitions rather than a hard swap, which is what lets a heading morph
    // into the same heading on the next page instead of blinking out of
    // existence. Browsers without the View Transitions API ignore it and the
    // app navigates normally, so this degrades to exactly today's behaviour.
    viewTransition: true,
  },
};

export default nextConfig;
