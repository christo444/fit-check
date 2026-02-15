import Link from "next/link";
import { Upload, Home, Shirt } from "lucide-react";

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      {/* Navigation */}
      <nav className="border-b bg-white/80 backdrop-blur-sm">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Shirt className="h-6 w-6" />
            <h1 className="text-xl font-bold">FitCheck</h1>
          </div>
          <div className="flex gap-4">
            <Link
              href="/"
              className="flex items-center gap-2 px-4 py-2 rounded-lg hover:bg-slate-100 transition"
            >
              <Home className="h-4 w-4" />
              Home
            </Link>
            <Link
              href="/wardrobe"
              className="flex items-center gap-2 px-4 py-2 rounded-lg hover:bg-slate-100 transition"
            >
              <Shirt className="h-4 w-4" />
              Wardrobe
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <main className="container mx-auto px-4 py-16">
        <div className="max-w-3xl mx-auto text-center space-y-8">
          <div className="space-y-4">
            <h2 className="text-5xl font-bold tracking-tight">
              AI-Powered Fashion Analysis
            </h2>
            <p className="text-xl text-slate-600">
              Upload your outfit photos and get instant style insights,
              fit analysis, and personalized recommendations
            </p>
          </div>

          {/* CTA Button */}
          <Link
            href="/upload"
            className="inline-flex items-center gap-2 px-8 py-4 bg-black text-white rounded-lg hover:bg-slate-800 transition-colors text-lg font-medium"
          >
            <Upload className="h-5 w-5" />
            Upload Your Outfit
          </Link>

          {/* Feature Cards */}
          <div className="grid md:grid-cols-3 gap-6 mt-16">
            <div className="bg-white p-6 rounded-xl shadow-sm border">
              <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
                <Upload className="h-6 w-6 text-blue-600" />
              </div>
              <h3 className="font-semibold mb-2">Smart Detection</h3>
              <p className="text-sm text-slate-600">
                AI detects clothing items, colors, and patterns automatically
              </p>
            </div>

            <div className="bg-white p-6 rounded-xl shadow-sm border">
              <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-4">
                <Shirt className="h-6 w-6 text-purple-600" />
              </div>
              <h3 className="font-semibold mb-2">Fit Analysis</h3>
              <p className="text-sm text-slate-600">
                Get size estimates and fit recommendations using pose detection
              </p>
            </div>

            <div className="bg-white p-6 rounded-xl shadow-sm border">
              <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mb-4">
                <Home className="h-6 w-6 text-green-600" />
              </div>
              <h3 className="font-semibold mb-2">Style Insights</h3>
              <p className="text-sm text-slate-600">
                Receive AI-generated style descriptions and outfit suggestions
              </p>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
