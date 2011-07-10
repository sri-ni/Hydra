import os
import hydra
import unittest
import tempfile


class HydraTestCase(unittest.TestCase):
	
	def setUp(self):
		self.db_fd, hydra.app.config['DATABASE'] = tempfile.mkstemp()
		hydra.app.config['TESTING'] = True
		self.app = hydra.app.test_client()
		hydra.init_db()
		
	def tearDown(self):
		os.close(self.db_fd)
		os.unlink(hydra.app.config['DATABASE'])
		
	def login(self, username, password):
		return self.app.post('/login', data=dict(
			username=username,
			password=password
		), follow_redirects=True)
	
	def logout(self):
		return self.app.get('/logout', follow_redirects=True)
		
	# Testing functions 
	
	def test_empty_db(self):
		rv = self.app.get('/')
		assert 'No entries here so far' in rv.data
	
	def test_login_logout(self):
		rv = self.login('coderishi', 'coderishi')
		assert 'You are logged in' in rv.data
		rv = self.logout()
		assert 'You are logged out' in rv.data
		rv = self.login('code', 'code')
		assert 'Invalid username' in rv.data
		rv = self.login('coderishi', 'cdoe')
		assert 'Invalid password' in rv.data
		
	def test_messages(self):
		self.login('coderishi', 'coderishi')
		rv = self.app.post('/add', data=dict(
			liquid='h2o',
			qty='500 ml'
		), follow_redirects=True)
		assert 'No entries here so far' not in rv.data
		assert 'h2o' in rv.data
		assert '500 ml' in rv.data
	
		
if __name__ == '__main__':
	unittest.main()