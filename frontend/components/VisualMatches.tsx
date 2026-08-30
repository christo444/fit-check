import React, { useState, useEffect } from 'react';
import { ShoppingBag, Loader2, ExternalLink, Image as ImageIcon } from 'lucide-react';
import { searchVisualMatches, VisualMatch } from '../lib/api';

interface VisualMatchesProps {
  imageUrl: string;
}

export default function VisualMatches({ imageUrl }: VisualMatchesProps) {
  const [matches, setMatches] = useState<VisualMatch[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchMatches() {
      if (!imageUrl) return;
      
      setIsLoading(true);
      setError(null);
      try {
        const response = await searchVisualMatches(imageUrl);
        if (response.success && response.results) {
          setMatches(response.results);
        } else {
          setError("No exact matches found.");
        }
      } catch (err) {
        console.error("Failed to fetch visual matches:", err);
        setError("Failed to fetch shopping links.");
      } finally {
        setIsLoading(false);
      }
    }
    
    fetchMatches();
  }, [imageUrl]);

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center py-8 text-slate-400 bg-white/50 rounded-xl border border-slate-100">
        <Loader2 className="h-6 w-6 animate-spin text-violet-500 mb-3" />
        <p className="text-sm">Scanning photo for exact products...</p>
      </div>
    );
  }

  if (error || matches.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-6 text-slate-400 bg-slate-50 rounded-xl border border-slate-100 text-sm">
        <ImageIcon className="h-5 w-5 mb-2 opacity-50" />
        <p>{error || "No exact matches found."}</p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2 mb-2">
        <ShoppingBag className="h-4 w-4 text-violet-600" />
        <h4 className="text-sm font-semibold text-slate-800">Shop Exact Matches</h4>
      </div>
      
      {/* Horizontal scrolling container for product cards */}
      <div className="flex overflow-x-auto pb-4 gap-4 snap-x hide-scrollbar" style={{ scrollbarWidth: 'none' }}>
        {matches.map((match, i) => (
          <a
            key={i}
            href={match.url}
            target="_blank"
            rel="noopener noreferrer"
            className="flex-none w-[200px] snap-start flex flex-col rounded-xl border border-slate-200 bg-white hover:border-violet-300 hover:shadow-md transition-all group overflow-hidden"
          >
            <div className="h-48 w-full bg-slate-50 relative border-b border-slate-100 flex items-center justify-center overflow-hidden">
              {match.thumbnail ? (
                <img 
                  src={match.thumbnail} 
                  alt={match.title}
                  className="object-contain w-full h-full mix-blend-multiply group-hover:scale-105 transition-transform duration-300"
                />
              ) : (
                <ImageIcon className="h-8 w-8 text-slate-300" />
              )}
              {match.price && (
                <div className="absolute bottom-2 left-2 bg-white/90 backdrop-blur-sm px-2 py-1 rounded text-xs font-bold text-slate-800 shadow-sm">
                  {match.price}
                </div>
              )}
            </div>
            
            <div className="p-3 flex flex-col flex-1">
              <span className="text-[10px] font-bold tracking-wider uppercase text-slate-400 mb-1">
                {match.source}
              </span>
              <h5 className="font-semibold text-sm text-slate-900 group-hover:text-violet-700 line-clamp-2 leading-tight flex-1">
                {match.title}
              </h5>
              
              <div className="mt-3 flex items-center justify-between text-xs font-medium text-violet-600">
                <span>View Product</span>
                <ExternalLink className="h-3 w-3" />
              </div>
            </div>
          </a>
        ))}
      </div>
    </div>
  );
}
