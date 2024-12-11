"""
Module that contains the command line app.

Typical usage example from command line:
        python cli.py
"""

import os
import argparse
import random
import string
from kfp import dsl
from kfp import compiler
import google.cloud.aiplatform as aip


GCP_PROJECT = os.environ["GCP_PROJECT"]
GCS_BUCKET_NAME = os.environ["GCS_BUCKET_NAME"]
BUCKET_URI = f"gs://{GCS_BUCKET_NAME}"
PIPELINE_ROOT = f"{BUCKET_URI}/pipeline_root/root"
GCS_SERVICE_ACCOUNT = os.environ["GCS_SERVICE_ACCOUNT"]
GCP_REGION = os.environ["GCP_REGION"]

DATA_CREATOR_IMAGE = "docker.io/hiyt/tripee-dataset-creator:0.2"
GEMINI_FINETUNER_IMAGE = "docker.io/hiyt/tripee-gemini-finetuner:0.2"

def generate_uuid(length: int = 8) -> str:
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=length))

def data_creator():
    print("data_creator()")

    # Define a Container Component
    @dsl.container_component
    def data_creator():
        container_spec = dsl.ContainerSpec(
            image=DATA_CREATOR_IMAGE,
            command=[],
            args=[
                "python",
                "cli.py",
                "--generate",
                "--prepare",
                "--save_prompt",
                "--upload",
            ],
        )
        return container_spec

    # Define a Pipeline
    @dsl.pipeline
    def data_creator_pipeline():
        data_creator()

    # Build yaml file for pipeline
    compiler.Compiler().compile(
        data_creator_pipeline, package_path="data_creator.yaml"
    )

    # Submit job to Vertex AI
    aip.init(project=GCP_PROJECT, staging_bucket=BUCKET_URI)

    job_id = generate_uuid()
    DISPLAY_NAME = "tripee-data-creator-" + job_id
    job = aip.PipelineJob(
        display_name=DISPLAY_NAME,
        template_path="data_creator.yaml",
        pipeline_root=PIPELINE_ROOT,
        enable_caching=False,
    )

    job.run(service_account=GCS_SERVICE_ACCOUNT)


def gemini_finetuner():
    print("gemini_finetuner()")

    # Define a Container Component for gemini_finetuner
    @dsl.container_component
    def gemini_finetuner():
        container_spec = dsl.ContainerSpec(
            image=GEMINI_FINETUNER_IMAGE,
            command=[],
            args=[
                "python",
                "cli.py",
                "--train",
            ],
        )
        return container_spec

    # Define a Pipeline
    @dsl.pipeline
    def gemini_finetuner_pipeline():
        gemini_finetuner()

    # Build yaml file for pipeline
    compiler.Compiler().compile(
        gemini_finetuner_pipeline, package_path="gemini_finetuner.yaml"
    )

    # Submit job to Vertex AI
    aip.init(project=GCP_PROJECT, staging_bucket=BUCKET_URI)

    job_id = generate_uuid()
    DISPLAY_NAME = "tripee-gemini_finetuner-" + job_id
    job = aip.PipelineJob(
        display_name=DISPLAY_NAME,
        template_path="gemini_finetuner.yaml",
        pipeline_root=PIPELINE_ROOT,
        enable_caching=False,
    )

    job.run(service_account=GCS_SERVICE_ACCOUNT)


def pipeline():
    print("pipeline()")
    # Define a Container Component for data creator
    @dsl.container_component
    def data_creator():
        container_spec = dsl.ContainerSpec(
            image=DATA_CREATOR_IMAGE,
            command=[],
            args=[
                "cli.py",
                "--generate",
                "--prepare",
                "--save_prompt",
                f"--upload",
            ],
        )
        return container_spec

    # Define a Container Component for gemini finetuner
    @dsl.container_component
    def gemini_finetuner():
        container_spec = dsl.ContainerSpec(
            image=GEMINI_FINETUNER_IMAGE,
            command=[],
            args=[
                "cli.py",
                "--train",
            ],
        )
        return container_spec

    # Define a Pipeline
    @dsl.pipeline
    def ml_pipeline():
        # Data Creator
        data_creator_task = (
            data_creator()
            .set_display_name("Data Creator")
            .set_cpu_limit("500m")
            .set_memory_limit("2G")
        )
        # Gemini Finetuner
        gemini_finetuner_task = (
            gemini_finetuner()
            .set_display_name("Gemini Finetuner")
            .after(data_creator_task)
        )

    # Build yaml file for pipeline
    compiler.Compiler().compile(ml_pipeline, package_path="pipeline.yaml")

    # Submit job to Vertex AI
    aip.init(project=GCP_PROJECT, staging_bucket=BUCKET_URI)

    job_id = generate_uuid()
    DISPLAY_NAME = "tripee-pipeline-" + job_id
    job = aip.PipelineJob(
        display_name=DISPLAY_NAME,
        template_path="pipeline.yaml",
        pipeline_root=PIPELINE_ROOT,
        enable_caching=False,
    )

    job.run(service_account=GCS_SERVICE_ACCOUNT)


def main(args=None):
    print("CLI Arguments:", args)

    if args.data_creator:
        data_creator()

    if args.gemini_finetuner:
        print("Gemini Finetuner")
        gemini_finetuner()

    if args.pipeline:
        pipeline()

if __name__ == "__main__":
    # Generate the inputs arguments parser
    # if you type into the terminal 'python cli.py --help', it will provide the description
    parser = argparse.ArgumentParser(description="Workflow CLI")

    parser.add_argument(
        "--data_creator",
        action="store_true",
        help="Run just the Data Creator",
    )
    parser.add_argument(
        "--gemini_finetuner",
        action="store_true",
        help="Run just the Gemini Finetuner",
    )
    parser.add_argument(
        "--pipeline",
        action="store_true",
        help="Tripee Pipeline",
    )

    args = parser.parse_args()

    main(args)
