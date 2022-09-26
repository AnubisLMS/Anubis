from kubernetes import client


def get_active_pipeline_jobs() -> list[client.V1Job]:
    batch_v1 = client.BatchV1Api()

    # Get all pipeline jobs in the anubis namespace
    jobs = batch_v1.list_namespaced_job(
        namespace="anubis",
        label_selector="app.kubernetes.io/name=submission-pipeline,role=submission-pipeline-worker",
    )
    return jobs.items
