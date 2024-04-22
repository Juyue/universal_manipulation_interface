if __name__ == "__main__":
    import sys
    import os
    import pathlib

    ROOT_DIR = str(pathlib.Path(__file__).parent.parent.parent.parent)
    sys.path.append(ROOT_DIR)
    os.chdir(ROOT_DIR)

from omegaconf import OmegaConf
import hydra
from diffusion_policy.dataset.base_dataset import BaseImageDataset, BaseDataset

config_path = "/home/ubuntu/universal_manipulation_interface/diffusion_policy/config/"
main_cfg_name = "train_diffusion_unet_timm_umi_workspace.yaml"

OmegaConf.register_new_resolver("eval", eval, replace=True)

@hydra.main(config_path=config_path, config_name=main_cfg_name)
def main(cfg):
    import debugpy
    port = 5700
    debugpy.listen(address=("localhost", port))
    print(f"Now is a good time to attach your debugger: Run: Python: Attach {port}")
    debugpy.wait_for_client()

    dataset: BaseImageDataset
    dataset = hydra.utils.instantiate(cfg.task.dataset)

    sampler = dataset.sampler
    replay_buffer = sampler.replay_buffer
    replay_buffer
    n_episode = len(sampler)
    # n_videos = len


    import pdb; pdb.set_trace()

main()

""" 
python sandbox/jchen/tutorial/04_visualize_data.py task.dataset_path=$HOME/example_demo_session/dataset.zarr.zip 
"""