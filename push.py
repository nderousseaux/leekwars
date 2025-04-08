"""
Force-push code to LeekWars by **erasing every AI file and folder** on the website
and copying everything from the local selected folder to the server
"""

import os
import requests

# Get .env variables
from dotenv import load_dotenv
load_dotenv()
URL = os.getenv("URL")
LOCAL_FOLDER = os.getenv("LOCAL_FOLDER")
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")

def irequest(token, method: str, url: str, **kwargs) -> requests.Response:
	"""
	Wrapper for requests to handle errors
	"""

	cookies = {
		"token": token
	}

	try:
		response = requests.request(method, url, cookies=cookies, **kwargs)
		response.raise_for_status()
		return response
	except requests.RequestException as e:
		print(f"Request failed: {e}")
		return None

def delete_all_remote(token) -> None:
	"""
	Delete all files and folders on server
	"""
	farmerAIs = irequest(token, "GET", f"{URL}/ai/get-farmer-ais").json()
	ais = farmerAIs["ais"]
	folders = farmerAIs["folders"]

	for ai in ais:
		irequest(token, "DELETE", f"{URL}/ai/delete/", data={
			"ai_id": ai["id"]
		})

	for folder in folders:
		irequest(token, "DELETE", f"{URL}/ai-folder/delete/", data={
			"folder_id": folder["id"]
		})

def fill_subtree(token, subtree_root: str, subtree_root_id: int) -> None:
	"""
	Fill the remote subtree to match its local counterpart
	Copy files and recursively fill subfolders
	"""
	subtree_root.split("/")[-1]

	for filename in os.listdir(subtree_root):
		# Files and directories starting with _ are considered to be hidden and are not pushed
		if filename.startswith("_"):
			continue

		file_full_path = os.path.join(subtree_root, filename)

		if os.path.isdir(file_full_path):
			folder_id = create_remote_folder(token, filename, subtree_root_id)
			fill_subtree(token, file_full_path, folder_id)
		else:
			with open(file_full_path, "r") as f:
				content = f.read()
				create_remote_file(token, filename, content, subtree_root_id)

def create_remote_folder(token, name: str, parent_id: int) -> int:
	"""
	Create a folder on server
	"""
	response = irequest(session, "POST", f"{URL}/ai-folder/new-name/", data={
		"name": name,
		"folder_id": parent_id
	})
	return response.json()["id"]

def create_remote_file(session, name: str, content: str, folder_id: int) -> None:
	"""
	Create a file on server
	"""
	response = irequest(session, "POST", f"{URL}/ai/new-name/", data={
		"name": name,
		"version": 4,
		"folder_id": folder_id
	})
	ai_id = response.json()["ai"]["id"]

	irequest(session, "POST", f"{URL}/ai/save/", data={
		"ai_id": ai_id,
		"code": content
	})

	irequest(session, "PUT", f"{URL}/ai/strict", data={
		"ai_id": ai_id,
		"strict": "true"
	})


if __name__ == "__main__":
	with requests.Session() as session:
		# Login to LeekWars
		res = irequest("", "POST", f"{URL}/farmer/login-token", data={
			"login": USERNAME,
			"password": PASSWORD
		})
		token = res.json()["token"]

		delete_all_remote(token)
		fill_subtree(token, LOCAL_FOLDER, 0)