import mlcroissant as mlc

file_path = "ACSED5YrSurvey_StatVarAgg.json"

try:
    # Initializing the dataset automatically triggers validation
    dataset = mlc.Dataset(jsonld=file_path)
    print("✅ The file is a valid Croissant metadata file.")
    ß
    # You can also inspect the validated metadata
    print(dataset.metadata.to_json())
    
except mlc.ValidationError as e:
    print("Validation Failed. Schema issues found:")
    print(e)
except Exception as e:
    print("An unexpected error occurred (e.g., invalid JSON format):")
    print(e)



# or using command line 
# mlcroissant validate --jsonld filename


