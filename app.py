import os
from flask import Flask, abort, request, jsonify, redirect
from src.models import setup_db, Paper, User, Discovery
from flask_cors import CORS
from flask_migrate import Migrate
from auth import AuthError, requires_auth

class RequestError(Exception):
    def __init__(self, status):
        self.status = status
    def __str__(self):
        return repr(self.status)

DISCOVERIES_PER_PAGE = int(os.getenv('DISCOVERIES_PER_PAGE', 10))


def paginate_discoveries(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * DISCOVERIES_PER_PAGE
    end = start + DISCOVERIES_PER_PAGE

    discoveries = [discovery.format() for discovery in selection]
    total_discoveries = len(discoveries)
    current_questions = discoveries[start: end]

    return current_questions, total_discoveries, page

def get_current_user_id():
    # This is a placeholder. You should implement the logic to get the ID 
    # of the currently logged-in user, e.g., from a session or a token.
    current_user_id = 1
    return current_user_id

def create_app(test_config=None):

    app = Flask(__name__)
    setup_db(app)
    CORS(app)

    @app.route('/')
    def index():
        return "Please go to the Login Page"

    @app.route('/login')
    def login():
        auth0_login_url = (
        f"https://{os.getenv('AUTH0_DOMAIN')}/authorize?"
        f"audience={os.getenv('API_AUDIENCE')}&"
        f"response_type=token&"
        f"client_id={os.getenv('CLIENTID')}&"
        f"redirect_uri={os.getenv('REDIRECT_URI')}"
    )
        return redirect(auth0_login_url)
    
    @app.route('/logout')
    def logout():
        return "This is the Logout Page"
    
    @app.route('/playground')
    @requires_auth('get:discoveries')
    def get_feeds(payload):
        try: 
            selection = Discovery.query.order_by(Discovery.date_posted).all()

            if len(selection) == 0:
                return jsonify({"success": True, "message": "No Related Discoveries Found"})
            
            current_discoveries, total_discoveries, current_page = paginate_discoveries(request, selection)

            if len(current_discoveries)==0:
                abort(422)
            
            # Format the discoveries
            # print(type(current_discoveries[0]))
            # formatted_discoveries = [discovery.format() for discovery in current_discoveries]

            # Return the paginated data along with pagination metadata
            return jsonify({
                'success': True,
                'discoveries': current_discoveries,
                'total_discoveries': total_discoveries,
                'current_page': current_page,
            })

        except Exception as e:
            print(e)
            abort(422)
    
    @app.route('/user/<int:id>')
    @requires_auth('get:user')
    def get_user(payload, id):
        try:
            user = User.query.get(id)
            if user is None:
                raise RequestError(404)

            formatted_user = user.format()

            return jsonify({
                'success': True,
                'user': formatted_user,
            }) 
        except RequestError as error:
            abort(error.status)

        except Exception as e:
            print(f"Error: {e}")  # Consider using a logger in a production application
            abort(422)
    
    
    @app.route('/playground/create', methods=['POST'])
    @requires_auth('post:discovery')
    def create_discovery(payload):
        try:
            caption = request.form.get('caption')
            paper_title = request.form.get('paper_title')
            paper_link = request.form.get('paper_link')
            user_id = get_current_user_id()

            # Validate input
            if not caption or not paper_title or not paper_link:
                raise RequestError(400)

            paper_found = Paper.query.filter_by(title=paper_title).one_or_none()
            
            if paper_found is not None:
                new_discovery = Discovery(caption, user_id, paper_found.id)
            else:
                new_paper = Paper(paper_title, paper_link)
                new_paper.insert()
                new_discovery = Discovery(caption, user_id, new_paper.id)
            
            new_discovery.insert()

            return jsonify({
                'success': True,
                'new_discovery': new_discovery.format()
            })
        
        except RequestError as error:
            abort(error.status)

        except Exception as e:
            print(f"Error: {e}")
            abort(422)



    @app.route('/playground/search', methods=['POST'])
    @requires_auth('search:discoveries')
    def search_discoveries(payload):
        try:
            search_term = request.form.get('search_term', '')
            selection = Discovery.query.join(Paper).filter(Paper.title.ilike(f'%{search_term}%')).order_by(Discovery.date_posted).all()

            if len(selection) == 0:
                return jsonify({"success": True, "message": "No Related Discoveries Found"})

            current_discoveries, total_discoveries, current_page = paginate_discoveries(request, selection)

            if len(current_discoveries) == 0:
                abort(422)

            # Format the discoveries
            # formatted_discoveries = [discovery.format() for discovery in current_discoveries]

            # Return the paginated data along with pagination metadata
            return jsonify({
                'success': True,
                'discoveries': current_discoveries,
                'total_discoveries': total_discoveries,
                'current_page': current_page,
            })

        except Exception as e:
            print(f"Error: {e}")
            abort(422)

    @app.route('/playground/edit/<int:discovery_id>', methods=['PATCH'])
    @requires_auth('patch:discovery')
    def edit_discovery(payload, discovery_id):
        try:
            discovery = Discovery.query.get(discovery_id)

            if not discovery:
                raise RequestError(404)

            # Update discovery data
            if 'caption' in request.form:
                discovery.caption = request.form['caption']
            
            discovery.update()

            return jsonify({
                'success': True,
                'discovery': discovery.format()
            })
        except RequestError as error:
            abort(error.status)

        except Exception as e:
            print(f"Error: {e}")
            abort(422) 

    @app.route('/playground/delete/<int:discovery_id>', methods=['DELETE'])
    @requires_auth('delete:discovery')
    def delete_discovery(payload, discovery_id):
        try:
            discovery = Discovery.query.get(discovery_id)

            if not discovery:
                raise RequestError(404)

            discovery.delete()

            return jsonify({
                'success': True,
                'deleted': discovery_id
            })
        except RequestError as error:
            abort(error.status)

        except Exception as e:
            print(f"Error: {e}")
            abort(422)



    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'resource not found'
        }), 404 
    
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'error': 400,
            'message': 'bad request'
        }), 400
    
    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            'success': False,
            'error': 422,
            'message': 'unprocessable'
        }), 422
    
    @app.errorhandler(405)
    def method_not_allowed(error):
        return jsonify({
            "success": False, 
            "error": 405,
            "message": "method not allowed"
        }), 405

    @app.errorhandler(AuthError)
    def authError(error):
            return jsonify({
            "success": False,
            "error": error.error,
        }),error.status_code


    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
