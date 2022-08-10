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
    def Quiz():

        try:

            JsonBody = request.get_json() #recieving the body of the request

            QuizCategory = JsonBody.get('quiz_category')
            AskedQuestions = JsonBody.get('previous_questions') 
            if QuizCategory is None:
                abort(422)
           
            else:
                ReadyQuestions = Question.query.filter_by(category=QuizCategory['id']).filter(Question.id.notin_((AskedQuestions))).all()

            SetQuestion = ReadyQuestions[random.randrange(0, len(ReadyQuestions))].format() if len(ReadyQuestions) > 0 else None

            return jsonify({
                'success': True,
                'question': SetQuestion
            })
        except:
            abort(422)
   
   
    @app.route('/questions', methods=['POST'])
    def AdddingQuestion():
        body = request.get_json()

        createNew_question = body.get('question')
        createNew_answer = body.get('answer')
        createNew_difficulty = body.get('difficulty')
        createNew_category = body.get('category')
        SearchItem = body.get('searchTerm', None)

        if SearchItem is None:
            if 'question' in body and 'answer' in body and 'difficulty' in body and 'category' in body:

                PostedQuestion = Question(question=createNew_question, answer=createNew_answer,
                                    difficulty=createNew_difficulty, category=createNew_category)
                PostedQuestion.insert()

                return jsonify({
                    'success': True,
                    'created': PostedQuestion.id
                })
            else: abort(422)

    
        else:
            if SearchItem is None: abort(400)
            SearchResult = Question.query.filter(
            Question.question.ilike(f'%{SearchItem}%')).all()

            return jsonify(
                {
                    'success': True,
                    'questions': [question.format() for question in SearchResult],
                    'all_questions': len(SearchResult),
                    'current_category': None
                }
                )
   
    @app.route('/categories/<int:CategoryId>/questions', methods=['GET'])
    def GettingCategoryQuestions(CategoryId):

        try:
            if CategoryId is not None:
                questions = Question.query.filter(Question.category == str(CategoryId)).all()
                categoryQuestions = [question.format() for question in questions]
                return jsonify({
                    'success': True,
                    'questions':categoryQuestions,
                    'all_questions': len(questions),
                    'current_category': CategoryId
                })
            else: abort(404)
        except:
            abort(404)
   
    @app.route('/categories')
    def GettingCategories():
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
    def GettingQuestions():
        choose = Question.query.order_by(Question.id).all()
        CurrentQuestions = paginate_questions(request, choose)

        categories = Category.query.order_by(Category.type).all()
        categoriesObject = {category.id: category.type for category in categories}
        if len(CurrentQuestions) == 0: abort(404)

        return jsonify({
            'success':True,
            'questions':CurrentQuestions,
            'all_questions':len(choose),
            'categories':categoriesObject,
            'current_category': None
        })
   
    @app.route("/questions/<QuestionId>", methods=['DELETE'])
    def DeleteQuestion(QuestionId):
        try:
            question = Question.query.get(QuestionId)
            question.delete()
            return jsonify({
                'success': True,
                'deleted': QuestionId
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

