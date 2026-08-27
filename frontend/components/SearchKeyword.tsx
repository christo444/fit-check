import React, { useState, useRef, useEffect } from 'react';
import { ShoppingCart, Search, ExternalLink, ChevronDown } from 'lucide-react';

interface SearchKeywordProps {
  keyword: string;
}

export default function SearchKeyword({ keyword }: SearchKeywordProps) {
  const [isOpen, setIsOpen] = useState(false);
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

  const encodedKeyword = encodeURIComponent(keyword);

  const searchLinks = [
    {
      name: "Google Shopping",
      url: `https://www.google.com/search?tbm=shop&q=${encodedKeyword}`,
      icon: <Search className="h-4 w-4" />
    },
    {
      name: "Amazon",
      url: `https://www.amazon.com/s?k=${encodedKeyword}`,
      icon: <ShoppingCart className="h-4 w-4" />
    },
    {
      name: "ASOS",
      url: `https://www.asos.com/search/?q=${encodedKeyword}`,
      icon: <ShoppingCart className="h-4 w-4" />
    }
  ];

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
        <div className="absolute z-10 mt-2 w-48 bg-white rounded-lg shadow-xl border border-slate-100 py-1 left-0 animate-in fade-in slide-in-from-top-2 duration-200">
          <div className="px-3 py-2 text-xs font-semibold text-slate-500 uppercase tracking-wider border-b border-slate-100 mb-1">
            Search on
          </div>
          {searchLinks.map((link) => (
            <a
              key={link.name}
              href={link.url}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center justify-between px-4 py-2 text-sm text-slate-700 hover:bg-violet-50 hover:text-violet-700 transition-colors"
              onClick={() => setIsOpen(false)}
            >
              <div className="flex items-center gap-2">
                {link.icon}
                <span>{link.name}</span>
              </div>
              <ExternalLink className="h-3 w-3 opacity-50" />
            </a>
          ))}
        </div>
      )}
    </div>
  );
}
