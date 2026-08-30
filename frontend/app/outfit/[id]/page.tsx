"use client";

import { useParams } from "next/navigation";
import Link from "next/link";
import { ArrowLeft, Loader2, Sparkles, User, Palette, Shirt, Brain, ChevronDown, ChevronUp } from "lucide-react";
import { useQuery, useMutation } from "@tanstack/react-query";
import { getOutfitById, detectClothing, detectPose, extractAttributes, analyzeFit, analyzeStyle, Detection, Landmark, PoseConnection, Measurements, AttributeItem, FitItem, LLMResult } from "@/lib/api";
import { useState } from "react";
import DetectionOverlay from "@/components/DetectionOverlay";
import PoseOverlay from "@/components/PoseOverlay";
import ProductRecommendations from "@/components/ProductRecommendations";

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

  // Attributes state
  const [attributes, setAttributes] = useState<AttributeItem[]>([]);
  const [showAttributes, setShowAttributes] = useState(false);

  // Fit analysis state
  const [fitResults, setFitResults] = useState<FitItem[]>([]);
  const [showFit, setShowFit] = useState(false);

  // LLM Style analysis state
  const [styleAnalysis, setStyleAnalysis] = useState<LLMResult | null>(null);
  const [expandedSuggestion, setExpandedSuggestion] = useState<number | null>(null);

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

  const attributesMutation = useMutation({
    mutationFn: () => extractAttributes(outfitId),
    onSuccess: (data) => {
      setAttributes(data.items);
      setImageDimensions(data.image_dimensions);
      setShowAttributes(true);
      setShowPose(false); // Switch to attributes view
    },
  });

  const fitMutation = useMutation({
    mutationFn: () => analyzeFit(outfitId),
    onSuccess: (data) => {
      setFitResults(data.items);
      setImageDimensions(data.image_dimensions);
      setShowFit(true);
      setShowPose(false);
      setShowAttributes(false);
    },
  });

  const styleMutation = useMutation({
    mutationFn: () => analyzeStyle(outfitId),
    onSuccess: (data) => {
      setStyleAnalysis(data);
    },
  });

  const handleDetect = () => {
    detectMutation.mutate();
  };

  const handleDetectPose = () => {
    poseMutation.mutate();
  };

  const handleExtractAttributes = () => {
    attributesMutation.mutate();
  };

  const handleAnalyzeFit = () => {
    fitMutation.mutate();
  };

  const handleAnalyzeStyle = () => {
    styleMutation.mutate();
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
                <div className="mt-6 grid grid-cols-2 md:grid-cols-4 gap-3">
                  <button
                    onClick={handleDetect}
                    disabled={detectMutation.isPending}
                    className="flex items-center justify-center gap-2 px-3 py-3 bg-black text-white rounded-lg hover:bg-slate-800 transition disabled:opacity-50 disabled:cursor-not-allowed text-sm"
                  >
                    {detectMutation.isPending ? (
                      <>
                        <Loader2 className="h-4 w-4 animate-spin" />
                        <span className="hidden sm:inline">Analyzing...</span>
                      </>
                    ) : (
                      <>
                        <Sparkles className="h-4 w-4" />
                        <span className="hidden sm:inline">Detect Items</span>
                      </>
                    )}
                  </button>

                  <button
                    onClick={handleDetectPose}
                    disabled={poseMutation.isPending}
                    className="flex items-center justify-center gap-2 px-3 py-3 bg-slate-700 text-white rounded-lg hover:bg-slate-600 transition disabled:opacity-50 disabled:cursor-not-allowed text-sm"
                  >
                    {poseMutation.isPending ? (
                      <>
                        <Loader2 className="h-4 w-4 animate-spin" />
                        <span className="hidden sm:inline">Analyzing...</span>
                      </>
                    ) : (
                      <>
                        <User className="h-4 w-4" />
                        <span className="hidden sm:inline">Detect Pose</span>
                      </>
                    )}
                  </button>

                  <button
                    onClick={handleExtractAttributes}
                    disabled={attributesMutation.isPending}
                    className="flex items-center justify-center gap-2 px-3 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition disabled:opacity-50 disabled:cursor-not-allowed text-sm"
                  >
                    {attributesMutation.isPending ? (
                      <>
                        <Loader2 className="h-4 w-4 animate-spin" />
                        <span className="hidden sm:inline">Analyzing...</span>
                      </>
                    ) : (
                      <>
                        <Palette className="h-4 w-4" />
                        <span className="hidden sm:inline">Colors & Patterns</span>
                      </>
                    )}
                  </button>

                  <button
                    onClick={handleAnalyzeFit}
                    disabled={fitMutation.isPending}
                    className="flex items-center justify-center gap-2 px-3 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition disabled:opacity-50 disabled:cursor-not-allowed text-sm"
                  >
                    {fitMutation.isPending ? (
                      <>
                        <Loader2 className="h-4 w-4 animate-spin" />
                        <span className="hidden sm:inline">Analyzing...</span>
                      </>
                    ) : (
                      <>
                        <Shirt className="h-4 w-4" />
                        <span className="hidden sm:inline">Analyze Fit</span>
                      </>
                    )}
                  </button>
                </div>

                {/* AI Style Analysis Button */}
                <div className="mt-3">
                  <button
                    onClick={handleAnalyzeStyle}
                    disabled={styleMutation.isPending}
                    className="w-full flex items-center justify-center gap-2 px-4 py-3 bg-gradient-to-r from-violet-600 to-fuchsia-600 text-white rounded-lg hover:from-violet-700 hover:to-fuchsia-700 transition disabled:opacity-50 disabled:cursor-not-allowed font-medium shadow-lg"
                  >
                    {styleMutation.isPending ? (
                      <>
                        <Loader2 className="h-5 w-5 animate-spin" />
                        <span>AI is thinking...</span>
                      </>
                    ) : (
                      <>
                        <Brain className="h-5 w-5" />
                        <span>AI Style Analysis</span>
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

              {/* Attributes Results (Colors & Patterns) */}
              {attributes.length > 0 && showAttributes && (
                <div className="bg-white p-6 rounded-xl border">
                  <h3 className="font-semibold mb-3">
                    Color & Pattern Analysis ({attributes.length} items)
                  </h3>
                  <div className="space-y-4">
                    {attributes.map((item, index) => (
                      <div
                        key={index}
                        className="p-4 bg-gradient-to-r from-slate-50 to-purple-50 rounded-lg border"
                      >
                        {/* Item Header */}
                        <div className="flex items-center justify-between mb-3">
                          <div>
                            <p className="font-medium capitalize text-lg">
                              {item.class_name}
                            </p>
                            <p className="text-xs text-slate-500">
                              Detection #{item.detection_id + 1}
                            </p>
                          </div>
                          <div className="text-right">
                            <p className="text-xs text-slate-600 font-medium">
                              {(item.confidence * 100).toFixed(1)}% confidence
                            </p>
                          </div>
                        </div>

                        {/* Colors Section */}
                        <div className="mb-3">
                          <h4 className="text-sm font-medium text-slate-700 mb-2">
                            Dominant Colors
                          </h4>
                          <div className="flex flex-wrap gap-2">
                            {item.colors.map((color, colorIdx) => (
                              <div
                                key={colorIdx}
                                className="flex items-center gap-2 bg-white px-3 py-2 rounded-md border shadow-sm"
                              >
                                <div
                                  className="w-6 h-6 rounded border-2 border-slate-200 shadow-sm"
                                  style={{ backgroundColor: color.hex }}
                                  title={color.hex}
                                />
                                <div className="text-xs">
                                  <p className="font-medium capitalize">{color.name}</p>
                                  <p className="text-slate-500">{color.percentage.toFixed(1)}%</p>
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>

                        {/* Pattern Section */}
                        <div className="pt-3 border-t">
                          <h4 className="text-sm font-medium text-slate-700 mb-2">
                            Pattern Type
                          </h4>
                          <div className="flex items-center gap-3">
                            <div className="px-4 py-2 bg-purple-100 text-purple-800 rounded-full text-sm font-medium capitalize">
                              {item.pattern.type}
                            </div>
                            <div className="text-sm text-slate-600">
                              {(item.pattern.confidence * 100).toFixed(0)}% confidence
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Fit Analysis Results */}
              {fitResults.length > 0 && showFit && (
                <div className="bg-white p-6 rounded-xl border">
                  <h3 className="font-semibold mb-3">
                    Fit & Size Analysis ({fitResults.length} items)
                  </h3>
                  <div className="space-y-4">
                    {fitResults.map((item, index) => (
                      <div
                        key={index}
                        className="p-4 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg border"
                      >
                        {/* Item Header */}
                        <div className="flex items-center justify-between mb-3">
                          <div>
                            <p className="font-medium capitalize text-lg">
                              {item.class_name}
                            </p>
                            <p className="text-xs text-slate-500">
                              Detection #{item.detection_id + 1}
                            </p>
                          </div>
                        </div>

                        {/* Fit Type Badge */}
                        <div className="mb-3">
                          <h4 className="text-sm font-medium text-slate-700 mb-2">
                            Fit Type
                          </h4>
                          <div className="flex items-center gap-3">
                            <div className={`px-4 py-2 rounded-full text-sm font-medium capitalize ${
                              item.fit_type === 'slim' ? 'bg-green-100 text-green-800' :
                              item.fit_type === 'regular' ? 'bg-blue-100 text-blue-800' :
                              item.fit_type === 'oversized' ? 'bg-orange-100 text-orange-800' :
                              'bg-red-100 text-red-800'
                            }`}>
                              {item.fit_type}
                            </div>
                            <div className="text-sm text-slate-600">
                              {(item.fit_confidence * 100).toFixed(0)}% confidence
                            </div>
                          </div>
                        </div>

                        {/* Size Recommendation */}
                        <div className="mb-3">
                          <h4 className="text-sm font-medium text-slate-700 mb-2">
                            Estimated Size
                          </h4>
                          <div className="flex items-center gap-3">
                            <div className="px-4 py-2 bg-indigo-100 text-indigo-800 rounded-full text-sm font-bold">
                              {item.size_estimate}
                            </div>
                            <div className="text-sm text-slate-600">
                              {(item.size_confidence * 100).toFixed(0)}% confidence
                            </div>
                          </div>
                        </div>

                        {/* Fit Ratio Visualization */}
                        <div className="mb-3">
                          <h4 className="text-sm font-medium text-slate-700 mb-2">
                            Fit Ratio: {item.fit_ratio}
                          </h4>
                          <div className="relative w-full h-6 bg-slate-200 rounded-full overflow-hidden">
                            <div
                              className={`absolute left-0 top-0 h-full rounded-full transition-all ${
                                item.fit_type === 'slim' ? 'bg-green-500' :
                                item.fit_type === 'regular' ? 'bg-blue-500' :
                                item.fit_type === 'oversized' ? 'bg-orange-500' :
                                'bg-red-500'
                              }`}
                              style={{ width: `${Math.min(item.fit_ratio * 50, 100)}%` }}
                            />
                            <div className="absolute inset-0 flex items-center justify-center">
                              <span className="text-xs font-medium text-slate-700">
                                {item.clothing_width.toFixed(0)}px / {item.body_width.toFixed(0)}px
                              </span>
                            </div>
                          </div>
                        </div>

                        {/* Reasoning */}
                        <div className="pt-3 border-t">
                          <h4 className="text-sm font-medium text-slate-700 mb-2">
                            Analysis
                          </h4>
                          <p className="text-sm text-slate-600">
                            {item.reasoning}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Error Display */}
              {(detectMutation.isError || poseMutation.isError || attributesMutation.isError || fitMutation.isError) && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-800 text-sm">
                  {detectMutation.isError && "Detection failed. "}
                  {poseMutation.isError && "Pose detection failed. "}
                  {attributesMutation.isError && "Attribute extraction failed. "}
                  {fitMutation.isError && "Fit analysis failed. "}
                  Make sure the backend is running and try again.
                </div>
              )}

              {/* LLM Style Analysis Results */}
              {styleAnalysis && (
                <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm animate-in fade-in duration-500">
                  <div className="flex items-center justify-between mb-6">
                    <div className="flex items-center gap-2">
                      <Brain className="h-5 w-5 text-violet-600" />
                      <h3 className="font-bold text-lg text-slate-900">AI Stylist</h3>
                    </div>
                    <div className="flex items-center gap-2 px-3 py-1 bg-violet-50 text-violet-700 rounded-full text-sm font-semibold capitalize border border-violet-100">
                      {styleAnalysis.style.type}
                    </div>
                  </div>

                  {/* Minimalist Style Description Tooltip/Detail */}
                  <details className="mb-6 group">
                    <summary className="text-sm font-medium text-slate-500 cursor-pointer hover:text-slate-700 list-none flex items-center gap-1">
                      <Sparkles className="h-3 w-3" />
                      Why this style?
                    </summary>
                    <p className="mt-2 text-sm text-slate-600 leading-relaxed bg-slate-50 p-3 rounded-lg border border-slate-100">
                      {styleAnalysis.style.description}
                    </p>
                  </details>

                  {/* Shop this Look (Auto-fetches products) */}
                  <div className="mb-6">
                    <ProductRecommendations keywords={styleAnalysis.keywords} />
                  </div>

                  {/* Minimalist Outfit Suggestions */}
                  <div className="mb-6">
                    <h4 className="text-xs font-semibold text-slate-400 uppercase tracking-wider mb-3">Suggested Pairings</h4>
                    <ul className="space-y-2">
                      {styleAnalysis.suggestions.map((suggestion, index) => (
                        <li key={index} className="flex items-start gap-2 text-sm text-slate-700">
                          <span className="mt-1 flex-shrink-0 w-1.5 h-1.5 bg-violet-400 rounded-full"></span>
                          <span>
                            <strong className="text-slate-900 font-medium">{suggestion.title}: </strong>
                            {suggestion.description}
                          </span>
                        </li>
                      ))}
                    </ul>
                  </div>

                  {/* Minimalist Fashion Advice */}
                  <div className="bg-amber-50/50 rounded-lg p-3 border border-amber-100 flex items-start gap-3">
                    <Sparkles className="h-4 w-4 text-amber-500 flex-shrink-0 mt-0.5" />
                    <p className="text-xs text-slate-600 leading-relaxed">
                      <strong className="font-medium text-slate-800">Pro Tip: </strong>
                      {styleAnalysis.advice}
                    </p>
                  </div>
                </div>
              )}

              {/* Style Analysis Error */}
              {styleMutation.isError && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-800 text-sm">
                  <p className="font-semibold mb-1">AI Style Analysis Failed</p>
                  <p>This could be due to:</p>
                  <ul className="list-disc list-inside mt-2 space-y-1 text-xs">
                    <li>LLM service not configured (check .env file)</li>
                    <li>No analysis data available (run detection/pose/attributes first)</li>
                    <li>API rate limit reached</li>
                    <li>Invalid API key</li>
                  </ul>
                </div>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
