"use client";

import Link from "next/link";
import { ArrowLeft, Loader2, Upload } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { getAllOutfits } from "@/lib/api";

export default function WardrobePage() {
  const { data: outfits, isLoading, error } = useQuery({
    queryKey: ["outfits"],
    queryFn: getAllOutfits,
  });

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      {/* Navigation */}
      <nav className="border-b bg-white/80 backdrop-blur-sm">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <Link
            href="/"
            className="inline-flex items-center gap-2 px-4 py-2 rounded-lg hover:bg-slate-100 transition"
          >
            <ArrowLeft className="h-4 w-4" />
            Back to Home
          </Link>
          <Link
            href="/upload"
            className="inline-flex items-center gap-2 px-4 py-2 bg-black text-white rounded-lg hover:bg-slate-800 transition"
          >
            <Upload className="h-4 w-4" />
            Upload New
          </Link>
        </div>
      </nav>

      {/* Wardrobe Grid */}
      <main className="container mx-auto px-4 py-8">
        <h1 className="text-4xl font-bold mb-8">My Wardrobe</h1>

        {isLoading && (
          <div className="flex items-center justify-center py-16">
            <Loader2 className="h-8 w-8 animate-spin text-slate-600" />
          </div>
        )}

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-800">
            Failed to load outfits. Please try again.
          </div>
        )}

        {outfits && outfits.length === 0 && (
          <div className="text-center py-16">
            <p className="text-slate-600 mb-4">
              No outfits yet. Upload your first outfit!
            </p>
            <Link
              href="/upload"
              className="inline-flex items-center gap-2 px-6 py-3 bg-black text-white rounded-lg hover:bg-slate-800 transition"
            >
              <Upload className="h-4 w-4" />
              Upload Outfit
            </Link>
          </div>
        )}

        {outfits && outfits.length > 0 && (
          <div className="grid md:grid-cols-3 lg:grid-cols-4 gap-6">
            {outfits.map((outfit) => (
              <Link
                key={outfit.id}
                href={`/outfit/${outfit.id}`}
                className="group bg-white rounded-xl border overflow-hidden hover:shadow-lg transition"
              >
                <div className="aspect-square relative overflow-hidden bg-slate-100">
                  <img
                    src={outfit.image_url}
                    alt="Outfit"
                    className="w-full h-full object-cover group-hover:scale-105 transition"
                  />
                </div>
                <div className="p-4">
                  <p className="text-sm text-slate-600">
                    {new Date(outfit.created_at).toLocaleDateString()}
                  </p>
                </div>
              </Link>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}
