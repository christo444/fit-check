"use client";

import { Detection } from "@/lib/api";

interface DetectionOverlayProps {
  imageUrl: string;
  detections: Detection[];
  imageWidth: number;
  imageHeight: number;
}

export default function DetectionOverlay({
  imageUrl,
  detections,
  imageWidth,
  imageHeight,
}: DetectionOverlayProps) {
  // Color mapping for different classes
  const getColorForClass = (className: string): string => {
    const colors: Record<string, string> = {
      person: "#00ff00",      // Green
      backpack: "#ff0000",    // Blue
      handbag: "#ff00ff",     // Magenta
      tie: "#00ffff",         // Cyan
      suitcase: "#ffa500",    // Orange
    };
    return colors[className] || "#00c8c8"; // Default cyan
  };

  return (
    <div className="relative inline-block w-full">
      {/* Image */}
      <img
        src={imageUrl}
        alt="Outfit with detections"
        className="w-full h-auto rounded-lg"
      />

      {/* SVG Overlay for bounding boxes */}
      <svg
        className="absolute top-0 left-0 w-full h-full pointer-events-none"
        viewBox={`0 0 ${imageWidth} ${imageHeight}`}
        preserveAspectRatio="none"
      >
        {detections.map((detection, index) => {
          const { x1, y1, x2, y2 } = detection.bbox;
          const width = x2 - x1;
          const height = y2 - y1;
          const color = getColorForClass(detection.class_name);

          return (
            <g key={index}>
              {/* Bounding box rectangle */}
              <rect
                x={x1}
                y={y1}
                width={width}
                height={height}
                fill="none"
                stroke={color}
                strokeWidth="3"
                opacity="0.8"
              />

              {/* Label background */}
              <rect
                x={x1}
                y={y1 - 30}
                width={width}
                height="30"
                fill={color}
                opacity="0.8"
              />

              {/* Label text */}
              <text
                x={x1 + 5}
                y={y1 - 10}
                fill="white"
                fontSize="14"
                fontWeight="bold"
                fontFamily="Arial, sans-serif"
              >
                {detection.class_name} {(detection.confidence * 100).toFixed(0)}%
              </text>
            </g>
          );
        })}
      </svg>
    </div>
  );
}
