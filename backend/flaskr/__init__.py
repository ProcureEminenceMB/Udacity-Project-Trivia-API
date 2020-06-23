import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random, copy

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

	@app.route('/categories/<int:category_id>/questions')
	def get_category_questions(category_id):

		# Convert category_id to string for db query
		category_id = str(category_id)

		question_list = Question.query.filter(Question.category == category_id).all()

		try:
			question_list = Question.query.filter(Question.category == category_id).all()
			requested_questions = paginate_question_list(request, question_list)

			if len(question_list) > 0:
				return jsonify({
					'success' : True,
					'questions' : requested_questions,
					'total_questions' : len(question_list),
					'current_category' : category_id
				})

			else:
				return jsonify({
					'success' : False,
					'questions' : requested_questions,
					'total_questions' : len(question_list),
					'current_category' : category_id
				})

		except:
			# Force 422 error if the selected category id can't process
			abort(422)

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

	@app.route('/questions', methods=['POST'])
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

	@app.route('/quizzes', methods=['POST'])
	def trivia_quiz():
		body = request.get_json()
		previous_questions = body.get('previous_questions', [])
		requested_category = body.get('quiz_category', 0)
		category_id = int(requested_category['id'])
		question_list = None
		new_question = False

		# Check for valid category id
		if category_id == 0:
			question_list = Question.query.all()

		elif category_id > 0:
			question_list = Question.query.filter(Question.category == requested_category['id']).all()

		else:
			# Force 422 error if the selected category isn't valid
			abort(422)

		# Force 422 error if no questions are found
		if len(question_list) <= 0:
			abort(422)

		modified_question_list = copy.copy(question_list)

		# Remove previously used questions from the db query results
		for question in question_list:
			if question.id in previous_questions:
				modified_question_list.remove(question) # Remove array item based on the value

		# If the question list isn't empty, select a random index and add to previous question list
		if len(modified_question_list) > 0:
			new_question = random.choice(modified_question_list).format()
		else:
			new_question = False

		return jsonify({
			"success": True,
			"question": new_question
		})
	# END Handle POST requests

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
	# END Error Handlers

	return app