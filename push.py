import os
import requests

name = "LeekIA"
folder = "leek-ia"

url = "https://leekwars.com/api"
c = {
	"token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE3NTI1ODY4MTMsImlkIjoxMjExNzUsImtlZXAiOnRydWUsImhhc2giOiIkMnkkMTAkU2dsTzF0TmV6cnhiYyIsImlwIjoiMTA5LjE0LjIzOC40IiwiaXNzIjoiaHR0cHM6XC9cL2xlZWt3YXJzLmNvbSIsImF1ZCI6Imh0dHBzOlwvXC9sZWVrd2Fycy5jb20ifQ.uwogTIybhONGfyPHqd2eAzEJLxkXO5Aglf2DwWAVOKk",
	"lang": "fr",
	"wt": "decoded null",
	"PHPSESSID": "gtb0a6odjv5m7c812huujegqav"
}

def create_file(name, content, folder=0):
	response = requests.post(f"{url}/ai/new-name/", cookies=c, data={
		"name": name,
		"version": 1,
		"folder_id": folder if folder else 0,
	})

	response = requests.post(f"{url}/ai/save/", cookies=c, data={
		"ai_id": response.json()["ai"]["id"],
		"code": content,
	})		


# Get ias 
response = requests.get(f"{url}/ai/get-farmer-ais", cookies=c)
ais = response.json()["ais"]

# Delete all ia on server
for i in ais:
	response = requests.delete(f"{url}/ai/delete/", cookies=c, data={
		"ai_id": i["id"],
	})

# For all file in the folder ./folder
for file in os.listdir(folder):
	# Create the file on the server
	with open(os.path.join(folder, file), "r") as f:
		content = f.read()
		name = file.split(".")[0]
		# Create the file on the server
		create_file(name, content, folder=0)

