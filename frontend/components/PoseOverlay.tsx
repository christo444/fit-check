"use client";

import React from "react";

interface Landmark {
  id: number;
  name: string;
  x: number; // Normalized [0, 1]
  y: number; // Normalized [0, 1]
  z: number;
  visibility: number;
}

interface Connection {
  0: number; // Start landmark id
  1: number; // End landmark id
}

interface PoseOverlayProps {
  landmarks: Landmark[];
  connections: Connection[];
  imageWidth: number;
  imageHeight: number;
}

export default function PoseOverlay({
  landmarks,
  connections,
  imageWidth,
  imageHeight,
}: PoseOverlayProps) {
  // Get pixel coordinates from normalized values
  const getPixelCoords = (landmark: Landmark) => ({
    x: landmark.x * imageWidth,
    y: landmark.y * imageHeight,
  });

  // Color scheme for different body parts
  const getConnectionColor = (start: number, end: number): string => {
    // Face connections (0-10)
    if (start <= 10 && end <= 10) return "#FFD700"; // Gold
    
    // Upper body (11-22: shoulders, elbows, wrists, hands)
    if (start >= 11 && start <= 22 && end >= 11 && end <= 22) return "#00CED1"; // Turquoise
    
    // Torso (11-12 shoulders to 23-24 hips)
    if ((start >= 11 && start <= 12 && end >= 23 && end <= 24) ||
        (start >= 23 && start <= 24 && end >= 11 && end <= 12)) return "#FF6B6B"; // Red
    
    // Lower body (23-32: hips, knees, ankles, feet)
    if (start >= 23 && end >= 23) return "#4ECDC4"; // Teal
    
    return "#FFFFFF"; // Default white
  };

  // Landmark size based on visibility
  const getLandmarkRadius = (visibility: number): number => {
    const baseRadius = 4;
    return baseRadius * Math.max(0.3, visibility);
  };

  return (
    <svg
      className="absolute inset-0 w-full h-full pointer-events-none"
      viewBox={`0 0 ${imageWidth} ${imageHeight}`}
      preserveAspectRatio="none"
      style={{ zIndex: 10 }}
    >
      {/* Draw connections (skeleton) first */}
      {connections.map((connection, idx) => {
        const startLandmark = landmarks[connection[0]];
        const endLandmark = landmarks[connection[1]];
        
        if (!startLandmark || !endLandmark) return null;
        
        // Only draw if both landmarks are visible enough
        if (startLandmark.visibility < 0.3 || endLandmark.visibility < 0.3) {
          return null;
        }
        
        const start = getPixelCoords(startLandmark);
        const end = getPixelCoords(endLandmark);
        const color = getConnectionColor(connection[0], connection[1]);
        
        return (
          <line
            key={`connection-${idx}`}
            x1={start.x}
            y1={start.y}
            x2={end.x}
            y2={end.y}
            stroke={color}
            strokeWidth="3"
            strokeLinecap="round"
            opacity="0.8"
          />
        );
      })}

      {/* Draw landmarks (keypoints) on top */}
      {landmarks.map((landmark) => {
        // Only draw if visible enough
        if (landmark.visibility < 0.3) return null;
        
        const coords = getPixelCoords(landmark);
        const radius = getLandmarkRadius(landmark.visibility);
        
        return (
          <g key={`landmark-${landmark.id}`}>
            {/* Landmark circle */}
            <circle
              cx={coords.x}
              cy={coords.y}
              r={radius}
              fill="#FFFFFF"
              stroke="#000000"
              strokeWidth="1"
              opacity="0.9"
            />
            
            {/* Optional: Show landmark name on hover (for key landmarks) */}
            {landmark.visibility > 0.8 && [0, 11, 12, 23, 24].includes(landmark.id) && (
              <title>{landmark.name}</title>
            )}
          </g>
        );
      })}
    </svg>
  );
}
