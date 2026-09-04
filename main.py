from pathlib import Path

import looker_sdk
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / "looker-env" / ".env")
sdk = looker_sdk.init40()

PROJECT_NAME = "q_project"


def get_project_explores(project_name):
    print(f"Fetching details for project: '{project_name}'...\n")

    # 1. Fetch all LookML models in your instance
    all_models = sdk.all_lookml_models()

    # 2. Filter models that belong to your specific project
    project_models = [
        model for model in all_models
        if model.project_name == project_name
    ]

    if not project_models:
        print(f"No models found associated with project '{project_name}'.")
        return

    # 3. Iterate through each model and list its explores
    for model in project_models:
        print(f"==========================================")
        print(f"Model Name: {model.name}")
        print(f"Allowed Connections: {', '.join(model.allowed_db_connection_names or [])}")
        print(f"==========================================")

        explores = model.explores or []
        if not explores:
            print("  No explores defined in this model.")
            continue

        print("  Explores:")
        for explore in explores:
            # Basic info returned from the model object
            print(f"   - Name: {explore.name}")
            print(f"     Label: {explore.label}")

            # Optional: Call lookml_model_explore to get deeper details (dimensions/measures)
            # explore_detail = sdk.lookml_model_explore(lookml_model_name=model.name, explore_name=explore.name)
            # print(f"     Joined Views: {[join.name for join in explore_detail.joins]}")

        print("\n")


if __name__ == "__main__":
    get_project_explores(PROJECT_NAME)
