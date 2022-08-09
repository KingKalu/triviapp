from __future__ import absolute_import
import os
from sre_constants import AT_BOUNDARY
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, choose):
    page = request.args.get('page', 1, type=int)
    beginning = (page - 1) * QUESTIONS_PER_PAGE 
    ending = beginning + QUESTIONS_PER_PAGE

    questions = [question.format() for question in choose]
    current_questions = questions[beginning:ending]

    return current_questions

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(app)
    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,PUT,POST,DELETE,OPTIONS')
        return response
    """
    @TODO:
    Create an endingpoint to handle GET requests
    for all available categories.
    """


    @app.route('/quizzes', methods=['POST'])
    def play_quiz():

        try:

            body = request.get_json() #recieving the body of the request

            quiz_category = body.get('quiz_category')
            previous_questions = body.get('previous_questions') 
            if quiz_category is None:
                abort(422)
           
            else:
                available_questions = Question.query.filter_by(category=quiz_category['id']).filter(Question.id.notin_((previous_questions))).all()

            new_question = available_questions[random.randrange(0, len(available_questions))].format() if len(available_questions) > 0 else None

            return jsonify({
                'success': True,
                'question': new_question
            })
        except:
            abort(422)
   
   
    @app.route('/questions', methods=['POST'])
    def add_question():
        body = request.get_json()

        createNew_question = body.get('question')
        createNew_answer = body.get('answer')
        createNew_difficulty = body.get('difficulty')
        createNew_category = body.get('category')
        search_term = body.get('searchTerm', None)

        if search_term is None:
            if 'question' in body and 'answer' in body and 'difficulty' in body and 'category' in body:

                question = Question(question=createNew_question, answer=createNew_answer,
                                    difficulty=createNew_difficulty, category=createNew_category)
                question.insert()

                return jsonify({
                    'success': True,
                    'created': question.id,
                })
            else: abort(422)

    
        else:
            if search_term is None: abort(400)
            search_results = Question.query.filter(
            Question.question.ilike(f'%{search_term}%')).all()

            return jsonify(
                {
                    'success': True,
                    'questions': [question.format() for question in search_results],
                    'all_questions': len(search_results),
                    'current_category': None
                }
                )
   
    @app.route('/categories/<int:category_id>/questions', methods=['GET'])
    def retrieve_questions_by_category(category_id):

        try:
            if category_id is not None:
                questions = Question.query.filter(Question.category == str(category_id)).all()
                categoryQuestions = [question.format() for question in questions]
                return jsonify({
                    'success': True,
                    'questions':categoryQuestions,
                    'all_questions': len(questions),
                    'current_category': category_id
                })
            else: abort(404)
        except:
            abort(404)
   
    @app.route('/categories')
    def retrieve_categories():
        categories = Category.query.order_by(Category.type).all()
        all_categories = {
            categories[0].id:categories[0].type,
            categories[1].id:categories[1].type,
            categories[2].id:categories[2].type,
            categories[3].id:categories[3].type,
            categories[4].id:categories[4].type,
            categories[5].id:categories[5].type
            }

        if len(categories) == 0: abort(404)

        return jsonify({
            'success': True,
            'categories': all_categories
        })

   
    @app.route('/questions')
    def retrieve_questions():
        choose = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, choose)

        categories = Category.query.order_by(Category.type).all()
        categoriesObject = {category.id: category.type for category in categories}
        if len(current_questions) == 0: abort(404)

        return jsonify({
            'success':True,
            'questions':current_questions,
            'all_questions':len(choose),
            'categories':categoriesObject,
            'current_category': None
        })
   
    @app.route("/questions/<question_id>", methods=['DELETE'])
    def delete_question(question_id):
        try:
            question = Question.query.get(question_id)
            question.delete()
            return jsonify({
                'success': True,
                'deleted': question_id
            })
        except:
            abort(422)
   
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "success": False,
            "error": 404,
            "message": "resource not found"
        }), 404

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            "success": False,
            "error": 422,
            "message": "unprocessable"
        }), 422

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            "success": False,
            "error": 400,
            "message": "bad request"
        }), 400

    return app

