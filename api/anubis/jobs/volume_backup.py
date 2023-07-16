import json
import time
import os
import jinja2
from parse import parse
from datetime import datetime
import argparse
from pathlib import Path
# from tqdm import tqdm

root = os.path.dirname(__file__)

volumes = json.load(open("/tmp/volumes.json"))
netids = [parse("ide-volume-{}", v)[0] for v in volumes]
jobs_dir = Path("/tmp/jobs/")
now = datetime.now().strftime("%Y%m%d-%H%M%S")


def parse_args() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser("Anubis Volume Backup (avb)")
    parser.set_defaults(func=None)
    sub_parser = parser.add_subparsers()

    gen_parser = sub_parser.add_parser("gen")
    gen_parser.add_argument("--backup_host", default="s3.backup.anubis-lms.io")
    gen_parser.add_argument(
        "--backup_host_path", default="/home/anubis/backups/volumes"
    )
    gen_parser.add_argument("--id", dest="identifier", default=now, help="")
    gen_parser.add_argument(
        "--ttl", "-t", dest="ttl", default=30, type=int, help="TTL of job"
    )
    gen_parser.set_defaults(func=gen)

    backup_parser = sub_parser.add_parser("backup")
    backup_parser.add_argument(
        "--jobs",
        "-j",
        dest="jobs",
        default=10,
        type=int,
        help="Number of jobs to batch",
    )
    backup_parser.add_argument(
        "--wait",
        "-w",
        dest="wait",
        default=60,
        type=int,
        help="Amount of time to wait between batches",
    )
    backup_parser.add_argument(
        "--filter", "-f", dest="filter", default=None, type=str, help="Filter by netid"
    )
    backup_parser.add_argument(
        "--yes", "-y", dest="yes", action="store_true", help="Skip confirmation"
    )
    backup_parser.add_argument("--id", dest="identifier", default="latest", help="")
    backup_parser.set_defaults(func=backup)

    restore_parser = sub_parser.add_parser("restore")
    restore_parser.add_argument(
        "--jobs",
        "-j",
        dest="jobs",
        default=10,
        type=int,
        help="Number of jobs to batch",
    )
    restore_parser.add_argument(
        "--wait",
        "-w",
        dest="wait",
        default=60,
        type=int,
        help="Amount of time to wait between batches",
    )
    restore_parser.add_argument(
        "--filter", "-f", dest="filter", default=None, type=str, help="Filter by netid"
    )
    restore_parser.add_argument(
        "--yes", "-y", dest="yes", action="store_true", help="Skip confirmation"
    )
    restore_parser.add_argument("--id", dest="identifier", default="latest", help="")
    restore_parser.set_defaults(func=restore)

    return parser


def initialize_gen(args):
    backup_host = args.backup_host
    backup_host_path = Path(args.backup_host_path) / args.identifier

    jobs_identifier_dir = jobs_dir / args.identifier
    backup_job_dir = jobs_identifier_dir / "backup"
    restore_job_dir = jobs_identifier_dir / "restore"
    backup_job_dir.mkdir(exist_ok=True, parents=True)
    restore_job_dir.mkdir(exist_ok=True, parents=True)

    latest = jobs_dir / "latest"
    latest.unlink(missing_ok=True)
    latest.symlink_to(Path(args.identifier), target_is_directory=True)

    print(f"Using config:")
    print(f"  {args.identifier=}")
    print(f"  {backup_host=}")
    print(f"  {backup_host_path=}")

    backup_template = jinja2.Template(
        (root / Path("jinja_templates/backup-job.yml.jinja2")).read_text()
    )
    restore_template = jinja2.Template(
        (root / Path("jinja_templates/restore-job.yml.jinja2")).read_text()
    )

    return (
        backup_template,
        restore_template,
        backup_job_dir,
        restore_job_dir,
        {
            "backup_host": backup_host,
            "backup_host_path": backup_host_path,
            "backup_identifier": args.identifier,
            "ttl": args.ttl,
        },
    )


def gen(args):
    (
        backup_template,
        restore_template,
        backup_job_dir,
        restore_job_dir,
        kwargs,
    ) = initialize_gen(args)
    os.makedirs("jobs", exist_ok=True)
    print(f"Generating {len(netids)} jobs")
    for netid in netids:
        kwargs["netid"] = netid
        (backup_job_dir / f"{netid}.yml").write_text(backup_template.render(**kwargs))
        (restore_job_dir / f"{netid}.yml").write_text(restore_template.render(**kwargs))
    print(f"done")


def backup_restore(args, label: str):
    print(f"{now=}")
    latest_dir = jobs_dir / args.identifier
    job_dir = latest_dir / label

    f = args.filter
    f = f.split(",") if f is not None else f

    job_files = []
    for job_file in job_dir.iterdir():
        if not job_file.is_file():
            print(f"Found unknown file {job_file=}, skipping")
            continue
        netid = parse("{}.yml", str(job_file.name))[0]
        if f is not None:
            if netid in f:
                job_files.append(job_file)
        else:
            job_files.append(job_file)

    if not args.yes:
        if f is not None:
            print(f"Included jobs:")
            print(json.dumps([str(job_file.name) for job_file in job_files], indent=2))
        else:
            print(f"{len(job_files)=}")
        y = input("Continue? [N/y] ")
        if not y.lower().startswith("y"):
            print("exiting")
            exit(1)

    print(f"Using latest:")
    print(f"  {latest_dir=}")
    print(f"Starting jobs")
    total = len(job_files)
    for index, job_file in enumerate(job_files):
        print(f'{index} / {total}')
        cmd = f"kubectl apply -f {str(job_file)} --wait=false 1> /dev/null"
        os.system(cmd)
        if (index + 1) % args.jobs == 0:
            time.sleep(args.wait)


def backup(args):
    return backup_restore(args, "backup")


def restore(args):
    return backup_restore(args, "restore")


def main() -> int | None:
    parser = parse_args()
    args = parser.parse_args()

    if args.func is None:
        parser.print_help()
        exit(1)

    return args.func(args)


if __name__ == "__main__":
    main()
