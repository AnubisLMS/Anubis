from kubernetes import client

from anubis.env import env
from anubis.k8s.reserve.get import get_active_reserve_cronjobs
from anubis.models import ReservedIDETime


def create_reserve_ide_time(reserved_time: ReservedIDETime) -> client.V1CronJob:
    container = client.V1Container(
        image="registry.digitalocean.com/anubis/api:latest",
        env=[
            client.V1EnvVar(name="PYTHONPATH", value="/opt/app"),
            client.V1EnvVar(name="MPLCONFIGDIR", value="/tmp"),
            client.V1EnvVar(name="DEBUG", value="1" if env.debug else "0"),
            client.V1EnvVar(name="MIGRATE", value="0"),
            client.V1EnvVar(name="DOMAIN", value=env.DOMAIN),
            client.V1EnvVar(name="GITHUB_TOKEN", value_from=client.V1EnvVarSource(
                secret_key_ref=client.V1SecretKeySelector(name='git', key='token'))),
            client.V1EnvVar(name="SECRET_KEY", value_from=client.V1EnvVarSource(
                secret_key_ref=client.V1SecretKeySelector(name='api', key='secret-key'))),
            client.V1EnvVar(name="DATABASE_URI", value_from=client.V1EnvVarSource(
                secret_key_ref=client.V1SecretKeySelector(name='api', key='database-uri'))),
            client.V1EnvVar(name="DB_PASSWORD", value_from=client.V1EnvVarSource(
                secret_key_ref=client.V1SecretKeySelector(name='api', key='database-password'))),
            client.V1EnvVar(name="DB_HOST", value_from=client.V1EnvVarSource(
                secret_key_ref=client.V1SecretKeySelector(name='api', key='database-host'))),
            client.V1EnvVar(name="DB_PORT", value_from=client.V1EnvVarSource(
                secret_key_ref=client.V1SecretKeySelector(name='api', key='database-port'))),
            client.V1EnvVar(name="REDIS_PASS", value_from=client.V1EnvVarSource(
                secret_key_ref=client.V1SecretKeySelector(name='api', key='redis-password'))),
        ]
    )

    return client.V1CronJob(
        metadata=client.V1ObjectMeta(
            name=f"anubis-reserved-time-{reserved_time.id}",
            namespace="anubis",
            labels={
                "app.kubernetes.io/name": "anubis",
                "role":                   "reserve-job"
            }
        ),
        spec=client.V1CronJobSpec(
            concurrency_policy="Forbid",
            failed_jobs_history_limit=5,
            job_template=client.V1JobTemplateSpec(
                spec=client.V1JobSpec(
                    backoff_limit=6,
                    template=client.V1PodTemplateSpec(
                        spec=client.V1PodSpec(
                            containers=[container],
                            service_account="anubis-rpc"
                        )
                    )
                )
            ),
            schedule=reserved_time.schedule,
            time_zone="America/New_York"
        ),
    )


def sync_reserved_ide_time(reserved_time: ReservedIDETime) -> client.V1CronJob:
    active_reserve_cronjobs = get_active_reserve_cronjobs()
    already_exists = False

    for cronjob in active_reserve_cronjobs:
        pass
