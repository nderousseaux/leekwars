"""
Force-push code to LeekWars by **erasing every AI file and folder** on the website
and copying everything from the local selected folder to the server

Instructions: Setup the session cookie credentials in creds.py, and change the local folder \
	to push to the remote (LOCAL_FOLDER="ai-code" by default)
"""

import os
import requests

import creds


URL = "https://leekwars.com/api"
SESSION_COOKIE = {
	"token": creds.TOKEN,
	"lang": "fr",
	"wt": "decoded null",
	"PHPSESSID": creds.PHPSESSID
}

LOCAL_FOLDER = "src"


def delete_all_remote() -> None:
	"""
	Delete all files and folders on server
	"""
	farmerAIs = requests.get(f"{URL}/ai/get-farmer-ais", cookies=SESSION_COOKIE).json()
	ais = farmerAIs["ais"]
	folders = farmerAIs["folders"]

	for ai in ais:
		requests.delete(f"{URL}/ai/delete/", cookies=SESSION_COOKIE, data={
			"ai_id": ai["id"]
		})

	for folder in folders:
		requests.delete(f"{URL}/ai-folder/delete/", cookies=SESSION_COOKIE, data={
			"folder_id": folder["id"]
		})

def fill_subtree(subtree_root: str, subtree_root_id: int) -> None:
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
			folder_id = create_remote_folder(filename, subtree_root_id)
			fill_subtree(file_full_path, folder_id)
		else:
			with open(file_full_path, "r") as f:
				content = f.read()
				create_remote_file(filename, content, subtree_root_id)

def create_remote_folder(name: str, parent_id: int) -> int:
	"""
	Create a folder on server
	"""
	response = requests.post(f"{URL}/ai-folder/new-name/", cookies=SESSION_COOKIE, data={
		"name": name,
		"folder_id": parent_id
	})
	return response.json()["id"]

def create_remote_file(name: str, content: str, folder_id: int) -> None:
	"""
	Create a file on server
	"""
	response = requests.post(f"{URL}/ai/new-name/", cookies=SESSION_COOKIE, data={
		"name": name,
		"version": 4,
		"folder_id": folder_id
	})
	ai_id = response.json()["ai"]["id"]

	response = requests.post(f"{URL}/ai/save/", cookies=SESSION_COOKIE, data={
		"ai_id": ai_id,
		"code": content
	})

	response = requests.put(f"{URL}/ai/strict/", cookies=SESSION_COOKIE, data={
		"ai_id": ai_id,
		"strict": True
	})


if __name__ == "__main__":
	delete_all_remote()
	fill_subtree(LOCAL_FOLDER, 0)