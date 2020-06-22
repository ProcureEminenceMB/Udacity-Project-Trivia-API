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
			'success' : True,
			'categories' : {category.id : category.type for category in category_list}
		})


	@app.route('/questions')
	def get_questions():
		question_list = Question.query.order_by(Question.category).all()
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

	'''
	@TODO: 

	TEST: At this point, when you start the application
	you should see questions and categories generated,
	ten questions per page and pagination at the bottom of the screen for three pages.
	Clicking on the page numbers should update the questions. 
	'''

	'''
	@TODO: 
	Create an endpoint to DELETE question using a question ID. 

	TEST: When you click the trash icon next to a question, the question will be removed.
	This removal will persist in the database and when you refresh the page. 
	'''

	'''
	@TODO: 
	Create an endpoint to POST a new question, 
	which will require the question and answer text, 
	category, and difficulty score.

	TEST: When you submit a question on the "Add" tab, 
	the form will clear and the question will appear at the end of the last page
	of the questions list in the "List" tab.	
	'''

	'''
	@TODO: 
	Create a POST endpoint to get questions based on a search term. 
	It should return any questions for whom the search term 
	is a substring of the question. 

	TEST: Search by any phrase. The questions list will update to include 
	only question that include that string within their question. 
	Try using the word "title" to start. 
	'''

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