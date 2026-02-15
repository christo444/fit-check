import axios from "axios";
import type { Outfit } from "./supabase";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:5000";

const api = axios.create({
  baseURL: API_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Upload image to backend
export async function uploadImage(file: File): Promise<{ outfit_id: string; image_url: string }> {
  const formData = new FormData();
  formData.append("image", file);

  const response = await api.post("/api/upload", formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });

  return response.data;
}

// Get outfit by ID
export async function getOutfitById(outfitId: string): Promise<Outfit> {
  const response = await api.get(`/api/outfit/${outfitId}`);
  return response.data;
}

// Get all outfits for a user
export async function getAllOutfits(): Promise<Outfit[]> {
  const response = await api.get("/api/outfits");
  return response.data;
}

// Health check
export async function checkBackendHealth(): Promise<boolean> {
  try {
    const response = await api.get("/health");
    return response.status === 200;
  } catch {
    return false;
  }
}

// Phase 2: Detection API
export interface Detection {
  class_id: number;
  class_name: string;
  confidence: number;
  bbox: {
    x1: number;
    y1: number;
    x2: number;
    y2: number;
    width: number;
    height: number;
  };
}

export interface DetectionResult {
  success: boolean;
  outfit_id: string;
  detections: Detection[];
  total_detections: number;
  image_dimensions: {
    width: number;
    height: number;
  };
}

// Run YOLO detection on outfit
export async function detectClothing(outfitId: string): Promise<DetectionResult> {
  const response = await api.post(`/api/detect/${outfitId}`);
  return response.data;
}

// Phase 3: Pose Estimation API
export interface Landmark {
  id: number;
  name: string;
  x: number; // Normalized [0, 1]
  y: number; // Normalized [0, 1]
  z: number;
  visibility: number;
}

export interface PoseConnection {
  0: number;
  1: number;
}

export interface Measurements {
  shoulder_width?: number;
  hip_width?: number;
  body_height?: number;
  left_arm_length?: number;
  right_arm_length?: number;
  left_leg_length?: number;
  right_leg_length?: number;
  torso_length?: number;
  shoulder_to_hip_ratio?: number;
  torso_to_leg_ratio?: number;
}

export interface PoseResult {
  success: boolean;
  outfit_id: string;
  landmarks: Landmark[];
  total_landmarks: number;
  connections: PoseConnection[];
  measurements: Measurements;
  image_dimensions: {
    width: number;
    height: number;
  };
}

// Run MediaPipe pose detection on outfit
export async function detectPose(outfitId: string): Promise<PoseResult> {
  const response = await api.post(`/api/pose/${outfitId}`);
  return response.data;
}

