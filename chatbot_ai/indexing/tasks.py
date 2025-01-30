import os

import gitlab
import psycopg2
from celery import shared_task
from dotenv import load_dotenv

from indexing.celery_app.queues import QUEUES
from indexing.models import Indexing


@shared_task(queue=QUEUES.BACKGROUND_TASKS, acks_late=True)
def update_resource_content():
    print("Process update resource started...")

    load_dotenv()

    # Get the token from the environment
    ACCESS_TOKEN = os.getenv('GITLAB_PAT')
    GITLAB_URL = 'http://192.168.137.11:5000/'

    # Initialize GitLab connection
    gl = gitlab.Gitlab(GITLAB_URL, private_token=ACCESS_TOKEN)

    # Fetch all repositories (projects)
    projects = gl.projects.list(all=True)

    # Loop through each project and get README content
    for project in projects:
        try:
            readme = project.files.get(file_path='README.md', ref='master')
            current_last_commit = readme._attrs.get("last_commit_id")

            print(current_last_commit)
            # TODO: add logic to check if readme file has changed or not
            indexes = Indexing.objects.filter(project_name=project.name, file_name=readme.file_name)

            if indexes.exists():
                index = indexes.last()
                last_commit_id = index.last_commit_id

                if last_commit_id != current_last_commit:
                    # update the content and last commit
                    index.content = readme.decode().decode('utf-8')
                    index.last_commit_id = current_last_commit
                    index.save()

        except gitlab.exceptions.GitlabGetError:
            print(f"README.md not found in {project.name}.\n")
