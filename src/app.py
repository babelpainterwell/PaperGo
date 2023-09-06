from flask import Flask, jsonify, request, abort, render_template, redirect, url_for, session, make_response
from flask_sqlalchemy import SQLAlchemy
from models import setup_db, Paper, User, Discovery
from flask_cors import CORS
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity, create_access_token
import os 
from dotenv import find_dotenv, load_dotenv
from os import environ as env
from flask_bcrypt import Bcrypt
# from flask_wtf import CSRFProtect
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.llms import OpenAI
from langchain.chains.question_answering import load_qa_chain
from langchain.callbacks import get_openai_callback
import pickle
from io import BytesIO
import base64


bcrypt = Bcrypt()
# csrf = CSRFProtect()

ENV_FILE = find_dotenv()
if ENV_FILE:
    load_dotenv(ENV_FILE)


class RequestError(Exception):
    def __init__(self, status):
        self.status = status
    def __str__(self):
        return repr(self.status)

def get_current_user_id():
    # current_user = get_jwt_identity()
    # # Assuming each user has a unique username
    # user = User.query.filter_by(email=current_user).first()
    # return user.id if user else None
    return 1


def create_app(test_config=None):

    app = Flask(__name__)
    # csrf.init_app(app)
    # app.secret_key = env.get('SESSION_SECRET_KEY')
    # jwt = JWTManager(app)
    # app.config['JWT_SECRET_KEY'] = env.get("JWT_SECRET_KEY")
    # app.config['JWT_TOKEN_LOCATION'] = ['cookies']
    # app.config['JWT_COOKIE_CSRF_PROTECT'] = True
    setup_db(app)
    CORS(app)

    @app.route('/')
    def index():
        return render_template('index.html')

    
    @app.route('/signup', methods=['GET', 'POST'])
    def signup():
        if request.method == 'GET':
            return render_template('signup.html')

        if request.method == 'POST':

            email = request.form.get('email')
            hashed_password = bcrypt.generate_password_hash(request.form.get('password')).decode("utf-8")
            name = request.form.get('name')
            institution = request.form.get('institution')
            profile_description = request.form.get('profile_description')

            # Check if the email is already taken
            existing_user = User.query.filter_by(email=email).first()

            if existing_user:
                return jsonify({"success": False, "msg": "Email already in use"}), 400

            new_user = User(
                email=email,
                password=hashed_password,
                name=name,
                institution=institution,
                profile_description=profile_description
            )

            new_user.insert()

            return redirect(url_for('login'))  # Redirect to the login page after signup

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'GET':
            return render_template('login.html')

        if request.method == 'POST':
            email = request.form.get('email')
            password = request.form.get('password')

            user = User.query.filter_by(email=email).first()
            if user and bcrypt.check_password_hash(user.password, password):
                access_token = create_access_token(identity=user.id)
                # session["user"] = access_token
                response = make_response(redirect(url_for('get_discoveries')))
                response.set_cookie('access_token_cookie', access_token, httponly=True, secure=False)
                return response
            else:
                return jsonify({"msg": "Invalid credentials"}), 401
    
    # @app.route('/token', methods=['POST'])
    # def create_token():
    #     email = request.json.get('email', None)
    #     password = request.json.get('password', None)

    #     user = User.query.filter_by(email=email).first()
    #     if user and bcrypt.check_password_hash(user.password, password):
    #         access_token = create_access_token(identity=user.id)
    #     return jsonify(access_token=access_token)
    
    @app.route('/logout')
    def logout():
        # session.clear()
        return redirect(url_for('index'))


    @app.route('/discoveries', methods=['GET'])
    # @jwt_required()
    def get_discoveries():
        page = request.args.get('page', 1, type=int)
        per_page = 10  
        
        try:
            paginated_discoveries = Discovery.query.paginate(page=page, per_page=per_page)

            if paginated_discoveries.total == 0:
                # return jsonify({"success": True, "message": "No Related Discoveries Found"})
                return render_template('no_discoveries.html')

            output = []

            for discovery in paginated_discoveries.items:
                paper_title = discovery.paper.title if discovery.paper else "N/A"
                paper_link = discovery.paper.link if discovery.paper else "N/A"

                output.append({
                    'id': discovery.id, 
                    'caption': discovery.caption,
                    'paper_title': paper_title,
                    'paper_link': paper_link
                })
            print(output)

            if len(output) == 0:
                raise RequestError(404)

            # output here is a list of dictionary 
            return render_template('discoveries.html', discoveries=output)

        except RequestError as e:
            return jsonify({"success": False, "error": str(e)}), e.status
        except Exception as e:
            print(e)
            abort(422)

    
    @app.route('/discoveries/add', methods=['POST'])
    # @jwt_required()
    def add_discovery():
        try:
            caption = request.form.get('caption')
            paper_title = request.form.get('paper_title')
            paper_link = request.form.get('paper_link')
            user_id = get_current_user_id()

            if user_id is None:
                raise RequestError(401)

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

            all_discoveries = Discovery.query.order_by(Discovery.date_posted.desc()).all()

            return redirect(url_for('get_discoveries'))
        
        except RequestError as error:
            abort(error.status)

        except Exception as e:
            print(f"Error: {e}")
            abort(422)


    @app.route('/discoveries/edit/<int:discovery_id>', methods=['PATCH'])
    # @jwt_required() # Uncomment if you are using JWTs
    def edit_discovery(discovery_id):
        try:
            discovery = Discovery.query.get(discovery_id)
            current_user_id = get_current_user_id()

            if not discovery:
                abort(404)
            
            if discovery.user_id != current_user_id:
                abort(403)

            data = request.json
            if 'caption' in data:
                discovery.caption = data['caption']
            
            # Assuming `update` is a method you have on your Discovery model that commits the changes to the database
            discovery.update()

            return jsonify({'message': 'Successfully updated'}), 200
        except Exception as e:
            print(f"Error: {e}")
            abort(422)
    

    @app.route('/discoveries/delete/<int:discovery_id>', methods=['DELETE'])
    # @jwt_required()
    def delete_discovery(discovery_id):
        try:
            discovery = Discovery.query.get(discovery_id)
            current_user_id = get_current_user_id()

            if not discovery:
                raise RequestError(404)
            
            if discovery.user_id != current_user_id:
                raise RequestError(403)

            discovery.delete()

            return redirect(url_for("get_discoveries"))
        except RequestError as error:
            abort(error.status)

        except Exception as e:
            print(f"Error: {e}")
            abort(422)
    
    @app.route('/chat', methods=['POST'])
    def chat():
        pdf_file = request.files['pdf']
        query = request.form['query']

        # Decoding the Base64 PDF into a BytesIO object
        pdf_file = BytesIO(base64.b64decode(pdf_file))

        pdf_reader = PdfReader(pdf_file)
        text = ''
        for page in pdf_reader.pages:
            text += page.extract_text()

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size = 1000,
            chunk_overlap = 200,
            length_function = len
        )

        chunks = text_splitter.split_text(text = text)

        store_name = pdf_file.filename[:-4]

        if os.path.exists(f'{store_name}.pkl'):
            with open(f'{store_name}.pkl', 'rb') as f:
                VectorStore = pickle.load(f)
        else:
            embeddings = OpenAIEmbeddings()
            VectorStore = FAISS.from_texts(chunks, embedding=embeddings)
            with open(f'{store_name}.pkl', 'wb') as f:
                pickle.dump(VectorStore, f)

        if query:
            docs = VectorStore.similarity_search(query=query, k=3)

            llm = OpenAI()
            chain = load_qa_chain(llm=llm, chain_type='stuff')
            with get_openai_callback() as cb:
                response = chain.run(input_documents=docs, question=query)

            return jsonify({"response": response})
    
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


    return app

app = create_app()


if __name__ == "__main__":
    app.run(debug=True)



    # @app.route('/login', methods=['POST'])
    # def login():
    #     email = request.form.get('email')
    #     password = request.form.get('password')

    #     user = User.query.filter_by(email=email).first()

    #     if user and bcrypt.check_password_hash(user.password, password):
    #         access_token = create_access_token(identity=email)
    #         return jsonify(access_token=access_token), 200
    #     else:
    #         return jsonify({"msg": "Invalid credentials"}), 401