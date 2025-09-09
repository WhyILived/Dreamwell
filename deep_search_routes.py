from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from deep_search_service import perform_deep_search, get_deep_search_status, create_influencer_analysis_prompt
from models import db, User, Product, DeepSearchCache
import traceback

deep_search_bp = Blueprint('deep_search', __name__, url_prefix='/api/auth/deep-search')

@deep_search_bp.route('/analyze', methods=['POST'])
@jwt_required()
def analyze_video():
    """
    Start deep search analysis for a YouTube video.
    """
    try:
        data = request.get_json()
        video_url = data.get('video_url')
        channel_id = data.get('channel_id')
        product_id = data.get('product_id')
        custom_prompt = data.get('custom_prompt')

        if not video_url:
            return jsonify({'error': 'video_url is required'}), 400

        # Get user and product info for custom prompt
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        product = None
        
        if product_id:
            product = Product.query.filter_by(id=product_id, user_id=user_id).first()
            if not product:
                return jsonify({'error': 'Product not found'}), 404

        # Create custom prompt if not provided
        if not custom_prompt and product:
            custom_prompt = create_influencer_analysis_prompt(
                influencer_name=data.get('influencer_name', 'Unknown'),
                product_name=product.name
            )

        # Get company values and settings for comprehensive analysis
        company_values = data.get('company_values', [])
        company_country = data.get('company_country', 'US')
        is_luxury = data.get('is_luxury', False)
        
        # If no company values provided, try to get from user or use defaults
        if not company_values:
            if user and user.keywords:
                company_values = [k.strip() for k in user.keywords.split(',') if k.strip()]
            else:
                company_values = ['innovation', 'quality', 'sustainability']
        
        # If product exists, use its luxury setting
        if product and product.is_luxury is not None:
            is_luxury = product.is_luxury

        # Perform deep search
        result = perform_deep_search(
            video_url=video_url,
            channel_id=channel_id,
            custom_prompt=custom_prompt,
            company_values=company_values,
            company_country=company_country,
            is_luxury=is_luxury
        )

        return jsonify({
            'success': True,
            'data': result
        })

    except Exception as e:
        print(f"Error in analyze_video: {str(e)}")
        print(traceback.format_exc())
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@deep_search_bp.route('/status/<video_url>', methods=['GET'])
@jwt_required()
def get_status(video_url):
    """
    Get the status of a deep search analysis.
    """
    try:
        result = get_deep_search_status(video_url)
        
        if not result:
            return jsonify({
                'success': False,
                'error': 'No analysis found for this video'
            }), 404

        return jsonify({
            'success': True,
            'data': result
        })

    except Exception as e:
        print(f"Error in get_status: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@deep_search_bp.route('/history', methods=['GET'])
@jwt_required()
def get_analysis_history():
    """
    Get analysis history for the current user.
    """
    try:
        user_id = get_jwt_identity()
        
        # Get all deep search results (you might want to filter by user in the future)
        results = DeepSearchCache.query.order_by(DeepSearchCache.created_at.desc()).limit(50).all()
        
        return jsonify({
            'success': True,
            'data': [result.to_dict() for result in results]
        })

    except Exception as e:
        print(f"Error in get_analysis_history: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@deep_search_bp.route('/retry/<int:analysis_id>', methods=['POST'])
@jwt_required()
def retry_analysis(analysis_id):
    """
    Retry a failed analysis.
    """
    try:
        analysis = DeepSearchCache.query.get(analysis_id)
        if not analysis:
            return jsonify({'error': 'Analysis not found'}), 404

        if analysis.status not in ['failed', 'pending']:
            return jsonify({'error': 'Analysis is not in a retryable state'}), 400

        # Reset status and retry
        analysis.status = 'pending'
        analysis.error_message = None
        db.session.commit()

        # Perform the analysis again
        result = perform_deep_search(
            video_url=analysis.video_url,
            channel_id=analysis.channel_id,
            custom_prompt=None  # Use original prompt if needed
        )

        return jsonify({
            'success': True,
            'data': result
        })

    except Exception as e:
        print(f"Error in retry_analysis: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
