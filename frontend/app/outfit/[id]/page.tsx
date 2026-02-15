"use client";

import { useParams } from "next/navigation";
import Link from "next/link";
import { ArrowLeft, Loader2, Sparkles, User } from "lucide-react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { getOutfitById, detectClothing, detectPose, Detection, Landmark, PoseConnection, Measurements } from "@/lib/api";
import { useState } from "react";
import DetectionOverlay from "@/components/DetectionOverlay";
import PoseOverlay from "@/components/PoseOverlay";

export default function OutfitDetailPage() {
  const params = useParams();
  const outfitId = params.id as string;
  
  // Detection state
  const [detections, setDetections] = useState<Detection[]>([]);
  const [imageDimensions, setImageDimensions] = useState({ width: 0, height: 0 });
  
  // Pose state
  const [landmarks, setLandmarks] = useState<Landmark[]>([]);
  const [connections, setConnections] = useState<PoseConnection[]>([]);
  const [measurements, setMeasurements] = useState<Measurements>({});
  const [showPose, setShowPose] = useState(false);

  const { data: outfit, isLoading, error } = useQuery({
    queryKey: ["outfit", outfitId],
    queryFn: () => getOutfitById(outfitId),
    enabled: !!outfitId,
  });

  const detectMutation = useMutation({
    mutationFn: () => detectClothing(outfitId),
    onSuccess: (data) => {
      setDetections(data.detections);
      setImageDimensions(data.image_dimensions);
      setShowPose(false); // Switch to detection view
    },
  });

  const poseMutation = useMutation({
    mutationFn: () => detectPose(outfitId),
    onSuccess: (data) => {
      setLandmarks(data.landmarks);
      setConnections(data.connections);
      setMeasurements(data.measurements);
      setImageDimensions(data.image_dimensions);
      setShowPose(true); // Switch to pose view
    },
  });

  const handleDetect = () => {
    detectMutation.mutate();
  };

  const handleDetectPose = () => {
    poseMutation.mutate();
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-slate-600" />
      </div>
    );
  }

  if (error || !outfit) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold mb-2">Outfit not found</h2>
          <Link href="/" className="text-blue-600 hover:underline">
            Return to home
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      {/* Navigation */}
      <nav className="border-b bg-white/80 backdrop-blur-sm">
        <div className="container mx-auto px-4 py-4">
          <Link
            href="/wardrobe"
            className="inline-flex items-center gap-2 px-4 py-2 rounded-lg hover:bg-slate-100 transition"
          >
            <ArrowLeft className="h-4 w-4" />
            Back to Wardrobe
          </Link>
        </div>
      </nav>

      {/* Outfit Details */}
      <main className="container mx-auto px-4 py-8">
        <div className="max-w-6xl mx-auto">
          <div className="grid md:grid-cols-2 gap-8">
            {/* Image Section */}
            <div className="bg-white p-4 rounded-xl border">
              {showPose && landmarks.length > 0 ? (
                <div className="relative">
                  <img
                    src={outfit.image_url}
                    alt="Outfit"
                    className="w-full h-auto rounded-lg"
                  />
                  <PoseOverlay
                    landmarks={landmarks}
                    connections={connections}
                    imageWidth={imageDimensions.width}
                    imageHeight={imageDimensions.height}
                  />
                </div>
              ) : detections.length > 0 ? (
                <DetectionOverlay
                  imageUrl={outfit.image_url}
                  detections={detections}
                  imageWidth={imageDimensions.width}
                  imageHeight={imageDimensions.height}
                />
              ) : (
                <img
                  src={outfit.image_url}
                  alt="Outfit"
                  className="w-full h-auto rounded-lg"
                />
              )}
            </div>

            {/* Details Section */}
            <div className="space-y-6">
              <div className="bg-white p-6 rounded-xl border">
                <h2 className="text-2xl font-bold mb-4">Outfit Analysis</h2>
                <div className="space-y-2 text-sm">
                  <p>
                    <span className="font-semibold">Uploaded:</span>{" "}
                    {new Date(outfit.created_at).toLocaleDateString()}
                  </p>
                  <p>
                    <span className="font-semibold">Status:</span>{" "}
                    <span className="capitalize">{outfit.status}</span>
                  </p>
                </div>

                {/* Detect Buttons */}
                <div className="mt-6 grid grid-cols-2 gap-3">
                  <button
                    onClick={handleDetect}
                    disabled={detectMutation.isPending}
                    className="flex items-center justify-center gap-2 px-4 py-3 bg-black text-white rounded-lg hover:bg-slate-800 transition disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {detectMutation.isPending ? (
                      <>
                        <Loader2 className="h-4 w-4 animate-spin" />
                        Analyzing...
                      </>
                    ) : (
                      <>
                        <Sparkles className="h-4 w-4" />
                        Detect Items
                      </>
                    )}
                  </button>

                  <button
                    onClick={handleDetectPose}
                    disabled={poseMutation.isPending}
                    className="flex items-center justify-center gap-2 px-4 py-3 bg-slate-700 text-white rounded-lg hover:bg-slate-600 transition disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    {poseMutation.isPending ? (
                      <>
                        <Loader2 className="h-4 w-4 animate-spin" />
                        Analyzing...
                      </>
                    ) : (
                      <>
                        <User className="h-4 w-4" />
                        Detect Pose
                      </>
                    )}
                  </button>
                </div>
              </div>

              {/* Detection Results */}
              {detections.length > 0 && !showPose && (
                <div className="bg-white p-6 rounded-xl border">
                  <h3 className="font-semibold mb-3">
                    Detected Items ({detections.length})
                  </h3>
                  <div className="space-y-3">
                    {detections.map((detection, index) => (
                      <div
                        key={index}
                        className="flex items-center justify-between p-3 bg-slate-50 rounded-lg"
                      >
                        <div>
                          <p className="font-medium capitalize">
                            {detection.class_name}
                          </p>
                          <p className="text-sm text-slate-600">
                            Size: {detection.bbox.width} × {detection.bbox.height}px
                          </p>
                        </div>
                        <div className="text-right">
                          <p className="font-semibold text-green-600">
                            {(detection.confidence * 100).toFixed(1)}%
                          </p>
                          <p className="text-xs text-slate-500">confidence</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Pose Results */}
              {landmarks.length > 0 && showPose && (
                <div className="bg-white p-6 rounded-xl border">
                  <h3 className="font-semibold mb-3">
                    Pose Analysis ({landmarks.length} landmarks detected)
                  </h3>
                  
                  {/* Body Measurements */}
                  {Object.keys(measurements).length > 0 && (
                    <div className="space-y-2 mb-4">
                      <h4 className="text-sm font-medium text-slate-700">Body Measurements</h4>
                      <div className="grid grid-cols-2 gap-2 text-sm">
                        {measurements.shoulder_width && (
                          <div className="p-2 bg-slate-50 rounded">
                            <p className="text-slate-600">Shoulder Width</p>
                            <p className="font-semibold">{measurements.shoulder_width}px</p>
                          </div>
                        )}
                        {measurements.hip_width && (
                          <div className="p-2 bg-slate-50 rounded">
                            <p className="text-slate-600">Hip Width</p>
                            <p className="font-semibold">{measurements.hip_width}px</p>
                          </div>
                        )}
                        {measurements.body_height && (
                          <div className="p-2 bg-slate-50 rounded">
                            <p className="text-slate-600">Body Height</p>
                            <p className="font-semibold">{measurements.body_height}px</p>
                          </div>
                        )}
                        {measurements.torso_length && (
                          <div className="p-2 bg-slate-50 rounded">
                            <p className="text-slate-600">Torso Length</p>
                            <p className="font-semibold">{measurements.torso_length}px</p>
                          </div>
                        )}
                        {measurements.shoulder_to_hip_ratio && (
                          <div className="p-2 bg-blue-50 rounded col-span-2">
                            <p className="text-slate-600">Shoulder-to-Hip Ratio</p>
                            <p className="font-semibold text-blue-700">{measurements.shoulder_to_hip_ratio}</p>
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                  
                  {/* Key Landmarks */}
                  <div className="mt-4">
                    <h4 className="text-sm font-medium text-slate-700 mb-2">Key Landmarks</h4>
                    <div className="space-y-1 text-xs max-h-48 overflow-y-auto">
                      {landmarks.filter(l => l.visibility > 0.7).slice(0, 10).map((landmark) => (
                        <div key={landmark.id} className="flex justify-between p-2 bg-slate-50 rounded">
                          <span className="capitalize">{landmark.name.replace(/_/g, ' ')}</span>
                          <span className="text-slate-500">{(landmark.visibility * 100).toFixed(0)}% visible</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {/* Error Display */}
              {(detectMutation.isError || poseMutation.isError) && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-800 text-sm">
                  {detectMutation.isError && "Detection failed. "}
                  {poseMutation.isError && "Pose detection failed. "}
                  Make sure the backend is running and try again.
                </div>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
