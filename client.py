import requests

# response = requests.post('http://localhost:5000/posted/',
#                          json={'title': 'this one', 'description': 'this one', 'owner': 'My'}
#                          )


# response = requests.get('http://localhost:5000/posted/15')


response = requests.patch('http://localhost:5000/posted/12', json={'description': 'test patch'})


# response = requests.delete('http://localhost:5000/posted/14')


print(response.text)
print(response.status_code)
