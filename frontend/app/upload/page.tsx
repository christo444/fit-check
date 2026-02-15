"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { ArrowLeft } from "lucide-react";
import UploadBox from "@/components/UploadBox";

export default function UploadPage() {
  const router = useRouter();
  const [isUploading, setIsUploading] = useState(false);

  const handleUploadSuccess = (outfitId: string) => {
    // Navigate to outfit detail page after successful upload
    router.push(`/outfit/${outfitId}`);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      {/* Navigation */}
      <nav className="border-b bg-white/80 backdrop-blur-sm">
        <div className="container mx-auto px-4 py-4">
          <Link
            href="/"
            className="inline-flex items-center gap-2 px-4 py-2 rounded-lg hover:bg-slate-100 transition"
          >
            <ArrowLeft className="h-4 w-4" />
            Back to Home
          </Link>
        </div>
      </nav>

      {/* Upload Section */}
      <main className="container mx-auto px-4 py-16">
        <div className="max-w-2xl mx-auto">
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold mb-2">Upload Your Outfit</h1>
            <p className="text-slate-600">
              Take or upload a full-body photo for AI analysis
            </p>
          </div>

          <UploadBox
            onUploadSuccess={handleUploadSuccess}
            isUploading={isUploading}
            setIsUploading={setIsUploading}
          />

          {/* Tips */}
          <div className="mt-8 bg-white p-6 rounded-xl border">
            <h3 className="font-semibold mb-3">📸 Tips for best results:</h3>
            <ul className="space-y-2 text-sm text-slate-600">
              <li>• Take a full-body photo with good lighting</li>
              <li>• Stand straight facing the camera</li>
              <li>• Wear a complete outfit (top + bottom + shoes)</li>
              <li>• Use a plain background if possible</li>
              <li>• Make sure your entire outfit is visible</li>
            </ul>
          </div>
        </div>
      </main>
    </div>
  );
}
