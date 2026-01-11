'use client';

import { Badge } from '@/components/ui/badge';

export function Header() {
  return (
    <div className="relative overflow-hidden rounded-xl bg-gradient-to-r from-[#8458B3] via-[#9b6fc4] to-[#7a4ca1] p-8 text-white shadow-xl mb-8">
      {/* Decorative circles */}
      <div className="absolute -top-1/2 -right-[10%] w-72 h-72 rounded-full bg-white/10 blur-3xl" />
      <div className="absolute -bottom-1/3 left-[10%] w-48 h-48 rounded-full bg-white/5 blur-2xl" />
      
      <div className="relative z-10">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-6 mb-6">
          {/* Logo section */}
          <div className="flex items-center gap-4">
            <div className="flex items-center justify-center w-14 h-14 rounded-lg bg-white/15 backdrop-blur-sm shadow-lg">
              <span className="text-3xl">🔍</span>
            </div>
            <div>
              <h1 className="text-2xl md:text-3xl font-bold">Review Sentinel</h1>
              <p className="text-white/85 font-medium">AI-Powered Insights</p>
            </div>
          </div>

          {/* Feature badges */}
          <div className="flex flex-wrap gap-3">
            <Badge variant="secondary" className="bg-white/12 text-white border-white/20 hover:bg-white/20 transition-all">
              <span className="mr-1.5">🍎</span> App Store
            </Badge>
            <Badge variant="secondary" className="bg-white/12 text-white border-white/20 hover:bg-white/20 transition-all">
              <span className="mr-1.5">🤖</span> Play Store
            </Badge>
            <Badge variant="secondary" className="bg-white/12 text-white border-white/20 hover:bg-white/20 transition-all">
              <span className="mr-1.5">📱</span> Reddit
            </Badge>
            <Badge variant="secondary" className="bg-white/12 text-white border-white/20 hover:bg-white/20 transition-all">
              <span className="mr-1.5">✨</span> AI Analysis
            </Badge>
          </div>
        </div>

        <div className="pt-4 border-t border-white/20">
          <p className="text-white/90 leading-relaxed">
            Transform customer reviews into actionable insights. Analyze sentiment, identify patterns, 
            and prioritize improvements with AI intelligence.
          </p>
        </div>
      </div>
    </div>
  );
}
