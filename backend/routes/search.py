from flask import Blueprint, jsonify, request
import logging
import os
from duckduckgo_search import DDGS
from serpapi import GoogleSearch

logger = logging.getLogger(__name__)

search_bp = Blueprint("search", __name__)

@search_bp.route("/shopping-search", methods=["GET"])
def shopping_search():
    """
    Search for products across e-commerce sites using DuckDuckGo
    
    GET /api/shopping-search?q=<keyword>
    """
    keyword = request.args.get("q", "")
    
    if not keyword:
        return jsonify({"error": "Missing search keyword"}), 400
        
    try:
        # Build search query targeting common fashion retailers + general query
        # "buy {keyword} clothing"
        query = f"buy {keyword} online clothing"
        
        results = []
        with DDGS() as ddgs:
            # max_results=4 to get a few good options
            ddgs_results = ddgs.text(query, max_results=4)
            
            if ddgs_results:
                for result in ddgs_results:
                    # Map the DDGS results (title, href, body) to our standard format
                    results.append({
                        "title": result.get("title", ""),
                        "url": result.get("href", ""),
                        "description": result.get("body", "")
                    })
                    
        return jsonify({
            "success": True,
            "keyword": keyword,
            "results": results
        }), 200
        
    except Exception as e:
        logger.error(f"Shopping search failed: {e}")
        return jsonify({
            "error": "Failed to search for products",
            "message": str(e)
        }), 500


@search_bp.route("/visual-search", methods=["POST"])
def visual_search():
    """
    Perform an exact visual search using Google Lens (via SerpApi)
    
    POST /api/visual-search
    Body: { "image_url": "..." }
    """
    data = request.get_json()
    if not data or "image_url" not in data:
        return jsonify({"error": "Missing image_url"}), 400
        
    image_url = data["image_url"]
    api_key = os.getenv("SERPAPI_KEY")
    
    if not api_key:
        return jsonify({"error": "SerpApi key is not configured"}), 500
        
    try:
        params = {
          "engine": "google_lens",
          "url": image_url,
          "api_key": api_key
        }
        
        search = GoogleSearch(params)
        results = search.get_dict()
        
        visual_matches = results.get("visual_matches", [])
        
        # Format the results to only include what we need
        formatted_results = []
        for match in visual_matches:
            # Only include results that have a shopping link and thumbnail
            if "link" in match and "thumbnail" in match:
                price_str = ""
                if "price" in match and "extracted_value" in match["price"]:
                    currency = match["price"].get("currency", "$")
                    price_str = f"{currency}{match['price']['extracted_value']}"
                    
                formatted_results.append({
                    "title": match.get("title", ""),
                    "url": match.get("link", ""),
                    "source": match.get("source", ""),
                    "price": price_str,
                    "thumbnail": match.get("thumbnail", "")
                })
                
        return jsonify({
            "success": True,
            "results": formatted_results[:8] # return top 8
        }), 200
        
    except Exception as e:
        logger.error(f"Visual search failed: {e}")
        return jsonify({
            "error": "Failed to perform visual search",
            "message": str(e)
        }), 500
