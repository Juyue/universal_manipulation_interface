#!/usr/bin/env python3

import argparse
import atexit
import os
import shlex
import subprocess

VNC_PASSWORD = "3284"
VNC_DISPLAY = ":99"

def launch_vnc(args):
    print("Starting VNC server...")
    subprocess.check_call(["apt", "update"])
    subprocess.check_call(
        ["apt", "install", "-y", "xvfb", "x11vnc", "vim"]
    )
    # resolution = "2560x1920x24" if args.vnc_high_resolution else "1024x768x24"
    # resolution = "768x1024x24" # 768 x 768 x 16
    # resolution = "2048x768x24" # 2048 x 9216 (2:9) 
    # resolution = "4096x768x24" # 4096 x 9216 (2:9) 
    # resolution = "1280x960x24"

    resolution = "1024x768x24" # 768 x 768 x 9; 1024 x 8736
    xvfb_p = subprocess.Popen(
        [
            "Xvfb",
            VNC_DISPLAY,
            "-screen",
            "0",
            resolution,
            "-ac",
            "+extension",
            "GLX",
            "+render",
            "+extension",
            "RANDR",
            "-noreset",
        ],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
    )

    passwd_file = os.path.expanduser("~/.x11vnc/passwd")

    os.makedirs(os.path.dirname(passwd_file), exist_ok=True)

    subprocess.check_call(
        ["x11vnc", "-storepasswd", VNC_PASSWORD, passwd_file], stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL
    )

    os.environ["DISPLAY"] = VNC_DISPLAY

    with open("/root/.bashrc", "a") as f:
        f.writelines([f"export DISPLAY={VNC_DISPLAY}\n"])

    x11vnc_p = subprocess.Popen(
        [
            "x11vnc",
            "-q",
            "-nopw",
            "-ncache",
            "10",
            "-forever",
            "-rfbauth",
            passwd_file,
            "-display",
            VNC_DISPLAY,
            "-rfbport",
            str(args.vnc_port),
            # "-geometry",
            # "1024x768"
        ],
        env=dict(os.environ, DISPLAY=f"{VNC_DISPLAY}.0"),
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
    )

    print(f"VNC launched! Connect via HOST:{args.vnc_port} and password is {VNC_PASSWORD}")

    atexit.register(xvfb_p.kill)
    atexit.register(x11vnc_p.kill)

def main(args):
    if args.vnc:
        launch_vnc(args)

    command = args.command
    print(f"Running command: {command}")
    exit(subprocess.check_call(shlex.split(args.command)))


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--vnc", action="store_true")
    parser.add_argument("--vnc-port", type=int, default=5901)
    parser.add_argument("-c", "--command", type=str, default="/bin/bash")
    return parser.parse_args()


if __name__ == "__main__":
    main(parse_args())