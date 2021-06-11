from apiclient import discovery
from httplib2 import Http
from oauth2client import client, file, tools
from urllib.parse import urlparse, parse_qs

# define path variables
credentials_file_path = './credentials/credentials.json'
clientsecret_file_path = './credentials/client_secret.json'

# define API scope
SCOPE = 'https://www.googleapis.com/auth/drive'

# define store
store = file.Storage(credentials_file_path)
credentials = store.get()
# get access token
if not credentials or credentials.invalid:
    flow = client.flow_from_clientsecrets(clientsecret_file_path, SCOPE)
    credentials = tools.run_flow(flow, store)

http = credentials.authorize(Http())
drive = discovery.build('drive', 'v3', http=http)

def getFileId(url):
	parse = urlparse(url)
	fileId = ""
	if "/file/u/" in parse.path:
		fileId = parse.path.split("/")[5]
	elif "/uc" in parse.path:
		fileId = parse_qs(parse.query)['id'][0]
	else:
		fileId = url
	return fileId

# bypass limit function
def bypassLimit(url):
	service = drive
	folderId = "[YOUR_FOLDER_ID]"
	fileId = getFileId(url)
	try:
		sourceFile = service.files().get(fileId=fileId, fields="id,name,md5Checksum").execute()
	except:
		return "Error: permission denied or file not found"
	fileList = service.files().list(q="'"+folderId+"' in parents",fields="files(id,name,md5Checksum,webViewLink)").execute()
	for availFile in fileList['files']:
		if sourceFile['md5Checksum'] == availFile['md5Checksum']:
			resp = "Name: " + availFile['name'] + "\nMD5: " + availFile['md5Checksum'] + "\nLink: " + availFile['webViewLink']
			return resp
	# print("Not Found")
	try:
		copy = service.files().copy(fileId=fileId, body={"parents":[folderId]}, fields="id,name,md5Checksum,webViewLink").execute()
		permission = {"role": "reader","type": "anyone"}
		perm = service.permissions().create(fileId=copy['id'], body=permission).execute()
		resp = "Name: " + copy['name'] + "\nMD5: " + copy['md5Checksum'] + "\nLink: " + copy['webViewLink']
		return resp
	except:
		return "Error: unknown"
