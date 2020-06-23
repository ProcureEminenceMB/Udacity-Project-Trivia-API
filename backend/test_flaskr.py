import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
	"""This class represents the trivia test case"""

	def setUp(self):
		"""Define test variables and initialize app."""
		self.app = create_app()
		self.client = self.app.test_client
		self.database_name = "trivia_test"
		self.database_path = "postgres://{}/{}".format('admin:admin@localhost:5432', self.database_name)
		setup_db(self.app, self.database_path)

		# Sample question
		self.new_question = {
			'question': 'What type of paint does Bob Ross use?',
			'answer': 'Oil',
			'difficulty': '2',
			'category': '2'
		}

		# Binds the app to the current context
		with self.app.app_context():
			self.db = SQLAlchemy()
			self.db.init_app(self.app)
			self.db.create_all()# Create all tables
	
	def tearDown(self):
		"""Executed after reach test"""
		pass

	# Test GET routes
	def test_get_full_category_list(self):
		res = self.client().get('/categories')
		data = json.loads(res.data)

		self.assertEqual(res.status_code, 200)
		self.assertEqual(data['success'], True)
		self.assertTrue(len(data['categories']))

	def test_get_question_list_in_category(self):
		res = self.client().get('/categories/1/questions')
		data = json.loads(res.data)

		self.assertEqual(res.status_code, 200)
		self.assertEqual(data['success'], True)
		self.assertTrue(len(data['questions']))
		self.assertTrue(data['total_questions'])

	def test_get_full_question_list(self):
		res = self.client().get('/questions')
		data = json.loads(res.data)

		self.assertEqual(res.status_code, 200)
		self.assertEqual(data['success'], True)
		self.assertTrue(len(data['questions']))
		self.assertTrue(data['total_questions'])
	# END Test GET routes


	# Test POST routes
	def test_get_search_results(self):
		res = self.client().post('/search', json={'searchTerm': 'title'})
		data = json.loads(res.data)

		self.assertEqual(res.status_code, 200)
		self.assertEqual(data['success'], True)
		self.assertTrue(len(data['questions']))
		self.assertTrue(data['totalQuestions'])

	def test_add_question(self):
		res = self.client().post('/questions', json=self.new_question)
		data = json.loads(res.data)

		self.assertEqual(res.status_code, 200)
		self.assertEqual(data['success'], True)

	def test_trivia_quiz(self):
		selected_quiz_category = {
			'quiz_category': {
				'type': 'Science',
				'id': 1
			}
		}
		res = self.client().post('/quizzes', json=selected_quiz_category)
		data = json.loads(res.data)

		self.assertEqual(res.status_code, 200)
		self.assertEqual(data['success'], True)
		self.assertTrue(data['question'])
	# END Test POST routes


	# Test DELETE routes
	def test_delete_question(self):
		# Get id of one question in the database
		res = self.client().get('questions?page=1')
		question_id = json.loads(res.data)['questions'][0]['id']
		
		res = self.client().delete(f'/questions/{question_id}')
		data = json.loads(res.data)

		self.assertEqual(res.status_code, 200)
		self.assertEqual(data['success'], True)
	# END Test DELETE routes


	# Test error handlers
	def test_400_error(self):
		res = self.client().post('/questions', json={})
		data = json.loads(res.data)

		self.assertEqual(res.status_code, 400)
		self.assertEqual(data['success'], False)
		self.assertEqual(data['message'], 'Bad Request')

	def test_404_error(self):
		res = self.client().get('/category')
		data = json.loads(res.data)

		self.assertEqual(res.status_code, 404)
		self.assertEqual(data['success'], False)
		self.assertEqual(data['message'], 'Not Found')

	def test_422_error(self):
		invalid_question = {
			'question': 'Where do you look to see the sky?',
			'answer': 'Down',
			'difficulty': 'F',
			'category': '1'
		}
		res = self.client().post('/questions', json=invalid_question)
		data = json.loads(res.data)

		self.assertEqual(res.status_code, 422)
		self.assertEqual(data['success'], False)
		self.assertEqual(data['message'], 'Unprocessable')

	def test_405_error(self):
		res = self.client().put('/questions')
		data = json.loads(res.data)

		self.assertEqual(res.status_code, 405)
		self.assertEqual(data['success'], False)
		self.assertEqual(data['message'], 'Method Not Allowed')
	# END Test error handlers

# Make the tests conveniently executable
if __name__ == "__main__":
	unittest.main()