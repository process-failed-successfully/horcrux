import json

with open('feature_list.json', 'r') as f:
    data = json.load(f)

features = data.get('features', [])

pending_features = [f for f in features if not f.get('passes', False)]

if pending_features:
    print("Pending features:")
    for i, feature in enumerate(pending_features, 1):
        print(f"{i}. ID: {feature.get('id')}, Description: {feature.get('description', 'N/A')}")
else:
    print("No pending features found.")
