from flask import Blueprint, jsonify, request
import logging
from duckduckgo_search import DDGS

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
