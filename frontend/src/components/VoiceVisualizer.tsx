"use client";

import React from "react";

interface VoiceVisualizerProps {
  isListening: boolean;
  audioLevel?: number;
  interimText?: string;
  languageName?: string;
}

export const VoiceVisualizer: React.FC<VoiceVisualizerProps> = ({
  isListening,
  audioLevel = 0,
  interimText = "",
  languageName = "English",
}) => {
  if (!isListening) return null;

  // Generate 7 bar heights based on audioLevel and pseudo-random frequency distribution
  const bars = [0.3, 0.6, 0.9, 1.0, 0.8, 0.5, 0.2].map((factor, i) => {
    const base = 8;
    const dynamic = isListening ? Math.max(4, audioLevel * 32 * factor) : 4;
    return Math.min(36, base + dynamic);
  });

  return (
    <div className="w-full px-4 py-3 bg-gradient-to-r from-amber-500/10 via-amber-600/15 to-amber-500/10 border border-amber-500/30 rounded-2xl backdrop-blur-md flex flex-col items-center justify-center gap-2 transition-all animate-fade-in shadow-lg">
      <div className="flex items-center gap-1.5 h-9">
        {bars.map((height, i) => (
          <span
            key={i}
            className="w-1.5 bg-gradient-to-t from-amber-600 to-amber-400 rounded-full transition-all duration-75 ease-out shadow-sm shadow-amber-500/50"
            style={{
              height: `${height}px`,
              opacity: Math.max(0.4, audioLevel * 1.5),
            }}
          />
        ))}
      </div>

      <div className="text-center max-w-full">
        <p className="text-xs font-medium text-amber-300 flex items-center justify-center gap-1.5">
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping inline-block" />
          Listening ({languageName})... Speak your legal concern
        </p>
        {interimText && (
          <p className="text-sm font-semibold text-white mt-1 italic line-clamp-2 px-2">
            &ldquo;{interimText}&rdquo;
          </p>
        )}
      </div>
    </div>
  );
};
