from pathlib import Path
import sys
import json
import os

# to import from a parent directory we need to add that directory to the system path
csd = os.path.dirname(os.path.realpath(__file__))  # get current script directory
parent = os.path.dirname(csd)  # parent directory (should be the scrapers one)
sys.path.append(
    parent
)  # add parent dir to sys path so that we can import py_common from there

try:
    from py_common import log, graphql
except ModuleNotFoundError:
    print("You need to download the folder 'py_common' from the community repo! "
          "(CommunityScrapers/tree/master/scrapers/py_common)", file=sys.stderr)
    sys.exit()

JSONS_PATH = Path("jsons")

def get_scene_data(fragment_data):
    scene_id = fragment_data["id"]
    scene_title = fragment_data["title"]
    scene_files = []

    response = graphql.callGraphQL("""
    query FileInfoBySceneId($id: ID) {
      findScene(id: $id) {
        files {
          path
          size
        }
      }
    }""", {"id": scene_id})

    if response and response["findScene"]:
        log.info(response["findScene"])
        for f in response["findScene"]["files"]:
            scene_files.append({"filename": os.path.basename(f["path"]), "size": f["size"]})
        return {"id": scene_id, "title": scene_title, "files": scene_files}
    return {}

def mapValues(scene_data):
    output = {
        "title": "",
        "code" : "",
        "director":"",
        "movies": [],
        "date": "",
        "url": "",
        "image": "",
        "details": "",
        "performers": [],
        "tags": []
    }

    #JSON files should contain a "_source" parameter so we can determine their format
    formatVersion = float(scene_data['_source'].split('_')[-1][7:])

    if formatVersion >= 1:
        output['title'] = scene_data['title']
        output['date'] = scene_data['date'].split('T')[0]
        output['url'] = scene_data['url']
        output['image'] = scene_data['image']
        output['tags'] = list(map(lambda x: {"Name":x}, scene_data['tags']))
        output['studio'] = {"Name" : scene_data['studio'] }
        output['details'] = scene_date['details']
    
    # Schema v1.1 introduces a field for performers
    if formatVersion > 1.1:
        output['performers'] = list(map(lambda x: {"Name":x}, scene_data['performers']))
    return output


if sys.argv[1] == "fragment":
    fragment = json.loads(sys.stdin.read())
    scene = get_scene_data(fragment)
    filename = scene['files'][0]['filename'][:-3] + "json"
    filename = JSONS_PATH / filename
    try:
        with open(filename, 'rb') as f:
            scene_info = json.load(f)
            print(json.dumps(mapValues(scene_info)))
    except:
        print("{}")
