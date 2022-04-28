from determined.experimental import client
import os
import git
import argparse
import yaml


def create_exp(configfile, datapath):
    client.login(
        master=os.getenv("DETERMINED_MASTER"),
        user=os.getenv("DETERMINED_USER"),
        password=os.getenv("DETERMINED_PASSWORD"),
    )
    exp = client.create_experiment(configfile, datapath)
    return exp


def clone_data(repo_url, ref, dir):
    repo = git.Repo.clone_from(repo_url, dir)
    repo.git.checkout(ref)


def read_config(conf_file):
    config = {}
    with open(conf_file, "r") as stream:
        try:
            config = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
    return config


def main():
    parser = argparse.ArgumentParser(
        description="Determined AI Experiment Runner"
    )
    parser.add_argument(
        "--config-file",
        type=str,
        default="config.yaml",
        help="The Configuration file",
    )
    parser.add_argument(
        "--git-url",
        type=str,
        help="Git URL for Accessing the Code",
    )
    parser.add_argument(
        "--git-ref",
        type=str,
        help="Git Commit/Tag/Branch to use",
    )
    parser.add_argument(
        "--sub-dir",
        type=str,
        help="Subfolder to experiment files (optional)",
    )
    args = parser.parse_args()
    local_repo = os.path.join(os.getcwd(), "test")
    clone_data(args.git_url, args.git_ref, local_repo)
    conf_file = os.path.join(local_repo, args.config_file)
    if args.sub_dir:
        workdir = local_repo + "/" + args.sub_dir
    else:
        workdir = local_repo
    config = read_config(conf_file)
    print(config)
    config["data"]["pachyderm"]["pipeline_name"] = (
        os.getenv("PPS_PIPELINE_NAME", "None"),
    )
    config["data"]["pachyderm"]["branch"] = os.getenv("PACH_JOB_ID", "None")
    exp = create_exp(config, workdir)

    exp.wait(10)


if __name__ == "__main__":
    main()
