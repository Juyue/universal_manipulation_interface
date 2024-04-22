#!/usr/bin/env python3

""" 
docker run -it \
-p 5901:5901 \
--volume /home/ubuntu/datasets/umi/demo_sessions/20240417_writingc/demos/demo_C3441327581725_2024.04.17_10.28.57.066033:/data \
--volume /home/ubuntu/datasets/umi/demo_sessions/20240417_writingc/demos/mapping:/map \
--entrypoint /bin/bash \
--name slam
chicheng/orb_slam3:latest

"""
""" 
./scripts_slam_pipeline/run.py --input_dir /home/ubuntu/datasets/umi/demo_sessions/20240417_writingc --vnc
"""

import argparse
import sys
import os
import subprocess
import glob

DOCKER_IMAGE = "chicheng/orb_slam3:latest"
DOCKER_NAME = "slam"

def warning(s):
    """Display string in bright red, prefixed by WARNING:."""
    return "\033[01m\033[91mWARNING: " + s + "\033[00m"

def call_with_echo(args) -> int:
    print(" ".join(args))
    return subprocess.check_call(args)


def get_docker_mount_opts(args):
    pass

def find_existing(docker_name):
    command = ["docker", "container", "ls", "-a", "-f", "name=" + docker_name, "-q"]
    try:
        return subprocess.check_output(command).decode().strip()
    except subprocess.CalledProcessError:
        return None

def get_video_dir(input_dir):
    # Step 0: Print all demos in the input_directory
    mp4_files = list(glob.glob(os.path.join(input_dir, "demos/*")))
    print(f"Found {len(mp4_files)} video dirs") 
    for i, mp4_file in enumerate(mp4_files):
        print(f"{i:10}: {mp4_file}")
    
    # Step 1: Ask the user to choose one demo
    while True:
        choice = input("Enter the number of the file you want to choose (to debug its slam): ")
        try:
            choice = int(choice)
            if 0 <= choice <= len(mp4_files)-1:
                chosen_file = mp4_files[choice]
                break
            else:
                print(f"Invalid choice. Please enter a valid number from 0 to {len(mp4_files)-1}.")
        except ValueError:
            print("Invalid input. Please enter a valid number.")
    print(f"Chosen file: {chosen_file}")
    return chosen_file

def relaunch_or_attach(args, docker_name):
    """Check if the container already exists, and if so, stop&rm it if user wants to relaunch it, otherwise, attach."""
    existing = find_existing(docker_name)
    if existing:
        if args.relaunch:
            # remove the existing container 
            print("You have chosen to relaunch the container, stopping and removing the existing container...")
            call_with_echo(["docker", "stop", docker_name])
            call_with_echo(["docker", "rm", docker_name])
        else:
            print(
                warning(
                    "Found existing container at {existing}, ignoring any invocation args you may have given...".format(
                        existing=existing
                    )
                )
            )
            exit(call_with_echo(["docker", "exec", "-it", existing, "/bin/bash"]))

def get_entrypoint_opts(args):
    opts = []
    if args.vnc:
        opts.append("--vnc")
    if args.vnc_port is not None:
        opts.extend(["--vnc_port", str(args.vnc_port)])
    return opts

def main(args):
    docker_name = DOCKER_NAME 
    docker_image = DOCKER_IMAGE

    relaunch_or_attach(args, docker_name)

    # volume
    video_dir = get_video_dir(args.input_dir)
    data_volume_opts = ["--volume", f"{video_dir}:/data"]
    mapping_volume_opts = ["--volume", f"{args.input_dir}/demos/mapping:/map"]
    code_volume_opts = ["--volume", f"{os.path.dirname(os.path.realpath(__file__))}:/code"]
    # vnc port
    vnc_port_opts = ["-p", f"{args.vnc_port}:{args.vnc_port}"]

    command = ["docker", "run"]
    command += data_volume_opts + mapping_volume_opts + vnc_port_opts + code_volume_opts
    # command += ["-w", "/root"]
    command += [
        "-it",
        # "--entrypoint",
        # "/code/docker_entrypoint.py",
        "--name",
        docker_name,
        docker_image,
    ]
    # command += get_entrypoint_opts(args)

    exit(call_with_echo(command))


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", type=str, default="/home/ubuntu/datasets/umi/demo_sessions/20240417_writingc")
    parser.add_argument("--vnc", action="store_true")
    parser.add_argument("--vnc-port", type=str, default="5901")
    parser.add_argument("--relaunch", action="store_true")
    
    args = sys.argv[1:]
    return parser.parse_args(args)
    
if __name__ == "__main__":
    # import debugpy
    # port = 5700
    # debugpy.listen(address=("localhost", port))
    # print(f"Now is a good time to attach your debugger: Run: Python: Attach {port}")
    # debugpy.wait_for_client()

    main(parse_args())