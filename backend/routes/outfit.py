from flask import Blueprint, jsonify
from services.storage_service import StorageService

outfit_bp = Blueprint("outfit", __name__)
storage_service = StorageService()


@outfit_bp.route("/outfit/<outfit_id>", methods=["GET"])
def get_outfit(outfit_id):
    """
    Get outfit details by ID
    
    Returns: outfit data including image_url, status, created_at, etc.
    """
    try:
        outfit = storage_service.get_outfit_by_id(outfit_id)

        if not outfit:
            return jsonify({"error": "Outfit not found"}), 404

        return jsonify(outfit), 200

    except Exception as e:
        print(f"Error fetching outfit: {str(e)}")
        return jsonify({"error": "Failed to fetch outfit", "details": str(e)}), 500


@outfit_bp.route("/outfits", methods=["GET"])
def get_all_outfits():
    """
    Get all outfits (for now, returns all; will add user filtering in auth phase)
    
    Returns: list of outfit objects
    """
    try:
        outfits = storage_service.get_all_outfits()
        return jsonify(outfits), 200

    except Exception as e:
        print(f"Error fetching outfits: {str(e)}")
        return jsonify({"error": "Failed to fetch outfits", "details": str(e)}), 500
