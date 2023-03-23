from kubernetes import client


def get_active_reserve_cronjobs() -> list[client.V1CronJob]:
    batch_v1 = client.BatchV1Api()

    # Get all pipeline jobs in the anubis namespace
    jobs = batch_v1.list_namespaced_cron_job(
        namespace="anubis",
        label_selector="app.kubernetes.io/name=anubis,role=reserve-job",
    )
    return jobs.items
