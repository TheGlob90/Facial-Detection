import json

names = [
   "Alex", "Brandon", "Ben", "Srishti", "Dummy"
]

sens1 = {
   "device-name" : "ESP32",
   "alias" : "Front Door",
   "address" : "54:43:B2:2B:A3:E2"
}

sens2 = {
   "device-name" : "ESP32",
   "alias" : "Back Door",
   "address" : "unknown"
}

sensors = [sens1, sens2]

# a Python object (dict):
settings = {
  "code" : 1234,
  "face-timeout" : 100,
  "code-timeout" : 200,
  "sensors" : sensors,
  "names" : names
}

# Writing to sample.json
def writeJSON(filename, data):
  with open(str(filename), "w") as outfile:
      outfile.write(data)
  outfile.close()

# convert into JSON:
settings_json = json.dumps(settings, indent=4)
writeJSON("settings.json", settings_json)

# Opening JSON file
with open('settings.json', 'r') as openfile:
 
    # Reading from json file
    json_object = json.load(openfile)
 
print(json_object)
print(type(json_object))

name_temp = json_object["names"]
print("names: ")
print(name_temp)
print(type(names))

sens_temp = json_object["sensors"]
for entry in range(len(sens_temp)): 
  print("sensor: ",entry)
  print(sens_temp[entry]["alias"], sens_temp[entry]["address"])