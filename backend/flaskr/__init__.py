import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

# Create pagination for question GET route
QUESTIONS_PER_PAGE = 10

def paginate_question_list(request, selection):
	page = request.args.get('page', 1, type=int)
	start = (page - 1) * QUESTIONS_PER_PAGE
	end = start + QUESTIONS_PER_PAGE
	questions = [question.format() for question in selection]
	current_page_questions = questions[start:end]

	return current_page_questions

def create_app(test_config=None):
	# create and configure the app
	app = Flask(__name__)
	setup_db(app)
	
	# Set up CORS
	CORS(app, resources={r"/api/*" : {"origins" : "*"}})

	# Set access control
	@app.after_request
	def after_request(response):
		response.headers.add("Access-Control-Allow-Headers", "Content-Type,Authorization,true")
		response.headers.add("Access-Control-Allow-Methods", "DELETE,GET,OPTIONS,PATCH,POST,PUT")
		return response

	# Handle GET requests
	@app.route('/categories')
	def get_categories():
		category_list = Category.query.order_by(Category.type).all()

		# Force 404 error if no categories are found
		if len(category_list) == 0:
			abort(404)

		return jsonify({
			'success': True,
			'categories': {category.id : category.type for category in category_list}
		})

	@app.route('/questions')
	def get_questions():
		question_list = Question.query.order_by(Question.id).all()
		requested_questions = paginate_question_list(request, question_list)

		# Force 404 error if no questions are found
		if len(requested_questions) == 0:
			abort(404)

		return jsonify({
			'success': True,
			'questions': requested_questions,
			'total_questions': len(question_list),
			'current_category': 'All Categories',
			'categories': {category.id : category.type for category in Category.query.order_by(Category.type).all()}
		})
	# END Handle GET requests


	# Handle POST requests
	@app.route('/search', methods=['POST'])
	def search_questions():
		body = request.get_json()
		search_text = body.get('searchTerm', None)
		question_list = Question.query.filter(Question.question.ilike(f'%{search_text}%')).all()
		requested_questions = paginate_question_list(request, question_list)

		# Force 404 error if no questions are found
		if len(requested_questions) == 0:
			abort(404)

		return jsonify({
			'success': True,
			'questions': requested_questions,
			'totalQuestions': len(question_list),
			'currentCategory': ''
		})

	@app.route('/questions', methods = ['POST'])
	def add_question():
		data = request.get_json()
		add_question = data.get('question', None)
		add_answer = data.get('answer', None)
		add_difficulty = data.get('difficulty', None)
		add_category = data.get('category', None)

		# Force 400 error if any input field is left blank
		if add_question == None or add_answer == None or add_difficulty == None or add_category == None:
			abort(400)

		try:
			question_to_add = Question(add_question, add_answer, add_category, add_difficulty)
			question_to_add.insert()

			return jsonify({
				"success" : True
			})

		except:
			# Force 422 error if the question cannot be added
			abort(422)
	# END Handle POST requests

	'''
	@TODO: 
	TEST: When you click the trash icon next to a question, the question will be removed.
	This removal will persist in the database and when you refresh the page. 
	'''
	# Handle DELETE requests
	@app.route('/questions/<int:question_id>', methods=['DELETE'])
	def delete_question(question_id):
		question_result = Question.query.get(question_id)

		# Force 404 error if the desired question does not exist
		if question_result is None:
			abort(404)

		try:
			question_result.delete() 
			return jsonify({
				'success': True
			})
		except:
			# Force 422 error if the question cannot be deleted
			abort(422)
	# END Handle DELETE requests
	'''
	@TODO: 
	Create a GET endpoint to get questions based on category. 

	TEST: In the "List" tab / main screen, clicking on one of the 
	categories in the left column will cause only questions of that 
	category to be shown. 
	'''


	'''
	@TODO: 
	Create a POST endpoint to get questions to play the quiz. 
	This endpoint should take category and previous question parameters 
	and return a random questions within the given category, 
	if provided, and that is not one of the previous questions. 

	TEST: In the "Play" tab, after a user selects "All" or a category,
	one question at a time is displayed, the user is allowed to answer
	and shown whether they were correct or not. 
	'''

	# Error Handlers
	@app.errorhandler(400)
	def bad_request(error):
		return jsonify({
			"success": False,
			"error": 400,
			"message": "Bad Request"
		}), 400

	@app.errorhandler(404)
	def not_found(error):
		return jsonify({
			"success": False,
			"error": 404,
			"message": "Not Found"
		}), 404

	@app.errorhandler(422)
	def unprocessable(error):
		return jsonify({
			"success": False,
			"error": 422,
			"message": "Unprocessable"
		}), 422

	@app.errorhandler(405)
	def method_not_allowed(error):
		return jsonify({
			"success": False,
			"error": 405,
			"message": "Method Not Allowed"
		}), 405

	return app