import React, { useState, useRef, useEffect } from 'react';
import { ShoppingCart, Search, ExternalLink, ChevronDown, Loader2 } from 'lucide-react';
import { searchProducts, SearchResult } from '../lib/api';

interface SearchKeywordProps {
  keyword: string;
}

export default function SearchKeyword({ keyword }: SearchKeywordProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [products, setProducts] = useState<SearchResult[]>([]);
  const [hasSearched, setHasSearched] = useState(false);
  
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Handle click outside to close dropdown
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => {
      document.removeEventListener("mousedown", handleClickOutside);
    };
  }, []);

  // Fetch products when opened (if not already fetched)
  useEffect(() => {
    if (isOpen && !hasSearched) {
      setIsLoading(true);
      searchProducts(keyword)
        .then(response => {
          if (response.success && response.results) {
            setProducts(response.results);
          }
        })
        .catch(err => {
          console.error("Failed to fetch products:", err);
        })
        .finally(() => {
          setIsLoading(false);
          setHasSearched(true);
        });
    }
  }, [isOpen, keyword, hasSearched]);

  return (
    <div className="relative inline-block" ref={dropdownRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className={`flex items-center gap-1.5 px-3 py-1.5 bg-white text-violet-700 rounded-full text-sm border shadow-sm transition hover:shadow-md ${
          isOpen ? 'border-violet-400 bg-violet-50 ring-2 ring-violet-100' : 'border-violet-200 hover:border-violet-300'
        }`}
      >
        <Search className="h-3.5 w-3.5 text-violet-500" />
        <span>{keyword}</span>
        <ChevronDown className={`h-3.5 w-3.5 text-violet-400 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {isOpen && (
        <div className="absolute z-10 mt-2 w-[340px] bg-white rounded-xl shadow-xl border border-slate-200 p-3 left-0 animate-in fade-in slide-in-from-top-2 duration-200">
          <div className="flex items-center justify-between mb-3 px-1">
            <h4 className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
              Shopping Results
            </h4>
            <a 
              href={`https://www.google.com/search?tbm=shop&q=${encodeURIComponent(keyword)}`}
              target="_blank"
              rel="noopener noreferrer"
              className="text-xs text-violet-600 hover:text-violet-800 flex items-center gap-1"
            >
              Google Shopping <ExternalLink className="h-3 w-3" />
            </a>
          </div>

          {isLoading ? (
            <div className="flex flex-col items-center justify-center py-6 text-slate-400">
              <Loader2 className="h-6 w-6 animate-spin text-violet-500 mb-2" />
              <p className="text-sm">Finding products online...</p>
            </div>
          ) : products.length > 0 ? (
            <div className="space-y-2 max-h-[300px] overflow-y-auto pr-1">
              {products.map((product, i) => (
                <a
                  key={i}
                  href={product.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="block p-3 rounded-lg border border-slate-100 bg-slate-50 hover:bg-violet-50 hover:border-violet-200 transition-colors group"
                >
                  <h5 className="font-medium text-sm text-slate-800 group-hover:text-violet-700 line-clamp-2 leading-tight mb-1">
                    {product.title}
                  </h5>
                  <p className="text-xs text-slate-500 line-clamp-2">
                    {product.description}
                  </p>
                  <div className="mt-2 flex items-center gap-1.5 text-xs font-medium text-emerald-600">
                    <ShoppingCart className="h-3.5 w-3.5" />
                    <span>View Store</span>
                  </div>
                </a>
              ))}
            </div>
          ) : (
            <div className="py-4 text-center text-sm text-slate-500">
              No direct products found. Try the Google Shopping link above.
            </div>
          )}
        </div>
      )}
    </div>
  );
}
