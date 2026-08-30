import React, { useState, useEffect } from 'react';
import { ShoppingBag, Loader2, ExternalLink } from 'lucide-react';
import { searchProducts, SearchResult } from '../lib/api';

interface ProductRecommendationsProps {
  keywords: string[];
}

export default function ProductRecommendations({ keywords }: ProductRecommendationsProps) {
  const [products, setProducts] = useState<SearchResult[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function fetchAllProducts() {
      setIsLoading(true);
      try {
        // Take up to 2 keywords to avoid spamming the search
        const topKeywords = keywords.slice(0, 2);
        
        const promises = topKeywords.map(kw => searchProducts(kw));
        const responses = await Promise.all(promises);
        
        // Flatten and deduplicate results by URL
        const allResults: SearchResult[] = [];
        const seenUrls = new Set<string>();
        
        responses.forEach(res => {
          if (res.success && res.results) {
            res.results.forEach(product => {
              if (!seenUrls.has(product.url)) {
                seenUrls.add(product.url);
                allResults.push(product);
              }
            });
          }
        });
        
        setProducts(allResults.slice(0, 5)); // Keep top 5 total
      } catch (err) {
        console.error("Failed to fetch products:", err);
      } finally {
        setIsLoading(false);
      }
    }
    
    if (keywords && keywords.length > 0) {
      fetchAllProducts();
    } else {
      setIsLoading(false);
    }
  }, [keywords]);

  if (isLoading) {
    return (
      <div className="flex flex-col items-center justify-center py-8 text-slate-400 bg-white/50 rounded-xl border border-slate-100">
        <Loader2 className="h-6 w-6 animate-spin text-violet-500 mb-3" />
        <p className="text-sm">Curating shopping links for your style...</p>
      </div>
    );
  }

  if (products.length === 0) {
    return null;
  }

  return (
    <div className="space-y-3">
      <div className="flex items-center gap-2 mb-2">
        <ShoppingBag className="h-4 w-4 text-violet-600" />
        <h4 className="text-sm font-semibold text-slate-800">Shop this Look</h4>
      </div>
      
      {/* Horizontal scrolling container for product cards */}
      <div className="flex overflow-x-auto pb-4 gap-4 snap-x hide-scrollbar" style={{ scrollbarWidth: 'none' }}>
        {products.map((product, i) => (
          <a
            key={i}
            href={product.url}
            target="_blank"
            rel="noopener noreferrer"
            className="flex-none w-[260px] snap-start flex flex-col p-4 rounded-xl border border-slate-200 bg-white hover:border-violet-300 hover:shadow-md transition-all group"
          >
            <div className="flex-1">
              <h5 className="font-semibold text-sm text-slate-900 group-hover:text-violet-700 line-clamp-2 leading-tight mb-2">
                {product.title}
              </h5>
              <p className="text-xs text-slate-500 line-clamp-3">
                {product.description}
              </p>
            </div>
            <div className="mt-4 pt-3 border-t border-slate-100 flex items-center justify-between text-xs font-medium text-violet-600">
              <span>View Product</span>
              <ExternalLink className="h-3.5 w-3.5" />
            </div>
          </a>
        ))}
      </div>
    </div>
  );
}
